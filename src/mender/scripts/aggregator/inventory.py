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

import logging as log
import os
import os.path as path
import subprocess

from mender.scripts.aggregator.aggregator import ScriptKeyValueAggregator
import mender.scripts.artifactinfo as artifactinfo
import mender.scripts.devicetype as devicetype


def aggregate(
    script_path="",
    device_type_path="",
    artifact_info_path="",
):
    """Runs all the inventory scripts in 'path', and parses the 'key=value' pairs
    into a data-structure ready for passing it on to the Mender server"""
    log.info("Aggregating inventory data from {script_path}")
    keyvals = {}
    for inventory_script in inventory_scripts(script_path):
        keyvals.update(inventory_script.run())
    dt = devicetype.get(device_type_path)
    log.info(f"Found the device type: {dt}")
    if dt:
        keyvals.update(dt)
    an = artifactinfo.get(artifact_info_path)
    log.info(f"Found the artifact_name: {an}")
    if an:
        keyvals.update(an)
    return keyvals


def inventory_scripts(inventory_dir):
    """Returns all the inventory scripts in a directory.

    An inventory scripts needs to:

    * Be executable
    * Be located in '/usr/share/mender/inventory'
    """
    scripts = []
    for f in os.listdir(inventory_dir):
        fp = path.join(inventory_dir, f)
        if path.isfile(fp) and os.access(fp, os.X_OK):
            scripts.append(ScriptKeyValueAggregator(fp))
    return scripts
