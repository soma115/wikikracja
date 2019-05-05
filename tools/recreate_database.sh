#!/bin/bash

if [ "$1" != "" ]; then
    name=$1
    password=`pwgen 10 1`
   
    # Create database and user:
    sudo -u postgres psql -c "CREATE USER $name WITH PASSWORD '$password';"
    sudo -u postgres psql -c "CREATE DATABASE $name;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $name TO $name;"
    
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
