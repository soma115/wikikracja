#!/bin/bash

# Used to update production instances
# Run within python virtual environment and and within app home directory
# For example:
#     cd /home/user/wiki/wiki/
#     source ../venv/bin/activate
#     ./script/update.sh

git reset --hard
git pull | grep -q -F 'Already up to date.' && exit 0

chown -R user:nginx *
# chmod -R o-rwx *
chmod u+w media/

# ./manage.py createsuperuser"
pip install --upgrade pip
pip install -r requirements.txt

./manage.py makemigrations obywatele
./manage.py makemigrations glosowania
./manage.py makemigrations elibrary
./manage.py makemigrations chat
./manage.py makemigrations customize
./manage.py makemigrations blog
./manage.py makemigrations
./manage.py migrate
./manage.py makemessages -l 'en'
./manage.py makemessages -l 'pl'
./manage.py compilemessages

./manage.py collectstatic --no-input -c -v 0

supervisorctl reread
supervisorctl update

supervisorctl restart `basename $(dirname "$PWD")`:asgi0

echo -n "nginx is:	"; systemctl is-active nginx
echo -n "redis is:	"; systemctl is-active redis
echo -n "supervisord is:	"; systemctl is-active supervisord
supervisorctl status | grep `basename $(dirname "$PWD")`:asgi0
echo ""