# Generated by Django 3.0.8 on 2020-07-26 16:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('client_app', '0002_auto_20200726_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='storage',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
