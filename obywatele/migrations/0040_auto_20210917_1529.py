# Generated by Django 3.1.12 on 2021-09-17 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obywatele', '0039_auto_20210917_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uzytkownik',
            name='hobby',
            field=models.CharField(blank=True, help_text='Hobbies one have', max_length=200, null=True, verbose_name='Hobby'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='to_give_away',
            field=models.TextField(blank=True, help_text='Things you are willing to give away for free', max_length=2000, null=True, verbose_name='To give away'),
        ),
    ]
