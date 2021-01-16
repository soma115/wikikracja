#!/bin/bash

supervisorctl reread
supervisorctl update

systemctl stop nginx
sleep 1
systemctl restart supervisord redis
sleep 1
systemctl start nginx
sleep 1
echo -n "nginx is: "; systemctl is-active nginx
echo -n "redis is: "; systemctl is-active redis
echo -n "supervisord is: "; systemctl is-active supervisord

echo "supervisorctl restart demo:asgi0  #restart 1 webpage"
