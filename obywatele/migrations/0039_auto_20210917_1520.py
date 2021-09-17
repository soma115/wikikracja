# Generated by Django 3.1.12 on 2021-09-17 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obywatele', '0038_auto_20210917_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uzytkownik',
            name='hobby',
            field=models.CharField(blank=True, default=None, help_text='Hobbies one have', max_length=200, null=True, verbose_name='Hobby'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='to_give_away',
            field=models.TextField(blank=True, default=None, help_text='Things you are willing to give away for free', max_length=2000, null=True, verbose_name='To give away'),
        ),
    ]
