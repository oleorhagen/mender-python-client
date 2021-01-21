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

import pytest

import mender_integration.tests.conftest as cf

cf.machine_name = "qemux86-64"

from mender_integration.tests.common_setup import standard_setup_one_client_bootstrapped
from mender_integration.tests.tests.common_update import (
    update_image,
    update_image_failed,
)


def test_update_successful(standard_setup_one_client_bootstrapped):
    """Test that the Python API client successfully installs a new update

    This is done through running it in an image, with the original mender-client
    installed, using it as the sub-updater agent, and letting it install the
    Artifact through:

    mender install <path-to-artifact>

    In the sub-updater install script.

    """

    update_image(
        standard_setup_one_client_bootstrapped.device,
        standard_setup_one_client_bootstrapped.get_virtual_network_host_ip(),
        install_image="core-image-full-cmdline-%s.ext4" % "qemux86-64",
    )


def test_update_error(standard_setup_one_client_bootstrapped):
    """Test that the client behaves as expected upon failure.

    This means that the deployment log from both the client itself, and the
    sub-updater should be uploaded to the Mender server upon an error.

    However, here we only check for the sub-updater log. The device deployment
    log is tested in:

    test_deployment_logs()

    """

    device = standard_setup_one_client_bootstrapped.device
    update_image_failed(
        standard_setup_one_client_bootstrapped.device,
        standard_setup_one_client_bootstrapped.get_virtual_network_host_ip(),
        install_image="broken_update.ext4",
        expected_log_message="An update was seemingly in progress, and failed",
    )


def test_deployment_logs():
    """Test that the client handles a missing install script

    The install script is supposed to be a symlink to the install script,
    however, if it is missing, the client should report an error, and upload the
    deployment logs.

    """
    device = standard_setup_one_client_bootstrapped.device
    device.run("rm /usr/share/mender/install")
    update_image_failed(
        standard_setup_one_client_bootstrapped.device,
        standard_setup_one_client_bootstrapped.get_virtual_network_host_ip(),
        install_image="broken_update.ext4",
        expected_log_message="Failed to run the install script",
    )


# def test_download_resume():
#     pass
