# Generated by Django 3.1 on 2020-11-13 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obywatele', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='akceptacjaosoby',
            name='rate',
            field=models.SmallIntegerField(default=0, null=True),
        ),
    ]
