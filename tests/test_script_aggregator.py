import tempfile
import pytest
import os
import stat


import mender.scripts.aggregator.aggregator as aggregator
import mender.scripts.aggregator.inventory as inventory
import mender.scripts.artifactinfo as artifactinfo
import mender.scripts.devicetype as devicetype


class TestScriptKeyValueAggregator:
    TEST_DATA = [
        (
            "key=value\nkey2=value2\nkey=value2",
            {"key": ["value", "value2"], "key2": ["value2"]},
        ),
        ("key=value key=value", {}),
        ("key=value\nkey=val2\nkey=value", {"key": ["value", "val2"]}),
        ("key=val\tkey=val2", {}),
    ]

    @pytest.mark.parametrize("data, expected", TEST_DATA)
    def test_parse_key_values(self, data, expected):
        vals = aggregator.ScriptKeyValueAggregator().parse(data)
        assert vals == expected


class TestArtifactInfo:

    TEST_DATA = [
        (
            """
            artifact_name=release-0.1
            artifact_group=test
            """,
            {"artifact_name": ["release-0.1"], "artifact_group": ["test"]},
        ),
        (
            """
            artifact_name=release-0.1
            artifact_name=release-1.0
            """,
            {"artifact_name": ["release-1.0"]},
        ),
    ]

    @pytest.fixture
    def file_create_fixture(self, tmpdir):
        d = tmpdir.mkdir("aggregator")

        def create_script(data):
            f = d.join("script")
            f.write(data)
            os.chmod(f, stat.S_IRWXU | stat.S_IRWXO | stat.S_IRWXG)
            return str(f)

        return create_script

    @pytest.mark.parametrize("data, expected", TEST_DATA)
    def test_get_artifact_info(self, data, expected, file_create_fixture):
        fpath = file_create_fixture(data)
        ainfo = artifactinfo.get(fpath)
        assert ainfo == expected


class TestDeviceType:

    TEST_DATA = [
        (
            """
            device_type=qemux86-64
            """,
            {"device_type": ["qemux86-64"]},
        ),
        (
            """
            device_type=qemux86-64
            device_type=qemux86-65
            """,
            {"device_type": ["qemux86-65"]},
        ),
    ]

    @pytest.fixture
    def file_create_fixture(self, tmpdir):
        d = tmpdir.mkdir("aggregator")

        def create_script(data):
            f = d.join("script")
            f.write(data)
            os.chmod(f, stat.S_IRWXU | stat.S_IRWXO | stat.S_IRWXG)
            return str(f)

        return create_script

    @pytest.mark.parametrize("data, expected", TEST_DATA)
    def test_get_device_type_info(self, data, expected, file_create_fixture):
        fpath = file_create_fixture(data)
        dtype_info = devicetype.get(fpath)
        assert dtype_info == expected

    def test_get_device_type_info_error(self, file_create_fixture):
        """Test that multiple different keys in the device_type file fails."""
        fpath = file_create_fixture("""device_type=foo\nkey=val""")
        dtype_info = devicetype.get(fpath)
        if dtype_info:
            pytest.fail("Multiple different keys in device_type file should fail")


class TestInventory:

    TEST_DATA = [
        (
            """#!/bin/sh
            echo key=val
            echo key2=val
            echo key=val2
            """,
            {"key": ["val", "val2"], "key2": ["val"]},
        )
    ]

    @pytest.fixture
    def file_create_fixture(self, tmpdir):
        d = tmpdir.mkdir("inventoryaggregator")

        def create_script(data):
            f = d.join("script")
            f.write(data)
            os.chmod(f, stat.S_IRWXU | stat.S_IRWXO | stat.S_IRWXG)
            return str(d)

        return create_script

    @pytest.mark.parametrize("data, expected", TEST_DATA)
    def test_inventory_aggregator(self, data, expected, file_create_fixture):
        tpath = file_create_fixture(data)
        assert (
            inventory.aggregate(tpath, device_type_path="", artifact_info_path="")
            == expected
        )
