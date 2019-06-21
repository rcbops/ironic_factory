[![Build Status](https://travis-ci.org/ldx/ansible-packer.svg?branch=master)](https://travis-ci.org/ldx/ansible-packer)

# Ansible-packer

### Introduction

Ansible role for installing [packer](http://packer.io).

### Usage

Role variables
--------------

- `packer_pkg`: Packer package file, this is the archive that will be fetched. Example: `0.7.1_linux_amd64.zip`. Note: the base URL is always `https://dl.bintray.com/mitchellh/packer/`.

- `packer_version_str`: This is the string that is searched in the output of `packer version`. If not found, `packer_pkg` will be fetched and installed. Example: `"Packer v0.7.1"`.

- `packer_plugins`: A dictionary of plugins to be installed. Example:

    packer_plugins:
      packer-builder-lxc:
        name: lxc
        type: builder
        url: https://s3.amazonaws.com/my-s3-bucket/packer-builder-lxc

  Where
  - `name`: the name of the plugin that can be used in a packer template.
  - `type`: either `builder` or `provisioner`.
  - `url`: URL to fetch the binary from.

  A packer configuration file at `/etc/packer.conf` will automatically created that contains any builder or provisioner installed via `packer_plugins`.

- `packer_plugins_force_install`: Whether to force the installation of plugins, even if they exist. Useful for forcing an update. Example: `false`.

### Example playbook

    ---
    - hosts: all
      sudo: yes
    
      vars:
        packer_pkg: 0.7.1_linux_amd64.zip
        packer_version_str: "Packer v0.7.1"
    
      roles:
        - packer
