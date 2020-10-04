#!/bin/bash

supervisorctl reread
supervisorctl update

systemctl stop nginx
sleep 1
systemctl restart supervisord
sleep 1
systemctl start nginx
sleep 1
systemctl status nginx supervisord | grep Active

podman rm --all
podman volume rm $(podman volume ls -q)
