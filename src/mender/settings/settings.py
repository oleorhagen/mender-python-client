import os.path


class Path(object):
    def __init__(self):
        self.conf = "/etc/mender"
        self.data_store = "/var/lib/mender"
        self.data_dir = "/usr/share/mender"
        self.key_filename = "mender-agent.pem"

        self.local_conf = os.path.join(self.conf, "mender.conf")
        self.global_conf = os.path.join(self.data_store, "mender.conf")

        self.identity_scripts = os.path.join(
            self.data_dir, "identity", "mender-device-identity"
        )
        self.inventory_scripts = os.path.join(self.data_dir, "inventory")
        self.key = os.path.join(self.data_store, self.key_filename)
        self.key_path = self.data_store

        self.artifact_info = os.path.join(self.conf, "artifact_info")
        self.device_type = os.path.join(self.data_store, "device_type")
