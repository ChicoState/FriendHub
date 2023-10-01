# Generated by Django 4.1.4 on 2023-10-01 02:55

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('application', '0021_alter_friendrequest_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='friendrequest',
            unique_together={('sender', 'receiver')},
        ),
    ]