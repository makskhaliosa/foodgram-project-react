# Generated by Django 4.2.2 on 2023-06-24 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0026_rename_fan_favorites_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shoppingcart',
            old_name='person',
            new_name='user',
        ),
    ]
