# wikikracja
This is community building system. Currently consist of two functioning modules: voting and citizens
Voting module (glosowania) uses principle known as Zero Knowledge Proof (https://youtu.be/HUs1bH85X9I). It means that voting is fairly anonymous.

## Requirements
You will need email account like gmail in order to send emails to users.
Smallest KVM VM is enough. 

## Installation (Centos 7, 8)
- download scripts/deploy_server.sh and run it as root
- Set 'user' as default in /etc/nginx/nginx.conf (user user;)
- adjust zzz/setting.py: Add SECRET_KEY etc.
- run `cerbot --nginx`
- Set site name in your_page.com/admin/sites/site/
- ./manage.py createsuperuser

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
