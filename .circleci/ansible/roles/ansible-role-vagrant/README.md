<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [ansible-role-vagrant](#ansible-role-vagrant)
- [Local installation : (ansible need to be installed)](#local-installation--ansible-need-to-be-installed)
- [Simple Usage :](#simple-usage-)
- [Usage with version specification](#usage-with-version-specification)
- [Specify virtualbox installation (For Debian)](#specify-virtualbox-installation-for-debian)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

ansible-role-vagrant
====================

Install vagrant with Ansible


# Local installation : (ansible need to be installed)
```
git clone https://github.com/jdauphant/ansible-role-vagrant.git
ansible-playbook -i "localhost," --ask-sudo-pass --connection=local installation.yml
```

# Simple Usage :
```
---
 - hosts: all
   roles:
    - vagrant
```

# Usage with version specification
```
---
 - hosts: all
   roles:
    - role: vagrant
      vagrant_version: "1.6.3"
```

# Specify virtualbox installation (For Debian)
```
---
 - hosts: all
   roles:
    - role: vagrant
      vagrant_virtualbox_install: True
      vagrant_virtualbox_ver: "virtualbox-5.1"
