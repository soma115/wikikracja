# Generated by Django 3.1.12 on 2021-09-30 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obywatele', '0040_auto_20210917_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uzytkownik',
            name='business',
            field=models.TextField(blank=True, help_text='If running a business', max_length=2000, null=True, verbose_name='Business'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='for_sale',
            field=models.TextField(blank=True, help_text='Stuff you have for sale', max_length=2000, null=True, verbose_name='For sale'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='hobby',
            field=models.CharField(blank=True, help_text='Hobbies one have', max_length=2000, null=True, verbose_name='Hobby'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='i_need',
            field=models.TextField(blank=True, help_text='What do you need', max_length=2000, null=True, verbose_name='I need'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='job',
            field=models.CharField(blank=True, help_text='Profession', max_length=2000, null=True, verbose_name='Job'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='knowledge',
            field=models.TextField(blank=True, help_text='Knowledge one have', max_length=2000, null=True, verbose_name='Knowledge'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='other',
            field=models.TextField(blank=True, help_text='Other things worth mentioning', max_length=2000, null=True, verbose_name='Other'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='skills',
            field=models.TextField(blank=True, help_text='Practical skills one have', max_length=2000, null=True, verbose_name='Skills'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='to_borrow',
            field=models.TextField(blank=True, help_text='Stuff you can borrow to others', max_length=2000, null=True, verbose_name='To borrow'),
        ),
        migrations.AlterField(
            model_name='uzytkownik',
            name='want_to_learn',
            field=models.TextField(blank=True, help_text='Things one would like to learn', max_length=2000, null=True, verbose_name='I want to learn'),
        ),
    ]
