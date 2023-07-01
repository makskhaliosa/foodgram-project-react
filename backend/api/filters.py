from enum import Enum

import django_filters
from django.shortcuts import get_object_or_404

from contents.models import Ingredient, Recipe, Tag
from users.models import User
from .core.utils import get_recipes_queryset


class Boolean_choices(Enum):
    FALSE = '0'
    TRUE = '1'


ENUM_CHOICES = (
    (Boolean_choices.FALSE.value, 'False'),
    (Boolean_choices.TRUE.value, 'True')
)


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для ингридиентов."""

    class Meta:
        model = Ingredient
        fields = {
            'name': ['istartswith', 'icontains'],
        }


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов."""
    author = django_filters.NumberFilter(
        field_name='author__id',
        label='Автор')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='Тэги',
        queryset=Tag.objects.all())
    is_favorited = django_filters.ChoiceFilter(
        choices=ENUM_CHOICES,
        label='Избранное',
        method='filter_is_favorited')
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=ENUM_CHOICES,
        label='В списке покупок',
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Метод для фильтрации по избранному."""
        if self.request is None:
            return Recipe.objects.none()
        if value == Boolean_choices.TRUE.value:
            user = get_object_or_404(
                User, username=self.request.user.username)
            favorites = user.favorites.all()
            return get_recipes_queryset(favorites)
        if value == Boolean_choices.FALSE.value:
            return Recipe.objects.all()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Метод для фильтрации по списку покупок."""
        if self.request is None:
            return Recipe.objects.none()
        if value == Boolean_choices.TRUE.value:
            user = get_object_or_404(
                User, username=self.request.user.username)
            shopping_cart = user.shopping_cart.all()
            return get_recipes_queryset(shopping_cart)
        if value == Boolean_choices.FALSE.value:
            return Recipe.objects.all()

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
