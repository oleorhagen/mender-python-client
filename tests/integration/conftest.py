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

from os import path
import sys

sys.path += [path.join(path.dirname(__file__), "mender_integration")]

def pytest_exception_interact(node, call, report):
    if report.failed:
        logger.error(
            "Test %s failed with exception:\n%s" % (node.name, call.excinfo.getrepr())
        )

        # Hack-ish way to inspect the fixtures in use by the node to find a MenderDevice/MenderDeviceGroup
        device = None
        env_candidates = [
            val
            for val in node.funcargs.values()
            if isinstance(val, BaseContainerManagerNamespace)
        ]
        if len(env_candidates) == 1:
            env = env_candidates[0]
            dev_candidates = [
                getattr(env, attr)
                for attr in dir(env)
                if isinstance(getattr(env, attr), MenderDevice)
                or isinstance(getattr(env, attr), MenderDeviceGroup)
            ]
            if len(dev_candidates) == 1:
                device = dev_candidates[0]

        # If we have a device (or group) try to print deployment and systemd logs
        if device == None:
            logger.info("Could not find device in test environment, no printing logs")
        else:
            try:
                logger.info("Printing client deployment log, if possible:")
                output = device.run("cat /data/mender/deployment*.log || true", wait=60)
                logger.info(output)
            except:
                logger.info("Not able to print client deployment log")

            for service in ["mender-python-client"]:
                try:
                    logger.info("Printing %s systemd log, if possible:" % service)
                    output = device.run("journalctl -u %s || true" % service, wait=60,)
                    logger.info(output)
                except:
                    logger.info("Not able to print %s systemd log" % service)

        # Note that this is not very fine grained, but running docker-compose -p XXXX ps seems
        # to ignore the filter
        output = subprocess.check_output(
            'docker ps --filter "status=exited"', shell=True
        ).decode()
        logger.info("Containers that exited during the test:")
        for line in output.split("\n"):
            logger.info(line)
