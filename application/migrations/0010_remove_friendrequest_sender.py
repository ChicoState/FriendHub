# Generated by Django 4.1.4 on 2023-10-01 01:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0009_alter_friendrequest_unique_together_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friendrequest',
            name='sender',
        ),
    ]