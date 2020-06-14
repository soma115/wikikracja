# wikikracja
This is community building system. Currently consist of two functioning modules: voting and citizens
Voting module (glosowania) uses principle known as Zero Knowledge Proof (https://youtu.be/HUs1bH85X9I). It means that voting is fairly anonymous.

## Requirements
You will need email account like gmail in order to send emails to users.
Smallest VM is enough. 

## Installation (Centos 7)
- Setup Gunicorn+Postgres+Nginx+Centos7: https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-centos-7
- Setup Daphne server https://pypi.org/project/daphne/ or https://avilpage.com/2018/05/deploying-scaling-django-channels.html
[TODO: Learn how to run it with Daphne only]
- Clone repository: git clone https://github.com/soma115/wikikracja.git
- adjust zzz/setting.py: Add SECRET_KEY etc.
- Set site name in your_page.com/admin/sites/site/

## Known issues
- if you get Error 500 - clear cookies in your web browser
- `yum install python36-devel` on Centos 7 for Channels
- Issues installing Pillow. Try:
    python -m pip install -U --force-reinstall pip
    easy_install pillow

### Fedora
- run: dnf install python3-devel
- Pillow issue: check requrements.txt version vs. OS version
- 
