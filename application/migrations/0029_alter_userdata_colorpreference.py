# Generated by Django 4.2.5 on 2023-10-11 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0028_userdata_colorpreference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='colorPreference',
            field=models.CharField(default=1, max_length=10),
        ),
    ]