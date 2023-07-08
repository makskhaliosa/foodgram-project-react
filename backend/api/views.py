from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from users.models import User
from contents.models import Tag, Ingredient, Recipe, Subscriptions
from .serializers import (
    UserSerializer, SetPasswordSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer, FavoriteSerializer,
    ShoppingCartSerializer, SubscriptionSerializer)
from .filters import IngredientFilter, RecipeFilter
from .core.utils import save_shopping_list
from .permissions import (
    IsAuthorAdminOrReadOnly, IsNewUserAuthorAdminOrReadOnly, IsAuthorOrAdmin)
from .pagination import LimitPageNumberPagination


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователей."""
    serializer_class = UserSerializer
    permission_classes = (IsNewUserAuthorAdminOrReadOnly,)
    search_fields = ('username', 'email')
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        subscribed = Count(
            'followers', filter=Q(
                followers__user__username=self.request.user.get_username()))
        queryset = User.objects.annotate(is_subscribed=subscribed)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    @action(
        methods=['get', 'patch'], detail=False, url_path='me',
        permission_classes=(IsAuthorOrAdmin,))
    def users_me(self, request, *args, **kwargs):
        """Конечная точка для получения информации о текущем пользователе."""
        user = request.user
        context = {'user': user}
        if request.method == 'GET':
            serializer = UserSerializer(user, context=context)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            instance=user,
            data=request.data,
            context=context,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'], detail=False, url_path='set_password',
        permission_classes=(IsAuthorOrAdmin,))
    def set_password(self, request, *args, **kwargs):
        """Конечная точка для смены пароля пользователя."""
        user = User.objects.get(username=request.user.get_username())
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
        user = get_object_or_404(User, username=request.user.get_username())
        author = get_object_or_404(User, id=kwargs['pk'])
        recipes_limit = self.request.query_params.get('recipes_limit')
        if request.method == 'POST':
            data = {
                'user': user,
                'author': author,
                'recipes_limit': recipes_limit
            }
            serializer = SubscriptionSerializer(
                data=data, context=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, author=author)
            return Response(
                data=serializer.data, status=status.HTTP_201_CREATED)
        subscription = user.subscriptions.filter(author=author)
        if not subscription.exists():
            return Response(data={
                "error": "Вы не подписаны на автора!"},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='subscriptions',
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request, *args, **kwargs):
        """
        Конечная точка для получения авторов, на которых подписан пользователь.
        """
        user = request.user
        recipes_limit = self.request.query_params.get('recipes_limit')
        subscribed = Count(
            'user', filter=Q(user__username=user.get_username()))
        recipes_count = Count('author__recipes')
        queryset = Subscriptions.objects.filter(
            user=user).prefetch_related(
                'author__recipes').annotate(
                    is_subscribed=subscribed,
                    recipes_count=recipes_count
                ).order_by('author__username')
        page = self.paginate_queryset(queryset)
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
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorAdminOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        username = self.request.user.get_username()
        favorited = Count('favorites', filter=Q(
            favorites__user__username=username))
        shopping_cart = Count('shopping_cart', filter=Q(
            shopping_cart__user__username=username))
        queryset = Recipe.objects.annotate(
            is_favorited=favorited, is_in_shopping_cart=shopping_cart)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        """Конечная точка для добавления и удаления рецептов из избранного."""
        recipe_id = kwargs.get('pk')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, username=request.user.get_username())
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
        favorite = user.favorites.filter(recipe=recipe)
        if not favorite.exists():
            return Response(
                data={"error": "Рецепта нет в избранном!"},
                status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart',
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        """
        Конечная точка для добавления и удаления рецептов из списка покупок.
        """
        recipe_id = kwargs.get('pk')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, username=request.user.get_username())
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
        recipe_in_cart = user.shopping_cart.filter(recipe=recipe)
        if not recipe_in_cart.exists():
            return Response(
                data={"error": "Рецепта нет в списке покупок!"},
                status=status.HTTP_400_BAD_REQUEST)
        recipe_in_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        """Конечная точка для скачивания списка покупок."""
        user = get_object_or_404(User, username=request.user.get_username())
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
        # В документации джанго пишут, что с FileREsponse закрывать открытый
        # файл не нужно, так как он закроется автоматически
        # https://docs.djangoproject.com/en/4.2/ref/request-response/#fileresponse-objects:~:text=The%20file%20will%20be%20closed%20automatically%2C%20so%20don%E2%80%99t%20open%20it%20with%20a%20context%20manager.
        # Все-таки надо делать с with?
