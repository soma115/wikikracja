# Generated by Django 3.1.12 on 2021-09-18 08:41

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('elibrary', '0005_auto_20210917_2341'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ebook',
            name='genre',
        ),
        migrations.AddField(
            model_name='ebook',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
