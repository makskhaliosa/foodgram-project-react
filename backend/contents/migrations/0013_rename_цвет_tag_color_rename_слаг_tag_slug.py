# Generated by Django 4.2.2 on 2023-06-14 19:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0012_alter_tag_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='Цвет',
            new_name='color',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='Слаг',
            new_name='slug',
        ),
    ]
