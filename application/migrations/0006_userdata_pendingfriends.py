# Generated by Django 4.1.4 on 2023-10-01 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0005_alter_userdata_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='pendingFriends',
            field=models.ManyToManyField(blank=True, related_name='pending_requests', to='application.userdata'),
        ),
    ]
