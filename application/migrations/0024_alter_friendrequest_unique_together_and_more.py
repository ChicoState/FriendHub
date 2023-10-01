# Generated by Django 4.1.4 on 2023-10-01 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0023_remove_friendrequest_isactive'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='friendrequest',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='friendrequest',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='friendrequest',
            name='sender',
        ),
        migrations.AddField(
            model_name='userdata',
            name='friends',
            field=models.ManyToManyField(blank=True, to='application.userdata'),
        ),
        migrations.DeleteModel(
            name='FriendList',
        ),
        migrations.DeleteModel(
            name='FriendRequest',
        ),
    ]
