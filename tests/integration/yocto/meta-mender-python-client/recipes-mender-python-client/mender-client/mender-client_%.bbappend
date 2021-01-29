SYSTEMD_AUTO_ENABLE_${PN} = "disable"

FILES_${PN} += "${datadir}/mender/install \
                /data/mender/device_type"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI_append = " file://mender.conf"

do_install_append() {
    install -m 755 -d ${D}/data/mender
    install -m 444 ${B}/device_type ${D}/data/mender/
    ln -s ${bindir}/mender-sub-updater ${D}${datadir}/mender/install

}
