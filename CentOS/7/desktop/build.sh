#! /usr/bin/env bash
#TMPDIR=/virtual_machines/tmp/ packer build -except=qemu -var-file=../../../private_vars.json -var-file=box_info.json -var-file=template.json ../../centos-desktop.json
TMPDIR=/virtual_machines/tmp/ packer build -only=qemu -var-file=../../../private_vars.json -var-file=box_info.json -var-file=template.json ../../centos-desktop.json