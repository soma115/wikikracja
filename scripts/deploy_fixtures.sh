#!/bin/bash

# Carefull - it will duplicate existing records if run second time

# TODO: grep settings.py to find out which language should be deployed

# Dump: ./manage.py dumpdata customize.customize > customize.json

# ./manage.py loaddata article/fixtures/articles.json
./manage.py loaddata customize/fixtures/customize.json
