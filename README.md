[![Build Status](https://gitlab.com/Northern.tech/Mender/mender-python-client/badges/master/pipeline.svg)](https://gitlab.com/Northern.tech/Mender/mender-python-client/pipelines)
[![Coverage Status](https://coveralls.io/repos/github/mendersoftware/mender-python-client/badge.svg?branch=master)](https://coveralls.io/github/mendersoftware/mender-python-client?branch=master)

Mender Python Client: A Python implementation of the Mender client
==============================================

![Mender logo](mender_logo.png)

## Overview

The _Mender Python Client_ is an API client, which is responsible for
interacting with the Mender server, and downloading the Artifact for a
deployment to a specified location on the device, and then exit until a local
sub-updater on the device has handled the update, reported the update status
(failed, or success), and re-started the _Python client_ thereafter.

## Workings

The _client_ in daemon mode will idle checking for updates at a configureable
interval, and download the Artifact for the deployment to a given location on
the device. Then control is passed over to the _sub-updater_ through calling the
script `/usr/share/mender/install <path-to-downloaded-artifact>`.

It is then the sub-updaters responsibility to unpack the Artifact, and install
it to the passive partition, reboot the device, commit the update (or roll back
if so is required). Then report the update status through calling
`mender-python-client report <--success|--failure>`, and then remove the
lock-file, to have the _Python Client_ start looking for updates again.

After a succesful update, the _sub-updater_ is responsible for updating the
_artifact_info_ file located in `/etc/mender/artifact_info`, to reflect the name
of the Artifact just installed on the device. This is important, as this is the
version which is used when polling the server for further updates. The
`artifact_info` file has to have the structure:

```
artifact_name=<name-of-current-installed-artifact>
```

The `device_type` is taken from `<datadir>/device_type` file, and has to have the structure:

```
device_type=<some-device-type>
```

## Configuration

The _Client_ respects this subset of configuration variables supported by the original _Mender Client_:

* RootfsPartA
* RootfsPartB
* ServerURL
* ServerCertificate
* TenantToken
* InventoryPollIntervalSeconds
* UpdatePollIntervalSeconds
* RetryPollIntervalSeconds

## Contributing

We welcome and ask for your contribution. If you would like to contribute to the
Mender project, please read our guide on how to best get started [contributing
code or
documentation](https://github.com/mendersoftware/mender/blob/master/CONTRIBUTING.md).

## License

Mender is licensed under the Apache License, Version 2.0. See
[LICENSE](https://github.com/mendersoftware/mender-python-client/blob/master/LICENSE) for
the full license text.

## Security disclosure

We take security very seriously. If you come across any issue regarding
security, please disclose the information by sending an email to
[security@mender.io](security@mender.io). Please do not create a new public
issue. We thank you in advance for your cooperation.

## Connect with us

* Join the [Mender Hub discussion forum](https://hub.mender.io)
* Follow us on [Twitter](https://twitter.com/mender_io). Please
  feel free to tweet us questions.
* Fork us on [Github](https://github.com/mendersoftware)
* Create an issue in the [bugtracker](https://tracker.mender.io/projects/MEN)
* Email us at [contact@mender.io](mailto:contact@mender.io)
* Connect to the [#mender IRC channel on Freenode](http://webchat.freenode.net/?channels=mender)


## Authors

[List](https://github.com/mendersoftware/mender-python-client/graphs/contributors)!

The [Mender](https://mender.io) project is sponsored by [Northern.tech
AS](https://northern.tech).
