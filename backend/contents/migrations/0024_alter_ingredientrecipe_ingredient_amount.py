# Generated by Django 4.2.2 on 2023-06-22 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0023_alter_tag_color_alter_tag_name_alter_tag_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='ingredient_amount',
            field=models.PositiveIntegerField(default=1, verbose_name='Количество'),
        ),
    ]