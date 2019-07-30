#!/bin/bash

#------- config vars ----------

STATIC_PORT=8010
STATIC_CODE_DIRECTORY=/home/alan/company-news-static
DYNAMIC_PORT=8080
DYNAMIC_BUILDING_OUTPUT_DIRECTORY=/home/alan/company-news-java/build


#------- functions -----------
usage() {
    cat << EOF
===============================================
Usage:
    /bin/bash dev-environment-init.sh -h/--help    # To see this help message.
    /bin/bash dev-environment-init.sh init         # To do the real work.

Please remember to modify the global var settings in the beginning of this script to your real developing project code directory.
===============================================

EOF
}

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

start_static_container() {
    echo -e "\n===> To start nginx container for static development."
    docker run -d -p ${STATIC_PORT}:80 --name company-news-static -v ${STATIC_CODE_DIRECTORY}:/usr/share/nginx/html nginx:latest
    docker ps | grep 'company-news-static'
    if [ $? -ne 0 ]; then
        echo "ERROR: To start container 'company-news-static' failed. Please contact the administrator."
    else
        echo -e "To start container 'company-news-static' succeeded.\nYou can visit your static app via http://127.0.0.1:${STATIC_PORT}"
    fi
}

start_tomcat_container() {
    echo -e "\n===> To start tomcat container for java development."
    docker run -d -p ${DYNAMIC_PORT}:8080 --name company-news-java -v ${DYNAMIC_BUILDING_OUTPUT_DIRECTORY}:/usr/local/tomcat/webapps tomcat:latest
    docker ps | grep 'company-news-static'
    if [ $? -ne 0 ]; then
        echo "ERROR: To start container 'company-news-java' failed. Please contact the administrator."
    else
        echo -e "To start container 'company-news-java' succeeded.\nYou can visit your java app via http://127.0.0.1:${DYNAMIC_PORT}"
    fi
}


#------------- main -------------

[ -z "$1" ] && usage && exit 1
[ "$1" == "-h" -o "$1" == "--help" ] && usage && exit 0

if [ "$1" == "init" ]; then
    [ ! -d "$STATIC_CODE_DIRECTORY" ] && mkdir -p $STATIC_CODE_DIRECTORY
    [ ! -d "$DYNAMIC_BUILDING_OUTPUT_DIRECTORY" ] && mkdir -p $DYNAMIC_BUILDING_OUTPUT_DIRECTORY
    install_docker
    start_static_container
    start_tomcat_container
else
    usage && exit 1
fi
