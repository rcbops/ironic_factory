#! /usr/bin/env bash
TMPDIR=/virtual_machines/tmp/ packer build -var-file=../../../private_vars.json -var-file=box_info.json -var-file=template.json ../../debian-server.json