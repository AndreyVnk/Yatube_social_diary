# Generated by Django 2.2.16 on 2022-01-30 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0016_auto_20220129_1304'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='user_cant_subscribe_yourself',
        ),
    ]