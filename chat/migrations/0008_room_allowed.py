# Generated by Django 3.1 on 2021-01-02 15:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0007_remove_room_staff_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='allowed',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
