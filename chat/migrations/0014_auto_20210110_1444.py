# Generated by Django 3.1 on 2021-01-10 13:44

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0013_auto_20210103_2014'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='message',
            unique_together={('sender', 'text', 'room', 'time')},
        ),
    ]
