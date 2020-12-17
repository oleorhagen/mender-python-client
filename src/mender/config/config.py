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


class Config(dict):
    """A dictionary for storing Mender configuration values"""

    def __init__(self, *args, **kw):
        super(Config, self).__init__(self, *args, **kw)
        self.__dict__ = self

    # TODO - handle non-existing keys, or explicitly map to all acceptable
    # values


def load(
    local_path="/etc/mender/mender.conf", global_path="/data/etc/mender/mender.conf"
):
    """Read and return the config from the local and global config files"""
    log.info("Loading the configuration files...")
    global_conf = local_conf = None
    try:
        with open(global_path, "r") as fh:
            global_conf = json.load(fh)
    except FileNotFoundError:
        log.debug(f"Global configuration file not found: {e}")
        pass
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
    if global_conf and local_conf:
        # Merge the two files, giving precedence to the local configuration
        b = {**global_conf, **local_conf}
        c = Config()
        c.update(b)
        return c
    if global_conf:
        c = Config()
        c.update(global_conf)
        return c
    c = Config()
    c.update(local_conf)
    return c
