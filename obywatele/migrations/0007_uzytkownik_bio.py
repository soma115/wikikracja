# Generated by Django 3.1 on 2020-11-24 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obywatele', '0006_auto_20201113_2250'),
    ]

    operations = [
        migrations.AddField(
            model_name='uzytkownik',
            name='bio',
            field=models.CharField(editable=False, max_length=2000, null=True),
        ),
    ]
