# Generated by Django 3.1.12 on 2021-10-15 19:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0019_messagehistory_messagehistoryentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=255)),
                ('filename', models.CharField(max_length=255)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='chat.message')),
            ],
        ),
    ]
