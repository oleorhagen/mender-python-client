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
import subprocess
import logging as log


def run_sub_updater() -> bool:
    """run_sub_updater runs the /var/lib/mender/install script"""
    log.info("Running the sub-updater script at /var/lib/mender/install")
    # TODO - Hand this process off to pid einz
    try:
        subprocess.run("/var/lib/mender/install")
        return True
    except Exception as e:
        log.error(f"Unexpected error running the install script: {e}")
        return False
