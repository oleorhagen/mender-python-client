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
import requests


def request(server_url: str, JWT: str, inventory_data: dict) -> None:
    if not server_url:
        log.error("ServerURL not provided, unable to upload the inventory")
        return None
    if not JWT:
        log.error("No JWT not provided, unable to upload the inventory")
        return None
    if not inventory_data:
        log.info("No inventory_data provided")
        return None
    log.debug(
        f"inventory request: server_url: {server_url}\nJWT: {JWT}\ninventory_data: {inventory_data}"
    )
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + JWT}
    log.debug(f"inventory headers: {headers}")
    raw_data = json.dumps([{"name": k, "value": v} for k, v in inventory_data.items()])
    try:
        r = requests.put(
            server_url + "/api/devices/v1/inventory/device/attributes",
            headers=headers,
            data=raw_data,
        )
    except (
        requests.RequestException,
        requests.ConnectionError,
        requests.URLRequired,
        requests.TooManyRedirects,
        requests.Timeout,
    ) as e:
        log.error(f"Failed to upload the inventory: {e}")
        return None
    log.debug(f"inventory response: {r}")
    log.error(f"Error {r.reason}. code: {r.status_code}")
    if r.status_code != 200:
        log.error(f"{r.json()}")
    return None
