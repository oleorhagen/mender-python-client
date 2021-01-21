# Copyright 2021 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
import logging as log
import os.path
import time

import mender.bootstrap.bootstrap as bootstrap
from mender.client import HTTPUnathorized
from mender.util import timeutil
import mender.client.authorize as authorize
import mender.client.deployments as deployments
import mender.client.inventory as client_inventory
import mender.config.config as config
import mender.scripts.aggregator.identity as identity
import mender.scripts.aggregator.inventory as inventory
import mender.scripts.artifactinfo as artifactinfo
import mender.scripts.devicetype as devicetype
import mender.scripts.runner as installscriptrunner
import mender.settings.settings as settings

from mender.log.log import DeploymentLogHandler


class Context:
    """Class for storing the state-machine context"""

    def __init__(self):
        self.private_key = None


class State:
    def __init__(self):
        pass

    def run(self, context):
        pass


class Init(State):
    def run(self, context, force_bootstrap=False):
        log.debug("InitState: run()")
        context.config = config.Config({}, {})
        try:
            context.config = config.load(
                local_path=settings.PATHS.local_conf,
                global_path=settings.PATHS.global_conf,
            )
            log.info(f"Loaded configuration: {context.config}")
        except config.NoConfigurationFileError:
            log.error(
                "No configuration files found for the device."
                "Most likely, the device will not be functional."
            )
        identity_data = identity.aggregate(path=settings.PATHS.identity_scripts)
        context.identity_data = identity_data
        private_key = bootstrap.now(
            force_bootstrap=force_bootstrap, private_key_path=settings.PATHS.key
        )
        context.private_key = private_key
        context.inventory_timer = timeutil.IsItTime(
            context.config.InventoryPollIntervalSeconds
        )
        context.update_timer = timeutil.IsItTime(
            context.config.UpdatePollIntervalSeconds
        )
        context.retry_timer = timeutil.IsItTime(context.config.RetryPollIntervalSeconds)
        log.debug(f"Init set context to: {context}")
        return context


##########################################


def run():
    while os.path.exists(settings.PATHS.lockfile_path):
        log.info(
            "A deployment is currently in progress, the client will go to sleep for 60 seconds"
        )
        time.sleep(settings.SLEEP_INTERVAL)
    StateMachine().run()


class StateMachine:
    def __init__(self):
        log.info("Initializing the state-machine")
        self.context = Context()
        self.context.authorized = False
        log.info(f"ctx: {self.context}")
        self.unauthorized_machine = UnauthorizedStateMachine()
        self.authorized_machine = AuthorizedStateMachine()
        log.info("Finished setting up the state-machine")

    def run(self, force_bootstrap=False):
        self.context = Init().run(self.context, force_bootstrap)
        log.debug(f"Initialized context: {self.context}")
        deployment_log_handler = [
            handler
            for handler in log.getLogger("").handlers
            if isinstance(handler, DeploymentLogHandler)
        ]
        assert (
            len(deployment_log_handler) == 1
        ), "Something is wrong with the setup of the DeploymentLogHandler"
        self.context.deployment_log_handler = deployment_log_handler[0]
        self.context.deployment_log_handler.disable()
        while True:
            self.unauthorized_machine.run(self.context)
            self.authorized_machine.run(self.context)


#
# Hierarchical - Yes!
#
# i.e., Authorized, and Unauthorized state-machine
#


class Authorize(State):
    def run(self, context):
        if not context.retry_timer.is_it_time():
            return None

        log.info("Authorizing...")
        log.debug(f"Current context: {context}")
        return authorize.request(
            context.config.ServerURL,
            context.config.TenantToken,
            context.identity_data,
            context.private_key,
            context.config.ServerCertificate,
        )


class Idle(State):
    def run(self, context):
        log.info("Idling...")
        timeutil.sleep(context.retry_timer)
        return True


class UnauthorizedStateMachine(StateMachine):
    """Handle Wait, and Authorize attempts"""

    def __init__(self):
        pass

    def run(self, context):
        while True:
            JWT = Authorize().run(context)
            if JWT:
                context.JWT = JWT
                context.authorized = True
                return
            Idle().run(context)


class AuthorizedStateMachine(StateMachine):
    """Handle Inventory update, and update check"""

    def __init__(self):
        self.idle_machine = IdleStateMachine()
        self.update_machine = UpdateStateMachine()

    def run(self, context):
        while context.authorized:
            try:
                self.idle_machine.run(context)  # Idle returns when an update is ready
                UpdateStateMachine().run(
                    context
                )  # Update machine runs when idle detects an update
            except HTTPUnathorized:
                context.authorized = False
                return


# Should transitions always go through the external state-machine, to verify and
# catch de-authorizations (?)
#
# Second layered machine (below Authorized)
#
# Idling - Or, just pushing inventory and identity data and looking for updates


class SyncInventory(State):
    def run(self, context):
        if not context.inventory_timer.is_it_time():
            return

        log.info("Syncing the inventory...")
        inventory_data = inventory.aggregate(
            settings.PATHS.inventory_scripts,
            settings.PATHS.device_type,
            settings.PATHS.artifact_info,
        )
        if inventory_data:
            log.debug(f"aggregated inventory data: {inventory_data}")
            client_inventory.request(
                context.config.ServerURL,
                context.JWT,
                inventory_data,
                context.config.ServerCertificate,
            )
        else:
            log.info("No inventory data found")


class SyncUpdate(State):
    def run(self, context):
        if not context.update_timer.is_it_time():
            return False

        log.info("Checking for updates...")
        device_type = devicetype.get(settings.PATHS.device_type)
        artifact_name = artifactinfo.get(settings.PATHS.artifact_info)
        deployment = deployments.request(
            context.config.ServerURL,
            context.JWT,
            device_type=device_type,
            artifact_name=artifact_name,
            server_certificate=context.config.ServerCertificate,
        )
        if deployment:
            context.deployment = deployment
            context.deployment_log_handler.enable()
            return True
        return False


class IdleStateMachine(AuthorizedStateMachine):
    def __init__(self):
        pass

    def run(self, context):
        while context.authorized:
            SyncInventory().run(context)
            if SyncUpdate().run(context):
                # Update available
                return
            timeutil.sleep(context.update_timer, context.inventory_timer)


#
# Updating - Run the update state-machine
#


class Download(State):
    def run(self, context):
        log.info("Running the Download state...")
        if deployments.download(
            context.deployment,
            artifact_path=os.path.join(
                settings.PATHS.artifact_download, "artifact.mender"
            ),
            server_certificate=context.config.ServerCertificate,
        ):
            if not deployments.report(
                context.config.ServerURL,
                deployments.STATUS_DOWNLOADING,
                context.deployment.ID,
                context.config.ServerCertificate,
                context.JWT,
                deployment_logger=None,
            ):
                log.error(
                    "Failed to report the deployment status 'downloading' to the Mender server"
                )
            return ArtifactInstall()
        return ArtifactFailure()


class ArtifactInstall(State):
    def run(self, context):
        log.info("Running the ArtifactInstall state...")
        if installscriptrunner.run_sub_updater(context.deployment.ID):
            return ArtifactReboot()
        return ArtifactFailure()


class ArtifactReboot(State):
    def run(self, context):
        log.info("Running the ArtifactReboot state...")
        return ArtifactCommit()


class ArtifactCommit(State):
    def run(self, context):
        log.info("Running the ArtifactCommit state...")
        return ArtifactRollback()


class ArtifactRollback(State):
    def run(self, context):
        log.info("Running the ArtifactRollback state...")
        return ArtifactRollbackReboot()


class ArtifactRollbackReboot(State):
    def run(self, context):
        log.info("Running the ArtifactRollbackReboot state...")
        return ArtifactFailure()


class ArtifactFailure(State):
    def run(self, context):
        log.info("Running the ArtifactFailure state...")
        if not deployments.report(
            context.config.ServerURL,
            deployments.STATUS_FAILURE,
            context.deployment.ID,
            context.config.ServerCertificate,
            context.JWT,
            context.deployment_log_handler,
        ):
            log.error(
                "Failed to report the deployment status 'failure' to the Mender server"
            )
        return _UpdateDone()


class _UpdateDone(State):
    def __str__(self):
        return "done"

    def __eq__(self, other):
        return isinstance(other, _UpdateDone)

    def run(self, context):
        assert False


# The update state-machine is the most advanced machine we need
class UpdateStateMachine(AuthorizedStateMachine):
    def __init__(self):
        self.current_state = Download()

    def run(self, context):
        while self.current_state != _UpdateDone():
            self.current_state = self.current_state.run(context)
            time.sleep(1)
