# Generated by Django 4.2.2 on 2023-06-24 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0027_rename_person_shoppingcart_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscriptions',
            old_name='follower',
            new_name='user',
        ),
    ]
