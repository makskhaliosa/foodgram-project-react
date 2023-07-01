from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User
from contents.models import Tag, Ingredient, Recipe
from .serializers import (
    UserSerializer, SetPasswordSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer, FavoriteSerializer,
    ShoppingCartSerializer, SubscriptionSerializer)
from .filters import IngredientFilter, RecipeFilter
from .core.utils import save_shopping_list
from .permissions import IsAuthorAdminOrReadOnly, IsAuthorOrAdmin
from .pagination import LimitPageNumberPagination


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователей."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthorAdminOrReadOnly,)
    search_fields = ('username', 'email')
    pagination_class = LimitPageNumberPagination

    def get_serializer_context(self):
        return {'user': self.request.user}

    @action(
        methods=['get', 'patch'], detail=False, url_path='me',
        permission_classes=(IsAuthorOrAdmin,))
    def users_me(self, request, *args, **kwargs):
        """Конечная точка для получения информации о текущем пользователе."""
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            instance=request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'], detail=False, url_path='set_password',
        permission_classes=(IsAuthorOrAdmin,))
    def set_password(self, request, *args, **kwargs):
        """Конечная точка для смены пароля пользователя."""
        user = User.objects.get(username=request.user.username)
        serializer = SetPasswordSerializer(
            instance=user,
            data=request.data,
            context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        """Конечная точка для создания и удаления подписки на автора."""
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, id=kwargs['pk'])
        if request.method == 'POST':
            data = {
                'user': user,
                'author': author
            }
            serializer = SubscriptionSerializer(
                data=data, context=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, author=author)
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED)
        if not user.subscriptions.filter(author=author).exists():
            return Response(data={
                "error": "Вы не подписаны на автора!"},
                status=status.HTTP_400_BAD_REQUEST)
        user.subscriptions.filter(author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='subscriptions',
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request, *args, **kwargs):
        """
        Конечная точка для получения авторов, на которых подписан пользователь.
        """
        recipes_limit = self.request.query_params.get('recipes_limit')
        user = get_object_or_404(User, username=request.user.username)
        subscriptions = user.subscriptions.all()
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            page,
            context={'user': user, 'recipes_limit': recipes_limit},
            many=True)
        return self.get_paginated_response(serializer.data)


class ListRetrieveViewSet(ListModelMixin, RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """Кастомный вьюсет для получения объектов списком и отдельно."""
    pass


class TagViewSet(ListRetrieveViewSet):
    """Вьюсет для тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(ListRetrieveViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorAdminOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_context(self):
        return {'user': self.request.user}

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        """Конечная точка для добавления и удаления рецептов из избранного."""
        recipe_id = kwargs.get('pk')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'POST':
            new_data = {
                'user': user,
                'recipe': recipe
            }
            serializer = FavoriteSerializer(data=new_data, context=new_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED)
        if not user.favorites.filter(recipe=recipe).exists():
            return Response(
                data={"error": "Рецепта нет в избранном!"},
                status=status.HTTP_400_BAD_REQUEST)
        user.favorites.filter(recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart',
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        """
        Конечная точка для добавления и удаления рецептов из списка покупок.
        """
        recipe_id = kwargs.get('pk')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'POST':
            new_data = {
                'user': user,
                'recipe': recipe
            }
            serializer = ShoppingCartSerializer(
                data=request.data, context=new_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED)
        if not user.shopping_cart.filter(recipe=recipe).exists():
            return Response(
                data={"error": "Рецепта нет в списке покупок!"},
                status=status.HTTP_400_BAD_REQUEST)
        user.shopping_cart.filter(recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        """Конечная точка для скачивания списка покупок."""
        user = get_object_or_404(User, username=request.user.username)
        shoping_cart = user.shopping_cart.all()
        ingredient_list = {}
        for shopping_item in shoping_cart:
            recipe = shopping_item.recipe
            ingredient_recipe_set = recipe.ingredient_recipe_set.all()
            for item in ingredient_recipe_set:
                name = item.ingredient.name
                measure = item.ingredient.measurement_unit
                amount = item.ingredient_amount
                if name in ingredient_list:
                    ingredient_list[name]['amount'] += amount
                else:
                    ingredient_list[name] = {
                        'amount': amount,
                        'measurement_unit': measure
                    }
        saved_file = save_shopping_list(user, ingredient_list)
        return FileResponse(open(saved_file, 'rb'), as_attachment=True)
