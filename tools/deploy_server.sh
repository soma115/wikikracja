#!/bin/bash

# software
yum -y install epel-release
yum -y install postgresql postgresql-server postgresql-devel postgresql-contrib python37 python37-libs python37-devel python37-pip python-pip yum-utils python-virtualenv git vim gcc nginx pwgen docker certbot python-certbot-nginx
yum -y install https://centos7.iuscommunity.org/ius-release.rpm
yum -y install epel-release
yum -y update
yum -y groupinstall development
yum install -y  

# python
virtualenv -p python3.6 /var/www/prod-env
source /var/www/prod-env/bin/activate
pip install --upgrade pip
pip3.6 install -r /var/www/wikikracja/requirements.txt
pip install -U pip
pip install -U virtualenv
pip install -U gunicorn

# If you need to open firewall:
firewall-cmd --get-active-zones
#echo "W zależności od tego jakie strefy istnieją należy zmienić --zone poniżej"
firewall-cmd --zone=trusted --add-port=80/tcp --permanent
firewall-cmd --zone=trusted --add-port=443/tcp --permanent
firewall-cmd --reload

# database
systemctl enable postgresql
systemctl start postgresql
postgresql-setup initdb
systemctl restart postgresql

# docker
systemctl enable docker
systemctl start docker