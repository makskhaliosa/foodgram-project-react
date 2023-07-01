from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=100)
    color = models.CharField(
        verbose_name='Цвет',
        max_length=50,
        help_text='Цветовое обозначение тэга')
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=250)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=250)
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=20)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __repr__(self):
        return f'{self.name} ({self.measurement_unit})'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название блюда',
        max_length=200)
    text = models.TextField(
        verbose_name='Описание',
        help_text='Текст рецепта')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления в минутах')
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        help_text='Фото блюда')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Продукты для приготовления блюда по рецепту')
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        related_name='recipes',
        verbose_name='Тэг',
        help_text='Укажите, к какому типу относится блюдо')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

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
        verbose_name='Количество',
        default=1)

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


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
        verbose_name = 'Тэг в рецепте'
        verbose_name_plural = 'Тэги в рецепте'

    def __repr__(self):
        return f'{self.tag.name} | {self.recipe.name}'

    def __str__(self):
        return f'{self.tag.name} | {self.recipe.name}'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='favorites')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранное',
        related_name='favorites')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

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
        verbose_name='Пользователь',
        related_name='shopping_cart')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранное',
        related_name='shopping_cart')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

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
        verbose_name='Подписчик',
        related_name='subscriptions')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='followers')

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __repr__(self):
        return (f'Подписчик {self.user.username} - '
                f'Автор {self.author.username}')

    def __str__(self):
        return (f'Подписчик {self.user.username} - '
                f'Автор {self.author.username}')
