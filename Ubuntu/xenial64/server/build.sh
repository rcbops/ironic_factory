#! /usr/bin/env bash
TMPDIR=/virtual_machines/tmp/ packer build -only=qemu -on-error=abort -timestamp-ui -var-file=box_info.json -var-file=template.json ../../ubuntu-server.json
