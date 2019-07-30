#!/bin/bash

install_docker() {
    echo -e "\n===> To remove old docker version."
    sudo yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine

    echo -e "\n===> To install docker yum repository."
    sudo yum install -y epel-release yum-utils device-mapper-persistent-data lvm2
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

    echo -e "\n===> To install docker engine."
    sudo yum install -y docker-cd-18.06.3.ce-3.el7 docker-ce-cli containerd.io

    echo -e "\n===> To start the docker daemon."
    systemctl start docker
    systemctl status docker
    [ $? -ne 0 ] && echo "ERROR: To install docker-ce failed. Please install docker-ce and start the docker daemon manually." && exit 1
}

#-------------------- main ------------------
install-docker
