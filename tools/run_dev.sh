#!/bin/bash

sudo docker run -p 6379:6379 -d redis:2.8

./manage.py makemigrations glosowania
./manage.py makemigrations obywatele
./manage.py makemigrations elibrary
./manage.py makemigrations
./manage.py migrate
./manage.py runserver


