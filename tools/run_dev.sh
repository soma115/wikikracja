#!/bin/bash

./manage.py makemigrations glosowania
./manage.py makemigrations obywatele
./manage.py makemigrations elibrary
./manage.py makemigrations
./manage.py migrate
./manage.py runserver


