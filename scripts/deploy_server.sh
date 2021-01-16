#!/bin/bash

echo; echo SOFTWARE 
dnf -y install epel-release
dnf -y install git-all python3 virtualenv nginx python3-certbot-nginx supervisor redis

echo; echo USER
adduser user -s /sbin/nologin  # TODO: make it to be parameter or something

echo; echo APP FOLDER
mkdir /home/user/wiki
cd /home/user/wiki

echo; echo PYTHON
git clone https://github.com/soma115/wikikracja.git
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r wikikracja/requirements.txt

echo; echo USER RIGHTS ETC.
cd wikikracja
chown -R user:nginx *
chmod u+w media/

echo; echo SERVICES
cp scripts/wiki.conf /etc/nginx/conf.d/
cp scripts/wiki.ini /etc/supervisord.d/
cp scripts/redis.ini /etc/supervisord.d/
systemctl enable nginx supervisord redis
./scripts/restart_services.sh
