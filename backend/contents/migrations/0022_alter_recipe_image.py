# Generated by Django 4.2.2 on 2023-06-19 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0021_ingredientrecipe_ingredient_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, help_text='Фото блюда', upload_to='recipes/', verbose_name='Изображение'),
        ),
    ]