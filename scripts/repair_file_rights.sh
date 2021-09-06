#!/bin/bash

chown -R user:nginx $1

find $1 -type d -exec chmod 700 {} \;
find $1 -type f -exec chmod 600 {} \;

chmod 500 $1/manage.py
chmod 700 $1/scripts/*.sh
#chmod 400 $1/db.sqlite3
#chmod 400 $1/zzz/settings.py

chown user /var/lib/nginx
chown user /var/lib/nginx/tmp
