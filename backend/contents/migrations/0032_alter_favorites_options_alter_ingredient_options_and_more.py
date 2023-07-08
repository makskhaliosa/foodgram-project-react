# Generated by Django 4.2.2 on 2023-07-04 19:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contents', '0031_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorites',
            options={'verbose_name': 'избранное', 'verbose_name_plural': 'избранное'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'ингредиент', 'verbose_name_plural': 'ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={'verbose_name': 'ингредиент в рецепте', 'verbose_name_plural': 'ингредиенты в рецепте'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',), 'verbose_name': 'рецепт', 'verbose_name_plural': 'рецепты'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'verbose_name': 'список покупок', 'verbose_name_plural': 'списки покупок'},
        ),
        migrations.AlterModelOptions(
            name='subscriptions',
            options={'verbose_name': 'подписки', 'verbose_name_plural': 'подписки'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',), 'verbose_name': 'тэг', 'verbose_name_plural': 'тэги'},
        ),
        migrations.AlterModelOptions(
            name='tagrecipe',
            options={'verbose_name': 'тэг в рецепте', 'verbose_name_plural': 'тэги в рецепте'},
        ),
        migrations.AlterField(
            model_name='favorites',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='contents.recipe', verbose_name='избранное'),
        ),
        migrations.AlterField(
            model_name='favorites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='подписчик'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=200, verbose_name='единицы измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=200, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='ingredient_amount',
            field=models.PositiveIntegerField(default=1, verbose_name='количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='автор'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(help_text='время приготовления в минутах', verbose_name='время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(help_text='фото блюда', upload_to='recipes/', verbose_name='изображение'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='продукты для приготовления блюда по рецепту', related_name='recipes', through='contents.IngredientRecipe', to='contents.ingredient', verbose_name='ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=200, verbose_name='название блюда'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='дата публикации'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='укажите, к какому типу относится блюдо', related_name='recipes', through='contents.TagRecipe', to='contents.tag', verbose_name='тэг'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(help_text='текст рецепта', verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='contents.recipe', verbose_name='избранное'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='пользователь'),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL, verbose_name='автор'),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='подписчик'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(help_text='цветовое обозначение тэга', max_length=7, verbose_name='цвет'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, verbose_name='слаг'),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.CheckConstraint(check=models.Q(('ingredient_amount__gte', 1)), name='ingredient_amount_is_more_than_zero'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.CheckConstraint(check=models.Q(('cooking_time__gte', 1)), name='cooking_time_is_more_than_zero'),
        ),
    ]