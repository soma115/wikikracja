#!/bin/bash

# software
yum -y install epel-release git-all python3 virtualenv nginx python2-certbot-nginx

# python
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt


podman run -p 6379:6379 -d redis:6