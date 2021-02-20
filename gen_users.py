import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zzz.settings")
import django
django.setup()
from django.contrib.auth.models import User
import csv
import random
from django.db import IntegrityError

with open('gen_users_out.txt', 'w') as dest:
    dest.writelines(['username',' ','password',' ','email','\n'])  # headers

    with open('gen_users.txt', 'r') as source:
        read_data = csv.reader(source)
        # next(read_data, None)  # skip the headers
        for i in read_data:
            email = i[0]
            username = i[0].split('@')[0]
            password = ''.join([random.SystemRandom().choice('abcdefghjkmnoprstuvwxyz23456789!@#$%=+') for i in range(8)])
            dest.writelines([username,'        ',password,' ',email,'\n'])
            try:
                user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
            except IntegrityError as e:
                print(f"Username '{username}' or email '{email}' already exist. Skipping...")
                continue
            except Exception as f:
                print(f)
                continue
            print(f"Username '{username}' with email '{email}' - created")

first = User.objects.get(id=1)
first.is_active=True
first.save()
print(f"User '{first.username}' '{first.email}' set as introducer.")
#TODO: Jak zrobić żeby piewszy user był aktywny? Może będzie z natury... Przetestować


'''
Dump Users information from DataBase:
$ python manage.py dumpdata auth.User --indent 4 > users.json
Import / load data especific JSON fixture:
$ python manage.py loaddata users.json

# from django.contrib.auth.hashers import make_password
# print(user)
# print(make_password('test', 'abc'))
'''