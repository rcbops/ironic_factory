FROM ubuntu:bionic

RUN set -xe \
   &&  echo '#!/bin/sh' > /usr/sbin/policy-rc.d \
   &&  echo 'exit 101' >> /usr/sbin/policy-rc.d \
   &&  chmod +x /usr/sbin/policy-rc.d \
   &&  dpkg-divert --local --rename --add /sbin/initctl \
   &&  cp -a /usr/sbin/policy-rc.d /sbin/initctl \
   &&  sed -i 's/^exit.*/exit 0/' /sbin/initctl \
   &&  echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/docker-apt-speedup \
   &&  echo 'DPkg::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' > /etc/apt/apt.conf.d/docker-clean \
   &&  echo 'APT::Update::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' >> /etc/apt/apt.conf.d/docker-clean \
   &&  echo 'Dir::Cache::pkgcache ""; Dir::Cache::srcpkgcache "";' >> /etc/apt/apt.conf.d/docker-clean \
   &&  echo 'Acquire::Languages "none";' > /etc/apt/apt.conf.d/docker-no-languages \
   &&  echo 'Acquire::GzipIndexes "true"; Acquire::CompressionTypes::Order:: "gz";' > /etc/apt/apt.conf.d/docker-gzip-indexes \
   &&  echo 'Apt::AutoRemove::SuggestsImportant "false";' > /etc/apt/apt.conf.d/docker-autoremove-suggests \
   &&  DEBIAN_FRONTEND=noninteractive apt-get update \
   &&  apt-get install -y git wget vim curl rsync unzip gnupg
RUN rm -rf /var/lib/apt/lists/*
RUN sed -i 's/^#\s*\(deb.*universe\)$/\1/g' /etc/apt/sources.list
RUN mkdir -p /run/systemd \
   &&  echo 'docker' > /run/systemd/container

RUN echo "===> Adding Ansible's PPA..." \
   &&  echo "deb http://ppa.launchpad.net/ansible/ansible/ubuntu bionic main" | tee /etc/apt/sources.list.d/ansible.list \
   &&  echo "deb-src http://ppa.launchpad.net/ansible/ansible/ubuntu bionic main" | tee -a /etc/apt/sources.list.d/ansible.list \
   &&  apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 7BB9C367 \
   &&  DEBIAN_FRONTEND=noninteractive apt-get update \
   &&  echo "===> Installing handy tools (not absolutely required)..." \
   &&  apt-get install -y python-pip \
   &&  pip install --upgrade pywinrm \
   &&  apt-get install -y sshpass openssh-client \
   &&  echo "===> Installing Ansible..." \
   &&  apt-get install -y ansible \
   &&  echo "===> Removing Ansible PPA..." \
   &&  rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/ansible.list \
   &&  echo "===> Adding hosts for convenience..." \
   &&  echo 'localhost' > /etc/ansible/hosts
CMD ["ansible-playbook" "--version"]
RUN pip install --upgrade pip
RUN pip install --upgrade paramiko fabric packet-python python-dateutil
