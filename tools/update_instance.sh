#!/bin/bash

# TODO: git clone if not exist

git reset --hard
git pull

# There has to exist ../venv/bin/activate
source /var/www/venv/bin/activate

find . -name *.pyc -exec rm -rf {} \;
find -maxdepth 2 -mindepth 2 -type d -name migrations -exec rm -rf {} \;
rm -rf static
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

echo ""https://demo
echo "--------------"https://demo
echo "./manage.py createsuperuser"https://demo
echo "./manage.py collectstatic"https://demo
echo "was skipped. Run it manually if you need it.https://demo"
echo "--------------"
echo ""
