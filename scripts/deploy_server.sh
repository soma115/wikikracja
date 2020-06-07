#!/bin/bash

# software
yum -y install epel-release git-all python3 virtualenv nginx python2-certbot-nginx docker

# python
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt

# docker
systemctl enable docker
systemctl start docker