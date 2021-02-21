#!/bin/bash

# Used to update production instances
# Run within python virtual environment and and within app home directory
# For example:
#     cd /home/user/wiki/wiki/
#     source ../venv/bin/activate
#     ./script/update.sh

git reset --hard --quiet    
git pull | grep -q -F 'Already up to date.' && exit 0

pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "Changing files rights..."
chown -R user:nginx .
find -type d -exec chmod 751 {} \;
find -type f -exec chmod 640 {} \;
chmod 700 ./scripts/*
chmod 700 ./manage.py
chmod 660 db.sqlite3
chmod u+w media/
echo ""

${1}/manage.py makemigrations waluty
${1}/manage.py makemigrations home
${1}/manage.py makemigrations
${1}/manage.py migrate
${1}/manage.py makemessages -l 'en'
${1}/manage.py makemessages -l 'pl'
${1}/manage.py makemessages -l 'de'
${1}/manage.py compilemessages
${1}/manage.py collectstatic --no-input -c -v 0

echo "Restarting `basename $(dirname "$PWD")`"
supervisorctl reread
supervisorctl update
supervisorctl restart `basename $(dirname "$PWD")`:asgi0
echo -n "nginx is:	"; systemctl is-active nginx
echo -n "redis is:	"; systemctl is-active redis
echo -n "supervisord is:	"; systemctl is-active supervisord
supervisorctl status | grep `basename $(dirname "$PWD")`
echo ""
