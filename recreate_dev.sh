#!/bin/bash

# source ../wikikracja-venv/bin/activate

sudo su - postgres <<EOF
psql -c "DROP DATABASE wikikracja_dev;"
psql -c "DROP USER wikikracja_dev;"
psql -c "CREATE DATABASE wikikracja_dev;"
psql -c "CREATE USER wikikracja_dev WITH PASSWORD 'tymczasowe1000'";
psql -c "GRANT ALL PRIVILEGES ON DATABASE wikikracja_dev TO wikikracja_dev";
EOF

# rm db.sqlite3

find . -name *.pyc -exec rm -rf {} \;
find -maxdepth 2 -mindepth 2 -type d -name migrations -exec rm -rf {} \;

./manage.py makemigrations obywatele
./manage.py makemigrations glosowania
./manage.py makemigrations elibrary
./manage.py makemigrations
./manage.py migrate

./manage.py createsuperuser
