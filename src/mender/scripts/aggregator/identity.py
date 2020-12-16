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

import os
import logging as log
import subprocess

from mender.scripts.aggregator.aggregator import ScriptKeyValueAggregator


def aggregate(path="/usr/share/mender/identity"):
    """Runs the identity script in 'path', and parses the 'key=value' pairs
    into a data-structure ready for passing it on to the Mender server"""
    log.info("Aggregating the device identity attributes...")
    identity_data = {}
    if os.path.isfile(path) and os.access(path, os.X_OK):
        identity_data = ScriptKeyValueAggregator(path).run()
    log.debug(f"Aggregated identity data: {identity_data}")
    return identity_data
