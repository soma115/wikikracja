'''
Put emails in to gen_users.txt file, one per line
'''

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zzz.settings")
import django
django.setup()
from django.contrib.auth.models import User, Group,Permission
from django.contrib.contenttypes.models import ContentType
from customize.models import Customize
import csv
import random
from django.db import IntegrityError

with open('gen_users_out.txt', 'a') as dest:
    # dest.writelines(['username','   ','password','   ','email','\n'])  # headers
    with open('gen_users.txt', 'r') as source:
        read_data = csv.reader(source)
        # next(read_data, None)  # skip the headers
        for i in read_data:
            email = i[0]
            username = i[0].split('@')[0]
            password = ''.join([random.SystemRandom().choice('abcdefghjkmnoprstuvwxyz23456789!@#$%=+') for i in range(8)])
            try:
                user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
                dest.writelines([username,'   ',password,'   ',email,'\n'])
            except IntegrityError as e:
                print(f"Username '{username}' or email '{email}' already exist. Skipping...")
                continue
            except Exception as f:
                print(f)
                continue
            print(f"Username '{username}' with email '{email}' - created")

# Create Editor group
new_group, created = Group.objects.get_or_create(name='Editor')
proj_add_perm = Permission.objects.get(name='Can add Article')
new_group.permissions.add(proj_add_perm)
proj_add_perm = Permission.objects.get(name='Can change Article')
new_group.permissions.add(proj_add_perm)
proj_add_perm = Permission.objects.get(name='Can delete Article')
new_group.permissions.add(proj_add_perm)
proj_add_perm = Permission.objects.get(name='Can view Article')
new_group.permissions.add(proj_add_perm)
proj_add_perm = Permission.objects.get(name='Can change customize')
new_group.permissions.add(proj_add_perm)
proj_add_perm = Permission.objects.get(name='Can view customize')
new_group.permissions.add(proj_add_perm)

# Add first user to group
first = User.objects.get(id=1)
editor = Group.objects.get(name='Editor')
editor.user_set.add(first)

# First user is intruducer.
# Only this one can be active because all other users needs to be approved by system.
# Only then reputation is assigned correctly by the system.
first.is_active=True
first.is_staff=True
first.save()
print(f"\nUser '{first.username}' '{first.email}' set as introducer.\n")

# Doesn't work because reputation level is growing but reputation is not given out
# all_users = User.objects.all()
# for i in all_users:
#     i.is_active = True
#     i.save()


'''
Dump Users information from DataBase:
$ python manage.py dumpdata auth.User --indent 4 > users.json
Import / load data especific JSON fixture:
$ python manage.py loaddata users.json

# from django.contrib.auth.hashers import make_password
# print(user)
# print(make_password('test', 'abc'))
'''