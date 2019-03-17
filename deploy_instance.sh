#!/bin/bash

# TODO: generowanie secret key

echo "Name your instance. This name should be also configured domain:"
read iname
# i is for instance
# Ta zmienna będzie użyta w demonie, nginxie, itd.
# Wcześniej oczywiście trzeba dodać domenę na DNS'ie
# Other variables should be generated autmatically:
# username = current user (iuser)
# dbpassword = random (idbpassword)

mkdir /var/www/$iname

# Create database:
idbpassword=`pwgen 10 1`
sudo su - postgres <<EOF
psql -c "CREATE DATABASE $iname;"
psql -c "CREATE USER $iname WITH PASSWORD '$idbpassword';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $iname TO $iname;"
EOF

echo 1

# Create gunicorn service
touch /etc/systemd/system/$iname.service
cat <<EOF >> /etc/systemd/system/$iname.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=r1
Group=nginx
WorkingDirectory=/var/www/$iname
ExecStart=/var/www/$iname-venv/bin/gunicorn --workers 3 --bind unix:/var/www/$iname.sock zzz.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

echo 2

# Create vhost
touch /etc/nginx/conf.d/$iname.conf
cat <<EOF >> /etc/nginx/conf.d/$iname.conf
server {
    server_name $iname.dobrada.pl;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/$iname;
    }
    location / {
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_pass http://unix:/var/www/$iname.sock;
    }
}
server {
    listen 80;
    server_name $iname.dobrada.pl;
    return 404;
}
EOF

echo 3

systemctl daemon-reload

systemctl enable nginx postgresql $iname
systemctl restart nginx postgresql $iname
systemctl status nginx postgresql $iname

echo 4

chown -R r1:nginx /var/www/$iname
chmod -R g+w /var/www/$iname
su - r1 -c "git clone git@gitlab.com:robert.fialek/currency.git /var/www/$iname"

echo 5

# virtualenv -p python36 /var/www/$iname-venv
# source /var/www/$iname-venv/bin/activate
# pip install -q --upgrade pip
# pip install -q -r /var/www/$iname/requirements.txt

echo 6

/var/www/$iname/manage.py makemigrations obywatele
/var/www/$iname/manage.py makemigrations glosowania
/var/www/$iname/manage.py makemigrations elibrary
/var/www/$iname/manage.py makemigrations
/var/www/$iname/manage.py migrate
/var/www/$iname/manage.py collectstatic
/var/www/$iname/manage.py createsuperuser

deactivate

echo 7

find /var/www/$iname -type f -exec chmod 440 {} \;
find /var/www/$iname -type d -exec chmod 550 {} \;

echo 8

sudo usermod -a -G $iuser nginx

# run certbot
certbot --nginx

echo $idbpassword

~
~
~
~
~
~
~
~