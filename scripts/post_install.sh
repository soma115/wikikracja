#!/bin/bash

# FIXTURES
# Carefull - it will duplicate existing records if run second time - especialy if you'll use: "pk": null,
# TODO: grep settings.py to find out which language should be deployed
# Dump: ./manage.py dumpdata customize.customize > customize.json  # customize.customize is a table
# ./manage.py loaddata article/fixtures/articles.json
../venv/bin/python ./manage.py loaddata customize/fixtures/customize.json

# SITE NAME
# Change example.com to actuall domain name
DOMAIN=`grep ALLOWED_HOSTS zzz/settings_custom.py | cut -d "'" -f 2`
sqlite3 db.sqlite3 "update django_site set name='${DOMAIN}', domain='${DOMAIN}'"

# CERTBOT
certbot --nginx --quiet --agree-tos --domains ${DOMAIN}

# VOTINGS
# Fixtures z początkowymi głosowaniami do wiki
../venv/bin/python ./manage.py loaddata glosowania/fixtures/votings.json

# RESTART INSTANCE
APP=`echo ${DOMAIN} | cut -d '.' -f 1`
supervisorctl restart ${APP}:asgi0
