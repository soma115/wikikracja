# Generated by Django 3.1 on 2020-11-22 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glosowania', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='decyzja',
            options={'verbose_name_plural': 'Decisions'},
        ),
        migrations.AlterField(
            model_name='decyzja',
            name='kara',
            field=models.TextField(help_text='What is the penalty for non-compliance with this rule. This can be, for example, Banishment for 3 months, Banishment forever, etc.', max_length=500, null=True, verbose_name='Penalty'),
        ),
        migrations.AlterField(
            model_name='decyzja',
            name='tresc',
            field=models.TextField(help_text='Enter the wording of the law as it is to be applied.', max_length=500, null=True, verbose_name='Law text'),
        ),
        migrations.AlterField(
            model_name='decyzja',
            name='uzasadnienie',
            field=models.TextField(help_text='What is the purpose of this law? Why was it created? What are we going to achieve with it? What event caused it to arise?', max_length=1500, null=True, verbose_name='Reasoning'),
        ),
        migrations.AlterField(
            model_name='decyzja',
            name='znosi',
            field=models.CharField(blank=True, help_text='If the proposed law supersedes other recipes, enter their numbers here.', max_length=500, null=True, verbose_name='Abolishes the rules'),
        ),
    ]
