#!/bin/bash

# software
dnf -y install epel-release 
dnf -y install git-all python3 virtualenv nginx python3-certbot-nginx supervisord podman

# user
adduser user -s /sbin/nologin

# configs
cp ./scripts/etc/supervisord.d/wiki.ini /etc/supervisord.d/
cp ./scripts/etc/nginx/conf.d/wiki.conf /etc/nginx/conf.d/

# app folder
mkdir /home/user/wiki

# python
git clone https://github.com/soma115/wikikracja.git /home/user/wiki/wiki/
virtualenv -p python3 /home/user/wiki/venv
source /home/user/wiki/venv/bin/activate
pip3 install -r /home/user/wiki/wiki/requirements.txt

# user rights etc.
/home/user/wiki/wiki/scripts/update.sh

# services
systemctl enable nginx supervisord
./scripts/restart_services.sh