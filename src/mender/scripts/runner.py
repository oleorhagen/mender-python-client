import subprocess
import logging as log

def run_sub_updater():
    """run_sub_updater runs the /var/lib/mender/install script"""
    log.info("Running the sub-updater script at /var/lib/mender/install")
    # TODO - Hand this process off to pid einz
    try:
        r = subprocess.run("/var/lib/mender/install")
        return True
    except Exception as e:
        log.error(f"Unexpected error running the install script: {e}")
    return False

