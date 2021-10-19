
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zzz.settings")
import django
django.setup()
django.setup()
from django.contrib.auth.models import User, Group,Permission

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