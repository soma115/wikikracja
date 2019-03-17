#!/bin/bash

yum -y install python2-certbot-nginx git nginx postgresql postgresql-server python-virtualenv python36 pwgen

# Not sure if needed:
# yum-config-manager --enable rhui-REGION-rhel-server-extras rhui-REGION-rhel-server-optional
# yum -y install epel-release gunicorn yum-utils python-pip python-devel postgresql-devel postgresql-contrib gcc

# If you need to open firewall:
#firewall-cmd --get-active-zones
#echo "W zależności od tego jakie strefy istnieją należy zmienić --zone poniżej"
#firewall-cmd --zone=trusted --add-port=80/tcp --permanent
#firewall-cmd --zone=trusted --add-port=443/tcp --permanent
#firewall-cmd --reload

postgresql-setup initdb
systemctl restart postgresql
systemctl stop postgresql
# Doesn't work:
/var/lib/pgsql/data/pg_hba.conf  <<EOF
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF

systemctl restart nginx ; systemctl restart postgresql
