# Generated by Django 4.2.2 on 2023-06-14 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='В подписках',
            new_name='is_subscribed',
        ),
    ]

    replaces = [
        ('users', '0005_rename_в_подписках_user_is_subscribed'),
    ]