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
from typing import Optional
import requests

from mender.client import HTTPUnathorized


class DeploymentInfo:
    """Class which holds all the information related to a deployment.

    The information is extracted from the json response from the server, and is
    thus afterwards considered safe to access all the keys in the data.

    """

    def __init__(self, deployment_json: dict) -> None:
        try:
            self.ID = deployment_json["id"]
            self.artifact_name = deployment_json["artifact"]["artifact_name"]
            self.artifact_uri = deployment_json["artifact"]["source"]["uri"]
        except KeyError as e:
            log.error(
                f"The key '{e}' is missing from the deployments/next response JSON"
            )


def request(
    server_url: str,
    JWT: str,
    device_type: Optional[dict],
    artifact_name: Optional[dict],
    server_certificate: str,
) -> Optional[DeploymentInfo]:
    if not server_url:
        log.error("ServerURL not provided. Update cannot proceed")
        return None
    if not device_type:
        log.error("No device_type found. Update cannot proceed")
        return None
    if not artifact_name:
        log.error("No artifact_Name found. Update cannot proceed")
        return None
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + JWT}
    parameters = {**device_type, **artifact_name}
    r = requests.get(
        server_url + "/api/devices/v1/deployments/device/deployments/next",
        headers=headers,
        params=parameters,
        verify=server_certificate if server_certificate else True,
    )
    log.debug(f"update: request: {r}")
    log.error(f"Error {r.reason}. code: {r.status_code}")
    deployment_info = None
    if r.status_code == 200:
        log.info(f"New update available: {r.text}")
        update_json = r.json()
        deployment_info = DeploymentInfo(update_json)
    elif r.status_code == 204:
        log.info("No new update available")
    elif r.status_code == 401:
        log.info(f"The client seems to have been unathorized {r}")
        raise HTTPUnathorized()
    else:
        log.debug(f"{r.json()}")
        log.error("Error while fetching update")
    return deployment_info


def download(
    deployment_data: DeploymentInfo, artifact_path: str, server_certificate: str
) -> bool:
    """Download the update artifact to the artifact_path"""
    if not artifact_path:
        log.error("No path provided in which to store the Artifact")
        return False
    update_url = deployment_data.artifact_uri
    log.info(f"Downloading Artifact: {artifact_path}")
    try:
        response = requests.get(
            update_url,
            stream=True,
            verify=server_certificate if server_certificate else True,
        )
        with open(artifact_path, "wb") as fh:
            for data in response.iter_content():
                fh.write(data)
    except (
        requests.RequestException,
        requests.ConnectionError,
        requests.URLRequired,
        requests.TooManyRedirects,
        requests.Timeout,
    ) as e:
        log.error(e)
        return False
    return True
