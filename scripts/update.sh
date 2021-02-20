#!/bin/bash

# Used to update production instances
# Run within python virtual environment and and within app home directory
# For example:
# cd /home/user/wiki/wiki/
# source ../venv/bin/activate
# ./script/update.sh

git reset --hard
git pull

./manage.py makemigrations obywatele
./manage.py makemigrations glosowania
./manage.py makemigrations elibrary
./manage.py makemigrations chat
./manage.py makemigrations
./manage.py migrate
./manage.py makemessages -l 'en'
./manage.py makemessages -l 'pl'
./manage.py compilemessages

chown -R user:nginx *
# chmod -R o-rwx *
chmod u+w media/

./manage.py collectstatic --no-input -c -v 0
# ./manage.py createsuperuser"
pip install -r requirements.txt

supervisorctl reread
supervisorctl update

# TODO: Don't restart everything if possible
systemctl stop nginx; sleep 1
systemctl restart supervisord; sleep 1
systemctl start nginx; sleep 1

echo -n "nginx is:	"; systemctl is-active nginx
echo -n "redis is:	"; systemctl is-active redis
echo -n "supervisord is:	"; systemctl is-active supervisord
echo ""
supervisorctl status
