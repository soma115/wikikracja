#!/bin/bash

yum -y install https://centos7.iuscommunity.org/ius-release.rpm
yum -y install epel-release
yum -y update
yum -y groupinstall development
yum install -y python36u python36u-libs python36u-devel python36u-pip yum-utils python-virtualenv git vim postgresql-server postgresql-devel postgresql-contrib gcc nginx 
mkdir /var/www
virtualenv -p python3.6 /var/www/prod-env
source /var/www/prod-env/bin/activate
pip3.6 install -r /var/www/wikikracja/requirements.txt