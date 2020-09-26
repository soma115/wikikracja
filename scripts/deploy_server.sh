#!/bin/bash

# software
dnf -y install epel-release 
dnf -y install git-all python3 virtualenv nginx python3-certbot-nginx supervisor podman

# user
adduser user -s /sbin/nologin

# app folder
mkdir /home/user/wiki  # TODO: as parameter or something
cd /home/user/wiki

# python
git clone https://github.com/soma115/wikikracja.git
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r wiki/requirements.txt

# user rights etc.
./wiki/scripts/update.sh

# services
cp wiki/scripts/etc/supervisord.d/wiki.ini /etc/supervisord.d/
cp wiki/scripts/etc/nginx/conf.d/wiki.conf /etc/nginx/conf.d/
systemctl enable nginx supervisord
./scripts/restart_services.sh
