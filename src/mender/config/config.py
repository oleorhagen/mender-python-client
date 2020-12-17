# Copyright 2020 Northern.tech AS
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


class NoConfigurationFileError(Exception):
    pass


class Config(object):
    """A dictionary for storing Mender configuration values"""

    def __init__(self, global_conf={}, local_conf={}):
        vals = {**global_conf, **local_conf}
        self.ServerURL = ""
        self.RootfsPartA = ""
        self.RootfsPartB = ""
        self.TenantToken = ""
        self.InventoryPollIntervalSeconds = ""
        self.UpdatePollIntervalSeconds = ""
        self.RetryPollIntervalSeconds = ""
        for k, v in vals:
            if k == "ServerURL":
                self.ServerURL = v
            elif k == "RootfsPartA":
                self.RootfsPartA = v
            elif k == "RootfsPartB":
                self.RootfsPartB = v
            elif k == "TenantToken":
                self.TenantToken = v
            elif k == "InventoryPollIntervalSeconds":
                self.InventoryPollIntervalSeconds = v
            elif k == "UpdatePollIntervalSeconds":
                self.UpdatePollIntervalSeconds = v
            elif k == "RetryPollIntervalSeconds":
                self.RetryPollIntervalSeconds = v
            else:
                log.error(f"The key {k} is not recognized by the Python client")


def load(local_path="", global_path=""):
    """Read and return the config from the local and global config files"""
    log.info("Loading the configuration files...")
    global_conf = local_conf = None
    try:
        with open(global_path, "r") as fh:
            global_conf = json.load(fh)
    except FileNotFoundError:
        log.debug(f"Global configuration file not found")
    except Exception as e:
        log.error(f"Failed to load the global configuration file with error {e}")
    try:
        with open(local_path, "r") as fh:
            local_conf = json.load(fh)
    except FileNotFoundError as e:
        log.debug(f"Local configuration file not found: {e}")
    except Exception as e:
        log.error(f"Failed to load the local configuration file with error {e}")
    if not global_conf and not local_conf:
        raise NoConfigurationFileError
    return Config(global_conf=global_conf or {}, local_conf=local_conf or {})
