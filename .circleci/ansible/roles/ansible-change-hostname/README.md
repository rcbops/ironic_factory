<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Role Name](#role-name)
  - [Build Status](#build-status)
  - [Requirements](#requirements)
  - [Role Variables](#role-variables)
  - [Dependencies](#dependencies)
  - [Example Playbook](#example-playbook)
  - [License](#license)
  - [Author Information](#author-information)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Role Name
=========

Changes the hostname on a node to match the inventory hostname.

Build Status
------------

[![Build Status](https://travis-ci.org/mrlesmithjr/ansible-change-hostname.svg?branch=master)](https://travis-ci.org/mrlesmithjr/ansible-change-hostname)

Requirements
------------

None

Role Variables
--------------

```
---
# defaults file for ansible-change-hostname

# Defines if the node should reboot after changing the hostname
change_hostname_reboot: true
```

Dependencies
------------

None

Example Playbook
----------------

```
- hosts: all
  become: true
  vars:
  roles:
    - role: ansible-change-hostname
  tasks:
```

License
-------

BSD

Author Information
------------------

Larry Smith Jr.
- @mrlesmithjr
- http://everythingshouldbevirtual.com
- mrlesmithjr [at] gmail.com
