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
import logging.handlers
import os
import os.path

import mender.settings.settings as settings


class DeploymentLogHandler(logging.FileHandler):
    def __init__(self):
        self.enabled = False
        self.log_dir = settings.PATHS.deployment_log
        filename = os.path.join(self.log_dir, "deployment.log")
        super().__init__(filename=filename)

    def handle(self, record):
        if self.enabled:
            super().handle(record)

    def enable(self):
        self.enabled = True
        filename = os.path.join(self.log_dir, "deployment.log")
        # Reset the log file
        super().__init__(filename, mode="w")

    def disable(self):
        self.enabled = False


def add_sub_updater_log(log_file):
    try:
        with open(log_file) as fh:
            log_string = fh.read()
            log.info(f"Sub-updater-logs follows:\n{log_string}")
    except FileNotFoundError:
        log.error(
            f"The log_file: {log_file} was not found.\
            No logs from the sub-updater will be reported."
        )
