# Generated by Django 3.1 on 2020-12-24 21:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('obywatele', '0011_auto_20201222_2117'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uzytkownik',
            old_name='foto',
            new_name='want_to_learn',
        ),
        migrations.RemoveField(
            model_name='uzytkownik',
            name='fb_profil',
        ),
        migrations.RemoveField(
            model_name='uzytkownik',
            name='i_know_personally_those_important_people',
        ),
        migrations.RemoveField(
            model_name='uzytkownik',
            name='i_want_to_learn',
        ),
    ]
