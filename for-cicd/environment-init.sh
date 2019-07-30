#!/bin/bash

SIT_MASTER="172.16.100.10"
SIT_NODES="172.16.100.11,172.16.100.12"

UAT_MASTER="10.100.1.10"
UAT_NODES="10.100.1.11,10.100.1.12"

PROD_MASTER="10.0.1.10"
PROD_NODES="10.0.1.11,10.0.1.12"

usage() {
    cat << EOF
==================================
Usage:
    /bin/bash environment-init.sh [sit|uat|prod]

Please remember to modify the global var settings in the beginning of this script to your real servers.
==================================

EOF
}

k8s_init_master() {
    ansible-playbook -i ${1},  ansible_root/k8s_init_master.yaml -T 600
}

k8s_init_nodes() {
    ansible-playbook -i ${1},  -e "master_ip=${2}" ansible_root/k8s_init_nodes.yaml -T 600
}


#-------------- main-------------
[ -z "$1" ] && usage && exit 1
if [ "$1" == "sit" ]; then
    MASTER=${SIT_MASTER}
    NODES=${SIT_NODES}
elif [ "$1" == "uat" ]; then
    MASTER=${UAT_MASTER}
    NODES=${UAT_NODES}
elif [ "$1" == "prod" ]; then
    MASTER=${PROD_MASTER}
    NODES=${PROD_NODES}
else
    usage && exit 1

k8s_init_master $MASTER
k8s_init_nodes $NODES $MASTER
