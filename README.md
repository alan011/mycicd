# Home Work Explaination

I wrote some scripts to accomplish the Homework. Describes below are some kind of Usage of these scripts.

Assume that we have 4 environments for the product developing lifecycle:

* DEV: For developers to write code, do developing-self-test.
* SIT: For QA team to d sit-test.
* UAT: For a limited release.
* PROD: A product environment for appitcations to run full public.

Assume that we already have a private gitlab with domain name 'gitlab.example.com', developers can summit their code to gitlab when they finish the developing-self-test.

We also have a docker repository named "docker-repo.example.com" like Harbor or others. And a package storage server to store building output packages(.zip file, .war file).

For the application in this homework, we named the image and stylesheet parts as project 'company-news-static', and the dynamic java parts as project 'company-news-java'.

All linux servers below should have a linux kernel version 3.10+. I test these scrips in CentOS7.2.

Also assume that we have a "central-control-master" server which runs ansible on it to control all other servers in different environments though ssh. This server can login to target servers with RSA certs(without password input):

* central-control-master: 172.16.0.10
* package-storage-server: 172.16.0.11

## Scripts

* dev-environment-init.sh

To initialize a developing environment with docker. Should only be used on 'developing-server'.

* environment-init.sh

To initialize other environments with kubernetes(k8s) though ansible remote control. (Run on central-control-master)
K8s use nginx-ingress to expose the services.
This requires your net work could visit docker repo of kubernetes.io.

* build-and-release.py

A script to run the whole CI/CD, written in python3.6+. (Run on central-control-master)
It does these works:
    - Fetch code from gitlab.
    - Build it to a .zip or .war file
    - decompress the built-output file into a docker image, push the image to a docker repository.
    - With environment tag specified, call kubectl though ansible to set image with the new docker image to do a rolling-update, or apply a pre-written deployment.yaml for the first time to deploy.

* config.py

A config file for script build-and-release.py. It records the servers info in different envs, and app build and deploy informations.
In a real CI/CD environment, we'd better to store these informations into CMDB or an independent CD system.


To see a detailed usage, run these scripts without any arguments.



## Environments and Servers Assumption

#### DEV Environment

* developing-server: local

A linux work station with GUI. A developer can write their code, and run it in docker.
'dev-environtent-init.sh' script will mount a code directory (or a building-out-put directory for java) onto a docker container, so that when modified code, the developer can see the changes immediately.

#### SIT (QA environment)

* servers:
    - 172.16.100.10: k8s master with kubectl.
    - 172.16.100.11,172.16.100.12: k8s nodes to run real applications.

#### UAT (a limited release environtent)

* servers:
    - 10.100.1.10: k8s master with kubectl.
    - 10.100.1.11,10.100.1.12: k8s nodes to run real applications.


#### PROD (a full public environtent)

* servers:
    - 10.0.1.10: k8s master with kubectl.  (It's only a demonstration. You must run multi-master for real product environment.)
    - 10.0.1.11,10.0.1.12: k8s nodes to run real applications.

## about Pipline

If we have a jenkins running up, we can hook the script 'build-and-release.py' to jenkins jobs, and configure a jenkins pipline to call these jobs.

Pipline jobs could be like this:

* A job to do building works with command:  `python3 build-and-release.py build -p company-news-java`
* A job to deploy apps to SIT environment: `python3 build-and-release.py release -p company-news-java -e sit`
* A job to call auto-test works if our QA team supported.
* A job to ask user if sit test was passed. If passed, do next job.( No script hooked.)
* A job to release apps to UAT environment: `python3 build-and-release.py release -p company-news-java -e uat`
* A job to ask user if uat test was passed. If passed, do next job.( No script hooked.)
* A job to release apps to PROD environment: `python3 build-and-release.py release -p company-news-java -e prod`

## about HA, Log and Monitor.

#### HA

Cause we use kubernetes on PROD environment, we can define a multi-replicas instance in app's deployment.yaml. Kubernetes will handle the single-server-failure problem.

#### log

Appy a daemonset with 'filebeat' to gatther containers stdout logs, deliver log-contents to 'kafka', configure a 'logstash' to consume log data from kafka, and write log data into 'elasticsearch'. So we can run a 'kibana' to view these logs.

#### monitor.

Use 'Prometheus' with kubernetes. If our apps support health-check API, the monitoring work will go easy.

## Other Suggestions

If we want to control our release acitons and do forther more automated works like fast roll-back, making snapshot of all running apps, migrating your producting environment, or calling up fast an entire new producting environment, we should not only play games within jenkins. We'd better to code an independent CD system, which has a web-ui, to accomplish these high-level CD functions.  
