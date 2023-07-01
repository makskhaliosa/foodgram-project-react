# Generated by Django 4.2.2 on 2023-06-14 19:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0013_rename_цвет_tag_color_rename_слаг_tag_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='Единицы измерения',
            new_name='measurement_unit',
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='Название',
            new_name='name',
        ),
    ]
