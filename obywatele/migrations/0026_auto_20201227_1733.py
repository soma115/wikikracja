# Generated by Django 3.1 on 2020-12-27 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obywatele', '0025_auto_20201227_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uzytkownik',
            name='to_give_away',
            field=models.TextField(blank=True, help_text='Things you are willing to give away for free', max_length=2000, null=True, verbose_name='To give away'),
        ),
    ]
