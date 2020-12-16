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
import requests
import logging as log
import json


class DeploymentInfo(dict):
    """Class which holds all the information related to a deployment.

    The information is extracted from the json response from the server, and is
    thus afterwards considered safe to access all the keys in the data.

    """

    def __init__(self, *args, **kw):
        super(DeploymentInfo, self).__init__(self, *args, **kw)
        self.__dict__ = self

    def verify(self, deployment_json):
        try:
            deployment_json["id"]
            deployment_json["artifact"]
            deployment_json["artifact"]["artifact_name"]
            deployment_json["artifact"]["source"]
            deployment_json["artifact"]["source"]["uri"]
            deployment_json["artifact"]["source"]["expire"]
            deployment_json["device_types_compatible"]
        except KeyError as ke:
            log.error(
                f"The key '{ke}' is missing from the deployments/next response JSON"
            )
            raise ke
        except Exception as e:
            log.error(
                f"Unknown exception {e} trying to parse the deployments/next JSOn response"
            )
            raise e


def request(server_url, JWT, device_type=None, artifact_name=None):
    if not device_type:
        log.error("No device_type found. Update cannot proceed")
        return
    if not artifact_name:
        log.error("No artifact_Name found. Update cannot proceed")
        return
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + JWT}
    r = requests.get(
        server_url + "/api/devices/v1/deployments/device/deployments/next",
        headers=headers,
        params={"artifact_name": artifact_name, "device_type": device_type},
    )
    log.debug(f"update: request: {r}")
    log.error(f"Error {r.reason}. code: {r.status_code}")
    if r.status_code == 200:
        log.info(f"New update available: {r.text}")
        update_json = r.json()
        try:
            dd = DeploymentInfo().verify(update_json)
            return dd
        except Exception as e:
            return None
    elif r.status_code == 204:
        log.info("No new update available}")
    else:
        log.debug(f"{r.json()}")
        log.error("Error while fetching update")


def download(deployment_data, artifact_path="tests/data/artifact.mender"):
    """Download the update artifact to the artifact_path"""
    update_url = deployment_data.artifact.source.uri
    response = requests.get(update_url, stream=True)
    with open(artifact_path, "wb") as fh:
        for data in response.iter_content():
            fh.write(data)
