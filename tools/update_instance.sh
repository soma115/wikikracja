#!/bin/bash

# TODO: git clone if not exist

git reset --hard
git pull

# There has to exist ../venv/bin/activate
source /var/www/venv/bin/activate

mkdir static media

./manage.py makemigrations obywatele
./manage.py makemigrations glosowania
./manage.py makemigrations elibrary
./manage.py makemigrations
./manage.py migrate

chown -R r1:nginx *
chmod -R o-rwx *
chmod u+w media/
# find -type f -exec chmod ugo-x {} \;

echo ""
echo "--------------"
echo "./manage.py createsuperuser"
echo "./manage.py collectstatic"
echo "was skipped. Run it manually if you need it."
echo "--------------"
echo ""
