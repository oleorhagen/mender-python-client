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
import logging as log
from typing import Optional
import os.path
import requests

import mender.settings.settings as settings
import mender.log.log as menderlog
from mender.client import HTTPUnathorized

STATUS_SUCCESS = "success"
STATUS_FAILURE = "failure"
STATUS_DOWNLOADING = "downloading"


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
        log.error(f"Error {r.reason}. code: {r.status_code}")
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
        with requests.get(
            update_url,
            stream=True,
            verify=server_certificate if server_certificate else True,
        ) as response:
            with open(artifact_path, "wb") as fh:
                for data in response.iter_content(
                    chunk_size=1024 * 1024
                ):  # 1MiB at a time
                    if not data:
                        break
                    fh.write(data)
                    fh.flush()
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


def report(
    server_url: str,
    status: str,
    deployment_id: str,
    server_certificate: str,
    JWT: str,
    deployment_logger: Optional[menderlog.DeploymentLogHandler],
) -> bool:
    """Report update :param status to the Mender server"""
    if not status:
        log.error("No status given to report")
        return False
    try:
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + JWT}
        response = requests.put(
            server_url
            + "/api/devices/v1/deployments/device/deployments/"
            + deployment_id
            + "/status",
            headers=headers,
            verify=server_certificate if server_certificate else True,
            json={"status": status},
        )
        if response.status_code != 204:
            log.error(
                f"Failed to upload the deployment status '{status}',\
                error: {response.status_code}: {response.reason}"
            )
            return False
        if status == STATUS_FAILURE:
            menderlog.add_sub_updater_log(
                os.path.join(settings.PATHS.deployment_log, "deployment.log")
            )
            if deployment_logger:
                logdata = deployment_logger.marshal()
            else:
                log.error("No deployment log handler given")
                return True

            response = requests.put(
                server_url
                + "/api/devices/v1/deployments/device/deployments/"
                + deployment_id
                + "/log",
                headers=headers,
                verify=server_certificate if server_certificate else True,
                json={"messages": logdata,},
            )
            if response.status_code != 204:
                log.error(
                    f"Failed to upload the deployment log,\
                    error: {response.status_code}: {response.reason} {response.text}"
                )
                return False
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
