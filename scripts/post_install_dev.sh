#!/bin/bash

./manage.py loaddata customize/fixtures/customize.json
./manage.py loaddata glosowania/fixtures/votings.json

sqlite3 db.sqlite3 "update django_site set name='127.0.0.1', domain='127.0.0.1'"
