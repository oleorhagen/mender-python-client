import logging as log
import logging.handlers
import os
import os.path


class DeploymentLogHandler(logging.handlers.RotatingFileHandler):
    def __init__(self):
        self.enabled = False
        self.log_dir = "tests/data/"
        super().__init__(
            filename=os.path.join(self.log_dir, "deployment-uninitialized.log")
        )

    def handle(self, record):
        if self.enabled:
            super().handle(record)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
        self.doRollover()

    def addSubUpdaterLogs(self, log_file):
        try:
            with open(log_file) as fh:
                log_data = fh.read()
                log_string = log_data.decode()
                log.info(f"Sub-updater-logs follows:\n{log_string}")
        except FileNotFoundError:
            log.error(f"The log_file: {log_file} was not found. No logs from the sub-updater will be reported.")
        except Exception as e:
            log.error(f"Unexpected exception {e}")

