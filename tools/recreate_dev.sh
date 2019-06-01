#!/bin/bash

# source ../wikikracja-venv/bin/activate

sudo su - postgres <<EOF
psql -c "DROP DATABASE wikikracja_dev;"
psql -c "DROP USER wikikracja_dev;"
psql -c "CREATE DATABASE wikikracja_dev;"
psql -c "CREATE USER wikikracja_dev WITH PASSWORD 'tymczasowe1000'";
psql -c "GRANT ALL PRIVILEGES ON DATABASE wikikracja_dev TO wikikracja_dev";
EOF

./manage.py makemigrations obywatele
./manage.py makemigrations glosowania
./manage.py makemigrations elibrary
./manage.py makemigrations
./manage.py migrate

./manage.py createsuperuser --username a --noinput --email a@a.pl
./manage.py changepassword a

# ./manage.py createsuperuser

sudo su - postgres <<EOF
psql --dbname wikikracja_dev -c "update auth_user set username='a' where id=1;"
psql --dbname wikikracja_dev -c "update auth_user set is_active=TRUE where id=1;"
psql --dbname wikikracja_dev -c "update auth_user set is_staff=TRUE where id=1;"
psql --dbname wikikracja_dev -c "update django_site set domain='127.0.0.1:8000' where id=1;"
psql --dbname wikikracja_dev -c "update django_site set name='127.0.0.1:8000' where id=1;"
EOF

