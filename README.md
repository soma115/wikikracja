# wikikracja
This is community building system. Currently consist of two functioning modules: voting and citizens
Voting module (glosowania) uses principle known as Zero Knowledge Proof (https://youtu.be/HUs1bH85X9I). It means that voting is fairly anonymous.

## Requirements
You will need email account like gmail in order to send emails to users.
Smallest VM is enough. 

## Installation
Clone repository:
- git clone git@github.com:wikikracja/wikikracja.git some_folder
- install python 3 (i.e. centos 7: https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-centos-7)
- create virtual environment 'virtualenv -p python3 env_name'
- install dependencies 'pip install -r requirements.'
- setup gunicorn, nginx and postgres e.g. like this: https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-centos-7
- install Channels: https://www.tutorialdocs.com/tutorial/django-channels/installation.html

## Known problems
- if you get Error 500 - clear cookies in your web browser
- `yum install python36-devel` on Centos 7 for Channels


yum -y install git; git clone https://github.com/soma115/wikikracja.git /var/www/wikikracja


yum -y install https://centos7.iuscommunity.org/ius-release.rpm
yum -y install epel-release
yum -y update
yum -y groupinstall development
yum install -y python36u python36u-libs python36u-devel python36u-pip yum-utils python-virtualenv git vim postgresql-server postgresql-devel postgresql-contrib gcc nginx 
mkdir /var/www
virtualenv -p python3.6 /var/www/prod-env
source /var/www/prod-env/bin/activate
pip3.6 install -r /var/www/wikikracja/requirements.txt

- setup gunicorn, nginx and postgres e.g. like this: https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-centos-7

