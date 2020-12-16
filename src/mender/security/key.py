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

import mender.security.rsa as rsa


def generate_key():
    log.debug("generate_key: ")
    private_key = rsa.generate_key()
    return private_key


def public_key(private_key):
    log.debug("key: public_key()")
    return rsa.public_key(private_key)


def store_key(private_key, path="/path/to/rsa_keys"):
    log.info(f"Storing key to: {path}")
    rsa.store_key(private_key, path)


def load_key(path="/path/to/rsa_keys"):
    log.info(f"Loading key from: {path}")
    return rsa.load_key(path)


def sign(private_key, data):
    log.debug("key: Signing the message body")
    return rsa.sign(private_key, data)
