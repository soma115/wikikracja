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

./manage.py createsuperuser --email a@a.pl --noinput
./manage.py changepassword a@a.pl

# ./manage.py createsuperuser

sudo su - postgres <<EOF
psql --dbname wikikracja_dev -c "update obywatele_user set username='a' where id=1;"
psql --dbname wikikracja_dev -c "update obywatele_user set is_active=TRUE where id=1;"
psql --dbname wikikracja_dev -c "update obywatele_user set is_staff=TRUE where id=1;"
EOF

