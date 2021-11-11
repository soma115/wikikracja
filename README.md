## Wikikracja
This is community building system. Currently it consist following modules:
- voting
- citizens
- chat
- eLibrary
- blog
  
Voting module (glosowania) uses principle known as Zero Knowledge Proof (https://youtu.be/HUs1bH85X9I).  
It means that voting is anonymous.

## Demo
You can find demo here:
https://demo.wikikracja.pl/

Login: demo  
Password: #democracynow

## Requirements
You will need email account like gmail in order to send emails to users. 
Smallest KVM VM is enough. 

## Installation (Centos 7, 8)
- Run as root:

`wget https://raw.githubusercontent.com/soma115/wikikracja/master/scripts/deploy_server.sh; chmod u+x deploy_server.sh; ./deploy_server.sh`
- Set 'user' as default in /etc/nginx/nginx.conf (user user;)
- Adjust zzz/setting.py: Add SECRET_KEY etc. (you may use zzz/settings_exampla.py as template)
- Enable (`source`) virtual environment
- run `./scripts/update.sh` from application root
- run `cerbot --nginx`
- `./manage.py createsuperuser`
- Set site name in your_page.com/admin/sites/site/

## Known issues
- if you get Error 500 - clear cookies in your web browser
- `yum install python36-devel` on Centos 7 for Channels
- Issues installing Pillow. Try:
    `python -m pip install -U --force-reinstall pip`
    `easy_install pillow`

### Fedora
- run: `dnf install python3-devel`
- Pillow issue: check requirements.txt version vs. OS version

## After installation
- Copy settings_custom_template.py to settings_custom.py and adjust its content
- Create superuser (superuser will be eliminated in future versions)
- Create 'Editor' group and assign rights:
    - Article - add, change, view, delete
    - Customize - change, view
    Each new user will be automaticaly assigned to group 'Editor'
- Apply fixtures to create Footer and Start page: ./manage.py loaddata customize/fixtures/customize.json
- Give site a name https://yoursite.com/admin/sites/site/
