# Generated by Django 4.2.2 on 2023-06-14 19:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0011_rename_название_tag_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',), 'verbose_name': 'Тэг', 'verbose_name_plural': 'Тэги'},
        ),
    ]
