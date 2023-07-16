import re
import base64
import uuid

from django.shortcuts import get_object_or_404
from django.contrib.auth import password_validation
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from users.models import User
from contents.models import (
    Tag, Ingredient, Recipe, IngredientRecipe, Favorites,
    Subscriptions, ShoppingCart)
from .core.utils import (
    get_tag_and_create_related, get_ingredient_and_create_related,
    filter_ingredients_and_create_related, filter_tags_and_create_related)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации и получения информации о пользователе."""
    is_subscribed = serializers.SerializerMethodField(default=False)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed']
        read_only_fields = ('id', 'is_subscribed')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        username = data['username']
        prog = re.compile(r'^[\w.@+-]+\Z', re.ASCII)
        result = prog.match(username)
        if not result:
            raise serializers.ValidationError(
                'Введи корректное имя пользователя. Можно использовать '
                'только латинские буквы, цифры и символы "@/./+/-/_" .')
        if username == 'me':
            raise serializers.ValidationError(
                'Придумай другое имя пользователя, это уже занято.')
        return data

    def validate_password(self, value):
        """Хэширует пароль пользователя."""
        password_validation.validate_password(value, User)
        prog = re.compile(r'^[\w.@+!?-]+\Z', re.ASCII)
        result = prog.match(value)
        if not result:
            raise serializers.ValidationError(
                'Придумайте другой пароль! Можно использовать '
                'только латинские буквы, цифры и символы "@/./+/-/_/!/?" .')
        return make_password(value)

    def get_is_subscribed(self, obj):
        if hasattr(obj, 'is_subscribed'):
            return bool(obj.is_subscribed)
        request_user = self.context['user']
        if request_user.is_authenticated:
            user = get_object_or_404(
                User, username=request_user.get_username())
            return user.subscriptions.filter(author=obj).exists()


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    current_password = serializers.CharField(
        max_length=150, write_only=True, required=True)
    new_password = serializers.CharField(
        max_length=150, write_only=True, required=True)

    def validate_current_password(self, value):
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Введен неверный пароль! Попробуйте снова.')
        return value

    def validate_new_password(self, value):
        user = self.context['user']
        password_validation.validate_password(value, user)
        prog = re.compile(r'^[\w.@+!?-]+\Z', re.ASCII)
        result = prog.match(value)
        if not result:
            raise serializers.ValidationError(
                'Придумайте другой пароль! Можно использовать '
                'только латинские буквы, цифры и символы "@/./+/-/_/!/?" .')
        return value

    def save(self, **kwargs):
        new_password = self.validated_data['new_password']
        user = self.context['user']
        user.set_password(new_password)
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('name', 'color', 'slug')

    def to_internal_value(self, data):
        if not isinstance(data, int):
            raise serializers.ValidationError('Введи id тэга.')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для игредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода количества ингредиентов в рецепте."""
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField(source='ingredient_amount')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для сохранения картинок."""
    def to_internal_value(self, value):
        if isinstance(value, str) and value.startswith('data:image'):
            form, image = value.split(';base64,')
            extension = form.split('/')[-1]
            filename = str(uuid.uuid4())
            complete_filename = filename + 'temp.' + extension
            value = ContentFile(
                base64.b64decode(image), name=complete_filename)
        return super().to_internal_value(value)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов с дополнительными полями."""
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault())
    ingredients = IngredientRecipeSerializer(
        source='ingredient_recipe_set',
        many=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(allow_null=True, required=False)
    is_favorited = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'text', 'author', 'ingredients', 'tags',
            'cooking_time', 'is_favorited', 'is_in_shopping_cart')

    def validate(self, data):
        if not self.initial_data.get('ingredients'):
            raise serializers.ValidationError(
                {'Ingredients': 'Рецепт не может быть без ингредиентов.'})
        if not self.initial_data.get('tags'):
            raise serializers.ValidationError(
                {'Tags': 'Добавь тэги для рецепта.'})
        return data

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше либо равно 1 минуте.'
            )
        return value

    def get_is_favorited(self, obj):
        if hasattr(obj, 'is_favorited'):
            return bool(obj.is_favorited)
        user = self.context['user']
        if user.is_authenticated:
            user = get_object_or_404(
                User, username=user.username)
            return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        if hasattr(obj, 'is_in_shopping_cart'):
            return bool(obj.is_in_shopping_cart)
        user = self.context['user']
        if user.is_authenticated:
            user = get_object_or_404(
                User, username=user.username)
            return obj.shopping_cart.filter(user=user).exists()

    def create(self, validated_data):
        ingredients = self.initial_data.get('ingredients')
        validated_data.pop('ingredient_recipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        get_ingredient_and_create_related(ingredients, recipe)
        get_tag_and_create_related(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = self.initial_data.get('ingredients')
        validated_data.pop('ingredient_recipe_set')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        filter_ingredients_and_create_related(instance, ingredients)
        filter_tags_and_create_related(instance, tags)
        return instance


class RelatedRecipeSerializer(serializers.Serializer):
    """
    Поля для отображения рецептов в сериализаторах
    Избранного и Списка покупок.
    """
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.CharField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Поля для отображения рецептов в сериализаторе Подписок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(RelatedRecipeSerializer, serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в избранное."""

    class Meta:
        model = Favorites
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context['user']
        recipe = self.context['recipe']
        if user.favorites.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное!')
        return data


class ShoppingCartSerializer(RelatedRecipeSerializer,
                             serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в список покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context['user']
        recipe = self.context['recipe']
        if user.shopping_cart.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок!')
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на пользователя."""
    id = serializers.IntegerField(source='author.id', read_only=True)
    email = serializers.CharField(source='author.email', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(
        source='author.first_name', read_only=True)
    last_name = serializers.CharField(
        source='author.last_name', read_only=True)
    is_subscribed = serializers.SerializerMethodField(default=False)
    recipes_count = serializers.SerializerMethodField(default=0)
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Subscriptions
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes_count', 'recipes')

    def validate(self, data):
        user = self.context['user']
        author = self.context['author']
        if user.username == author.username:
            raise serializers.ValidationError('Нельзя подписаться на себя!')
        if user.subscriptions.filter(author=author).exists():
            raise serializers.ValidationError('Вы уже подписаны на автора!')
        return data

    def get_is_subscribed(self, obj):
        """Сообщает, подписан ли пользователь на автора."""
        if hasattr(obj, 'is_subscribed'):
            return bool(obj.is_subscribed)
        request_user = self.context['user']
        if request_user.is_authenticated:
            user = get_object_or_404(User, username=request_user.username)
            return user.subscriptions.filter(author=obj.author).exists()
        return False

    def get_recipes_count(self, obj):
        """Считает количество рецептов в подписках."""
        if hasattr(obj, 'recipes_count'):
            return obj.recipes_count
        return obj.author.recipes.count()

    def get_recipes(self, obj):
        """Возвращает список рецептов автора."""
        output = []
        for recipe in obj.author.recipes.all():
            serializer = ShortRecipeSerializer(recipe, context=self.context)
            output.append(serializer.data)
        recipes_limit = self.context['recipes_limit']
        if recipes_limit:
            try:
                if int(recipes_limit) < 0:
                    raise serializers.ValidationError(
                        'Укажите целое неотрицательное число.')
                output = output[:int(recipes_limit)]
            except ValueError:
                raise serializers.ValidationError(
                    'Укажите целое число рецептов.')
        return output
