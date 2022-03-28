#!/bin/bash

DOMAIN=`grep ALLOWED_HOSTS zzz/settings_custom.py | cut -d "'" -f 2`
HOME=/home/user/${DOMAIN}/

# DEPLOY DB
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py makemigrations article;
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py makemigrations chat;
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py makemigrations customize;
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py makemigrations elibrary;
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py makemigrations glosowania;
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py makemigrations obywatele;
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py makemigrations;
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py migrate;
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py makemessages -l 'en' --ignore=.git/* --ignore=static/* --ignore=.mypy_cache/*;
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py makemessages -l 'pl' --ignore=.git/* --ignore=static/* --ignore=.mypy_cache/*;
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py compilemessages --ignore=.git/* --ignore=static/* --ignore=.mypy_cache/*;

# FIXTURES
# Carefull - it will duplicate existing records if run second time - especialy if you'll use: "pk": null,
# TODO: grep settings.py to find out which language should be deployed
# Dump: ./manage.py dumpdata customize.customize > customize.json  # customize.customize is a table
# ./manage.py loaddata article/fixtures/articles.json
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py loaddata ${HOME}/${DOMAIN}/customize/fixtures/customize.json

# SITE NAME
# Change example.com to actuall domain name
sqlite3 db.sqlite3 "update django_site set name='${DOMAIN}', domain='${DOMAIN}'"

# CERTBOT
certbot --nginx --quiet --agree-tos --domains ${DOMAIN}

# VOTINGS
# Fixtures z początkowymi głosowaniami do wiki
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py loaddata ${HOME}/${DOMAIN}/glosowania/fixtures/votings.json

# COLLECT STATIC
cd ${HOME}/${DOMAIN}; ${HOME}/venv/bin/python ${HOME}/${DOMAIN}/manage.py collectstatic --no-input -v 0 --no-post-process -i *bootstrap.css

# RESTART INSTANCE
supervisorctl restart ${DOMAIN}:asgi0
