# wikikracja
This is community building system. Currently consist of two functioning modules: voting and citizens
Voting module (glosowania) uses principle known as Zero Knowledge Proof (https://youtu.be/HUs1bH85X9I). It means that voting is fairly anonymous.

## Requirements
You will need email account like gmail in order to send emails to users.
Smallest VM is enough. 

## Installation
Clone repository:
- git clone git@gitlab.com:wikikracja/wikikracja.git some_folder
- create virtual environment and 'pip install -r requirements.'
- setup gunicorn, nginx and postgres e.g. like this: https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-centos-7
- install Channels: https://www.tutorialdocs.com/tutorial/django-channels/installation.html

## Known problems
- if you get Error 500 - clear cookies in your web browser
- `yum install python36-devel` on Centos 7 for Channels
- 