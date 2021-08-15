#!/bin/bash

# Used to run local develepment instances

# 'podman' is an equivalent of 'docker' on Centos/RedHat
# podman/docker will not work on OpenVZ. At least KVM VM is needed.
# podman run -p 6379:6379 -d redis:6
pip install -q -r requirements.txt

./manage.py makemigrations glosowania
./manage.py makemigrations obywatele
./manage.py makemigrations elibrary
./manage.py makemigrations chat
./manage.py makemigrations customize
./manage.py makemigrations
./manage.py migrate

./manage.py makemessages -l 'en'
./manage.py makemessages -l 'pl'
./manage.py compilemessages

./manage.py runserver
