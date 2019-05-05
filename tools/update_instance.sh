#!/bin/bash

# TODO: git clone if not exist

git reset --hard
git pull

# There has to exist ../venv/bin/activate
source /var/www/venv/bin/activate

<<<<<<< HEAD
find . -name *.pyc -exec rm -rf {} \;
find -maxdepth 2 -mindepth 2 -type d -name migrations -exec rm -rf {} \;
=======
#sudo su - postgres <<EOF
#psql -c "DROP DATABASE wikikracja_dev;"
#psql -c "DROP USER wikikracja_dev;"
#psql -c "CREATE DATABASE wikikracja_dev;"
#psql -c "CREATE USER wikikracja_dev WITH PASSWORD 'tymczasowe1000'";
#psql -c "GRANT ALL PRIVILEGES ON DATABASE wikikracja_dev TO wikikracja_dev";
#EOF

# rm db.sqlite3

>>>>>>> 89f36f7d84066208d3b1cafd023f0c5a2e086e93
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
