# Generated by Django 4.2.2 on 2023-07-01 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0030_remove_recipe_is_favorited_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(help_text='Фото блюда', upload_to='recipes/', verbose_name='Изображение'),
        ),
    ]