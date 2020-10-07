#!/bin/bash

# run with virtual environment and and within app home directory

git reset --hard
git pull

# There has to exist ../venv/bin/activate
# source /var/www/venv/bin/activate

./manage.py makemigrations obywatele
./manage.py makemigrations glosowania
./manage.py makemigrations elibrary
./manage.py makemigrations chat
./manage.py makemigrations
./manage.py migrate

chown -R user:nginx *
# chmod -R o-rwx *
chmod u+w media/

./manage.py collectstatic --noinput
# ./manage.py createsuperuser"
