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

An [Ansible] role to configure timezone settings

Build Status
------------
[![Build Status](https://travis-ci.org/mrlesmithjr/ansible-timezone.svg?branch=master)](https://travis-ci.org/mrlesmithjr/ansible-timezone)

Requirements
------------

None

Role Variables
--------------

```
---
# defaults file for ansible-timezone

# set your desired default timezone

# timezone: 'EST5EDT'
# timezone: 'America/New_York'
timezone: 'UTC'

timezone_update_hardware_clock: false
```

Dependencies
------------

None

Example Playbook
----------------

```
---
- hosts: all
  become: true
  vars:
  roles:
    - role: ansible-timezone
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

[Ansible]: <https://www.ansible.com>
