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
import json
import logging as log
import logging.handlers
import os
import os.path
from typing import List

import mender.settings.settings as settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter

    Logs every log message to a json encoded line in the deployment.log file, in
    the format:

    {
    "message": "foobar",
    "timestamp": "UTC-...",
    "level": "LEVEL"
    }

    """

    def format(self, record) -> str:
        level = record.levelname
        message = record.message
        timestamp = self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ")
        return json.dumps({"level": level, "timestamp": timestamp, "message": message})


class DeploymentLogHandler(logging.FileHandler):
    def __init__(self):
        self.enabled = False
        self.log_dir = settings.PATHS.deployment_log
        filename = os.path.join(self.log_dir, "deployment.log")
        self.log_file = filename
        super().__init__(filename=filename)
        super().setFormatter(JSONFormatter())

    def handle(self, record):
        if self.enabled:
            super().handle(record)

    def enable(self):
        self.enabled = True
        filename = os.path.join(self.log_dir, "deployment.log")
        # Reset the log
        with open(filename, "w"):
            pass

    def disable(self):
        self.enabled = False

    def marshal(self) -> List[str]:
        """Marshal the logs to the format required by the deployment endpoint"""
        logs = []
        try:
            for line in open(self.log_file):
                try:
                    data = json.loads(line)
                    logs.append(data)
                except json.JSONDecodeError as e:
                    log.error(f"Failed to marshal json, {e}")
        except FileNotFoundError:
            log.error("The log file was not found at: {self.log_file}")
        return logs


def add_sub_updater_log(log_file):
    try:
        with open(log_file) as fh:
            log_string = fh.read()
            log.info(f"Sub-updater-logs follows:\n{log_string}")
    except FileNotFoundError:
        log_str = (
            "The log_file: %s was not found."
            + "No logs from the sub-updater will be reported."
        )
        log.error(
            log_str, log_file,
        )
