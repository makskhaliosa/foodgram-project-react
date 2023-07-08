from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'название',
        max_length=200)
    color = models.CharField(
        verbose_name='цвет',
        max_length=7,
        help_text='цветовое обозначение тэга')
    slug = models.SlugField(
        verbose_name='слаг',
        max_length=200)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'
        ordering = ('name',)


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=200)
    measurement_unit = models.CharField(
        verbose_name='единицы измерения',
        max_length=200)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)

    def __repr__(self):
        return f'{self.name} ({self.measurement_unit})'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='название блюда',
        max_length=200)
    text = models.TextField(
        verbose_name='описание',
        help_text='текст рецепта')
    cooking_time = models.PositiveIntegerField(
        verbose_name='время приготовления',
        help_text='время приготовления в минутах')
    image = models.ImageField(
        verbose_name='изображение',
        upload_to='recipes/',
        help_text='фото блюда')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='recipes')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='ингредиенты',
        help_text='продукты для приготовления блюда по рецепту')
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        related_name='recipes',
        verbose_name='тэг',
        help_text='укажите, к какому типу относится блюдо')
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.CheckConstraint(
                check=models.Q(cooking_time__gte=1),
                name='cooking_time_is_more_than_zero'),
        ]

    def __repr__(self):
        return f'{self.name} | {self.author}'

    def __str__(self):
        return f'{self.name} | {self.author}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe_set')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe_set')
    ingredient_amount = models.PositiveIntegerField(
        verbose_name='количество',
        default=1)

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'ингредиенты в рецепте'
        constraints = [
            models.CheckConstraint(
                check=models.Q(ingredient_amount__gte=1),
                name='ingredient_amount_is_more_than_zero'),
        ]


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_recipe_set')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tag_recipe_set')

    class Meta:
        verbose_name = 'тэг в рецепте'
        verbose_name_plural = 'тэги в рецепте'

    def __repr__(self):
        return f'{self.tag.name} | {self.recipe.name}'

    def __str__(self):
        return f'{self.tag.name} | {self.recipe.name}'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='подписчик',
        related_name='favorites')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='избранное',
        related_name='favorites')

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'

    def __repr__(self):
        return (f'Пользователь {self.user.username} - '
                f'Рецепт {self.recipe.name}')

    def __str__(self):
        return (f'Пользователь {self.user.username} - '
                f'Рецепт {self.recipe.name}')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
        related_name='shopping_cart')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='избранное',
        related_name='shopping_cart')

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'

    def __repr__(self):
        return (f'Пользователь {self.user.username} - '
                f'Рецепт {self.recipe.name}')

    def __str__(self):
        return (f'Пользователь {self.person.username} - '
                f'Рецепт {self.recipe.name}')


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='подписчик',
        related_name='subscriptions')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='followers')

    class Meta:
        verbose_name = 'подписки'
        verbose_name_plural = 'подписки'

    def __repr__(self):
        return (f'Подписчик {self.user.username} - '
                f'Автор {self.author.username}')

    def __str__(self):
        return (f'Подписчик {self.user.username} - '
                f'Автор {self.author.username}')
