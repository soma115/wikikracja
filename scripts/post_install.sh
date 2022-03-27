#!/bin/bash

DOMAIN=`grep ALLOWED_HOSTS zzz/settings_custom.py | cut -d "'" -f 2`
APP=`echo ${DOMAIN} | cut -d '.' -f 1`
HOME=/home/user/$APP/

# DEPLOY DB
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py makemigrations article;
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py makemigrations chat;
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py makemigrations customize;
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py makemigrations elibrary;
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py makemigrations glosowania;
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py makemigrations obywatele;
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py makemigrations;
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py migrate;
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py makemessages -l 'en' --ignore=.git/* --ignore=static/* --ignore=.mypy_cache/*;
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py makemessages -l 'pl' --ignore=.git/* --ignore=static/* --ignore=.mypy_cache/*;
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py compilemessages --ignore=.git/* --ignore=static/* --ignore=.mypy_cache/*;

# FIXTURES
# Carefull - it will duplicate existing records if run second time - especialy if you'll use: "pk": null,
# TODO: grep settings.py to find out which language should be deployed
# Dump: ./manage.py dumpdata customize.customize > customize.json  # customize.customize is a table
# ./manage.py loaddata article/fixtures/articles.json
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py loaddata $HOME/$APP/customize/fixtures/customize.json

# SITE NAME
# Change example.com to actuall domain name
sqlite3 db.sqlite3 "update django_site set name='${DOMAIN}', domain='${DOMAIN}'"

# CERTBOT
certbot --nginx --quiet --agree-tos --domains ${DOMAIN}

# VOTINGS
# Fixtures z początkowymi głosowaniami do wiki
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py loaddata $HOME/$APP/glosowania/fixtures/votings.json

# COLLECT STATIC
cd $HOME/$APP; $HOME/venv/bin/python $HOME/$APP/manage.py collectstatic --no-input -v 0 --no-post-process -i *bootstrap.css

# RESTART INSTANCE
supervisorctl restart ${APP}:asgi0
