# Generated by Django 3.1 on 2020-12-25 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obywatele', '0016_auto_20201225_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uzytkownik',
            name='city',
            field=models.CharField(blank=True, help_text='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='for_sale',
            field=models.CharField(blank=True, help_text='', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='hobby',
            field=models.CharField(blank=True, help_text='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='i_need',
            field=models.CharField(blank=True, help_text='', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='to_borrow',
            field=models.CharField(blank=True, help_text='', max_length=500, null=True),
        ),
    ]
