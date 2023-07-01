# Generated by Django 4.2.2 on 2023-06-14 19:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0014_alter_ingredient_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='Автор публикации',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='Время приготовления',
            new_name='cooking_time',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='Изображение',
            new_name='image',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='Ингредиенты',
            new_name='ingredients',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='В избранном',
            new_name='is_favorited',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='В списке покупок',
            new_name='is_in_shopping_cart',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='Название блюда',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='Дата публикации',
            new_name='pub_date',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='Тэг',
            new_name='tags',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='Описание',
            new_name='text',
        ),
    ]
