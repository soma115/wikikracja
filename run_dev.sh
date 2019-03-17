#!/bin/bash

# source ../wikikracja-venv/bin/activate
# workon wiki

./manage.py makemigrations glosowania
./manage.py makemigrations obywatele
./manage.py makemigrations elibrary
./manage.py makemigrations
./manage.py migrate
./manage.py runserver


