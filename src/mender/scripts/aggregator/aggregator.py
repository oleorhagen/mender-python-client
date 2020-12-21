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
import subprocess


class ScriptKeyValueAggregator:
    """Handles the parsing of the output from any Mender identity of inventory scripts.

    These scripts support key=value pairs, with one output per line maximum.
    Multiple lines with a matching key are aggregated into an array."""

    def __init__(self, script_path="unset"):
        self.script_path = script_path
        self.vals = {}

    def run(self):
        output = subprocess.run(self.script_path, stdout=subprocess.PIPE, timeout=100)
        data = output.stdout.decode()
        return self.parse(data)

    def collect(self, unique_keys=False):
        with open(self.script_path) as fh:
            data = fh.read()
            return self.parse(data, unique_keys)

    def parse(self, data, unique_keys=False):
        for line in data.split("\n"):
            if line == "":
                continue
            arr = line.strip().split("=")
            if len(arr) < 2:
                log.debug(f"Skipping line without output")
                continue
            if len(arr) > 2:
                log.error(
                    f"script: {self.script_path} output line: {line} is improperly formatted with more than one '=' sign. Skipping."
                )
                continue
            key, val = arr[0], arr[1]
            l = self.vals.get(key, [])
            if unique_keys:
                l = [val]
            elif val not in l:
                l.append(val)
            self.vals[key] = l
        return self.vals
