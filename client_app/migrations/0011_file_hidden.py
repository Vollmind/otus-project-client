# Generated by Django 3.0.8 on 2020-08-01 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_app', '0010_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]
