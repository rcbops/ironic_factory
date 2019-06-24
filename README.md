# ironic_factory

An image building factor for OpenStack Ironic using Packer

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [ironic_factory](#ironic_factory)
  - [Purpose](#purpose)
  - [Information](#information)
  - [Requirements](#requirements)
    - [Software](#software)
  - [Usage](#usage)
    - [Local builds](#local-builds)
    - [CI builds](#ci-builds)
  - [License](#license)
  - [Author Information](#author-information)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Purpose

This repository contains the definitions to build images of a number of Linux distributions suitable for use with OpenStack Ironic. CircleCI is used to build these images once a month using [Packer](https://www.packer.io/).

## Information

All builds in this repository

All builds are based on the following providers:

- [qemu](https://www.virtualbox.org)
- [vmware_desktop](https://www.vmware.com)

- You can find my collection of builds [here](https://app.vagrantup.com/mrlesmithjr)

> NOTE: All builds are base builds and follow the Vagrant [guidelines](https://www.vagrantup.com/docs/boxes/base.html) of how a Vagrant
> box should be built.

## Requirements

If using CircleCI to automate the build process, you will need to fork this repository and edit `.circleci/config.yml` accordingly. Otherwise, to build locally, the following is required:

### Software

- [Packer](https://www.packer.io)
- KVM/QEMU

## Usage

There are two ways to use this repository:

- Local builds
- CI builds

### Local builds

There are several ways to perform a local build. Most commonly you will need to run an individual build to troubleshoot. This can be done as follows:

```shell
git clone https://github.com/rcbops/ironic_factory
cd ironic_factory
cd Ubuntu/bionic64/server
./build.sh
```

In the above commands, you will need to change the path from `Ubuntu/bionic64/server` to whatever OS and version you are troubleshooting. Optionally, you can add `PACKER_LOG=1` to the build command for more verbose output.

During the build process, Packer starts a VNC server, which can be connected to for troubleshooting. The following output will tell you which port to connect to:

```shell
2019-06-24T10:54:58-05:00:     qemu: The VM will be run headless, without a GUI. If you want to
qemu: view the screen of the VM, connect via VNC without a password to
qemu: vnc://0.0.0.0:5980
```

Additionally, you can run all of the builds at once using the included `utils.py` script as follows:

```shell
python utils.py build_all
```

### CI builds

This repository also contains a configuration for scheduled builds using CircleCI. The configuration can be found at `.circleci/config.yml` and will need to be adjusted for your particular setup.

Within the `.circleci/ansible` folder are jobs to create an OnMetal host on the Rackspace Cloud that CircleCI then uses to perform the builds. Once a build is complete, the image is pushed to Rackspace Cloud Files with the following folder structure:

```shell
... snip ...
├── Ubuntu
│   ├── bionic64
│   │   ├── 2019-06-24
|   │   │   ├── desktop
|   |   |   |    └── ubuntu-bionic64-desktop.qcow2
|   │   │   └── server
|   |   |        └── ubuntu-bionic64-server.qcow2
│   ├── cosmic64
│   │   ├── 2019-06-24
|   │   │   ├── desktop
|   |   |   |    └── ubuntu-cosmic64-desktop.qcow2
|   │   │   └── server
|   |   |        └── ubuntu-cosmic64-server.qcow2
|   ├── ubuntu-bionic64-server.qcow2
|   └── Ubuntu-cosmic64-server.qcow2
... snip ...
```

The files at the root of a given distribution's folder are pointers to the most recent build for that distribution. This is done by setting the `X-Object-Manifest` header for that file.

## License

MIT

## Author Information

Cody Bunch

- [@cody_bunch](https://www.twitter.com/cody_bunch)
- [vBrownBag](https://vbrownbag.com)
- [bunchc@gmail.com](mailto:bunchc@gmail.com)

Larry Smith Jr.

- [@mrlesmithjr](https://www.twitter.com/mrlesmithjr)
- [EverythingShouldBeVirtual](http://everythingshouldbevirtual.com)
- [mrlesmithjr@gmail.com](mailto:mrlesmithjr@gmail.com)
