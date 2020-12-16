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

import mender.security.key as key


def now(force_bootstrap=False, private_key_path="tests/data/keys/"):
    log.info("Bootstrapping the device")
    private_key = None
    if not force_bootstrap:
        private_key = key_already_generated(private_key_path)
    if not private_key:
        log.info("Generating a new RSA key pair..")
        private_key = key.generate_key()
        key.store_key(private_key, private_key_path)
    log.info("Device bootstrapped successfully")
    return private_key


def key_already_generated(private_key_path):
    log.debug("Checking if a key already exists for the device")
    try:
        return key.load_key(private_key_path + "id_rsa")
    except FileNotFoundError:
        return None
    except Exception as e:
        log.error(e)
    return None
