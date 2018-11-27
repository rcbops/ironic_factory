#!/bin/bash
set -x

codename="$(facter lsbdistcodename)"
os="$(facter operatingsystem)"
os_family="$(facter osfamily)"
os_release="$(facter operatingsystemrelease)"

if [ "$PACKER_BUILDER_TYPE" != "virtualbox-iso" ]; then
    exit 0
fi

if [[ $os_family = "Debian" || $os = "Debian" ]]; then
    if [[ $os = "Ubuntu" ]]; then
        set -e
        sudo apt-get install -y virtualbox-guest-utils
        sudo rm -rf /home/vagrant/VBoxGuestAdditions*.iso
        
        elif [[ $os = "LinuxMint" ]]; then
        sudo apt-get install -y virtualbox-guest-utils
        sudo rm -rf /home/vagrant/VBoxGuestAdditions*.iso
        elif [[ $os = "Debian" ]]; then
        if [[ $os_release > 7.11 ]]; then
            sudo mkdir -p /mnt/virtualbox
            sudo mount -o loop /home/vagrant/VBoxGuestAdditions*.iso /mnt/virtualbox
            sudo sh /mnt/virtualbox/VBoxLinuxAdditions.run
            sudo umount /mnt/virtualbox
            sudo rm -rf /home/vagrant/VBoxGuestAdditions*.iso
        fi
    fi
    
    elif [[ $os_family = "RedHat" ]]; then
    if [[ $os = "Fedora" ]]; then
        sudo dnf -y install gcc kernel-devel kernel-headers dkms make bzip2 perl && \
        sudo dnf -y groupinstall "Development Tools"
        if [[ $os_release > 28 ]]; then
            sudo dnf -y remove virtualbox-guest-additions
        fi
    else
        set -e
        sudo yum -y install gcc kernel-devel kernel-headers dkms make bzip2 perl && \
        sudo yum -y groupinstall "Development Tools"
    fi
    sudo mkdir -p /mnt/virtualbox
    sudo mount -o loop /home/vagrant/VBoxGuest*.iso /mnt/virtualbox
    sudo sh /mnt/virtualbox/VBoxLinuxAdditions.run
    sudo umount /mnt/virtualbox
    sudo rm -rf /home/vagrant/VBoxGuest*.iso
    
    elif [[ $os_family = "Suse" || $os = *openSUSE* ]]; then
    sudo zypper --non-interactive install gcc kernel-devel \
    make bzip2 perl
    sudo mkdir -p /mnt/virtualbox
    sudo mount -o loop /root/VBoxGuest*.iso /mnt/virtualbox
    sudo sh /mnt/virtualbox/VBoxLinuxAdditions.run
    sudo umount /mnt/virtualbox
    sudo rm -rf /root/VBoxGuest*.iso
    
    elif [[ $os_family = "Linux" ]]; then
    if [[ $os = "Alpine" ]]; then
        if [[ $os_release = 3.7.1 ]]; then
            echo http://dl-cdn.alpinelinux.org/alpine/v3.7/community >> /etc/apk/repositories
        fi
        set -e
        apk add -U virtualbox-guest-additions virtualbox-guest-modules-virthardened || true
        echo vboxsf >> /etc/modules
        apk add nfs-utils || true
        rc-update add rpc.statd
    fi
    elif [[ $os_family = "Archlinux" ]]; then
    sudo /usr/bin/pacman -S --noconfirm linux-headers virtualbox-guest-utils virtualbox-guest-modules-arch nfs-utils
    sudo bash -c "echo -e 'vboxguest\nvboxsf\nvboxvideo' > /etc/modules-load.d/virtualbox.conf"
    sudo /usr/bin/systemctl enable vboxservice.service
    sudo /usr/bin/systemctl enable rpcbind.service
    sudo /usr/bin/usermod --append --groups vagrant,vboxsf vagrant
fi

if [ -f /home/vagrant/VBoxGuestAdditions*.iso ]; then
    sudo rm -rf /home/vagrant/VBoxGuestAdditions*.iso
    elif [ -f /root/VBoxGuestAdditions*.iso ]; then
    sudo rm -rf /root/VBoxGuestAdditions*.iso
fi