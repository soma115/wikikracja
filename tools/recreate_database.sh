#!/bin/bash

if [ "$1" != "" ]; then
    name=$1
    password=`pwgen 10 1`
<<<<<<< HEAD

    # Drop database:
    sudo -u postgres psql -c "DROP DATABASE $name;"
    sudo -u postgres psql -c "DROP USER $name;"

=======
   
>>>>>>> 89f36f7d84066208d3b1cafd023f0c5a2e086e93
    # Create database and user:
    sudo -u postgres psql -c "CREATE USER $name WITH PASSWORD '$password';"
    sudo -u postgres psql -c "CREATE DATABASE $name;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $name TO $name;"
    
<<<<<<< HEAD
    echo ""
=======
>>>>>>> 89f36f7d84066208d3b1cafd023f0c5a2e086e93
    echo Database name: $name
    echo Database user: $name
    echo Database password: $password

else
    echo ""
    echo "Usage: create_database.sh database_name"
    echo "Please note: database name and database user will be same"
    echo ""
    exit 1

fi
