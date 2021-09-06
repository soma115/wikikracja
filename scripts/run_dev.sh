#!/bin/bash

# Used to run local develepment instances

# 'podman' is an equivalent of 'docker' on Centos/RedHat
# podman/docker will not work on OpenVZ. At least KVM VM is needed.
# podman run -p 6379:6379 -d redis:6
mkdir -p media/uploads

pip install -q -r requirements.txt

./manage.py makemigrations glosowania
./manage.py makemigrations obywatele
./manage.py makemigrations elibrary
./manage.py makemigrations chat
./manage.py makemigrations customize
./manage.py makemigrations article
./manage.py makemigrations
./manage.py migrate

./manage.py makemessages -l 'en' --ignore=.git/* --ignore=static/* --ignore=.mypy_cache/*
./manage.py makemessages -l 'pl' --ignore=.git/* --ignore=static/* --ignore=.mypy_cache/*
./manage.py compilemessages --ignore=.git/* --ignore=static/* --ignore=.mypy_cache/*
# ./manage.py compilemessages

# run if needed:
# ./manage.py collectstatic --no-input -c -v 0

# this one needs to be run first time instance is installed
# ./manage.py loaddata customize/fixtures/customize.json

./manage.py runserver
