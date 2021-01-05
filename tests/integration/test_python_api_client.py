import pytest

from mender_integration.tests.common_setup import standard_setup_one_client_bootstrapped
from mender_integration.tests.tests.common_update import update_image


def test_update_successful(standard_setup_one_client_bootstrapped):
    """Test that the Python API client successfully installs a new update with the
original Mender-client as a sub-updater"""
    update_image(
        standard_setup_one_client_bootstrapped.device,
        standard_setup_one_client_bootstrapped.get_virtual_network_host_ip(),
        install_image="core-image-full-cmdline-%s.ext4"
        % "qemux86-64",
    )




# def test_update_error():
#     pass


# def test_deployment_logs():
#     pass


# def test_download_resume():
#     pass
