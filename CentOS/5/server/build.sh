#! /usr/bin/env bash
TMPDIR=/virtual_machines/tmp/ packer build -only=qemu -timestamp-ui -var-file=box_info.json -var-file=template.json ../../centos-server.json
