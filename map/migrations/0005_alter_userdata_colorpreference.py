# Generated by Django 4.1.4 on 2023-11-13 19:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0004_alter_userdata_colorpreference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='colorPreference',
            field=models.CharField(default='#0035fe', max_length=7, validators=[django.core.validators.MinLengthValidator(7, 'invalid submit')]),
        ),
    ]
