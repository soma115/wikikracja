#!/bin/bash

# This way there will be no errors in logs

supervisorctl reread
supervisorctl update

systemctl stop nginx
sleep 1
systemctl restart supervisord
sleep 1
systemctl start nginx
sleep 5
systemctl status nginx supervisord
