import shutil
import tempfile
import base64
from http import HTTPStatus

from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from django.core.files.base import ContentFile
from rest_framework.authtoken.models import Token

from contents.models import (
    Recipe, Ingredient, Tag, TagRecipe, IngredientRecipe)

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ApiURLsTests(TestCase):
    """Тестирует доступность страниц."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user_one = User.objects.create_user(
            username='testuser1', email='example1@mail.ru')
        cls.user_two = User.objects.create_user(
            username='testuser2', email='example2@mail.ru')
        cls.user_one_token = Token.objects.create(user=cls.user_one)
        cls.user_two_token = Token.objects.create(user=cls.user_two)
        cls.authorized_client_one = Client()
        cls.authorized_client_two = Client()
        cls.authorized_client_one.force_login(cls.user_one)
        cls.authorized_client_two.force_login(cls.user_two)
        cls.test_image = (
            'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//'
            '8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='
        )
        cls.image_file = ContentFile(
            base64.b64decode(cls.test_image), name='test_image.png')
        cls.tag = Tag.objects.create(
            name='tag_name',
            slug='tag_slug'
        )
        cls.ingredient = Ingredient.objects.create(
            name='ingredient_name',
            measurement_unit='ingredient_measure'
        )
        cls.recipe = Recipe.objects.create(
            name='recipe_name',
            text='recipe_text',
            cooking_time=15,
            image=cls.image_file,
            author=cls.user_one
        )
        TagRecipe.objects.create(
            tag=cls.tag,
            recipe=cls.recipe
        )
        IngredientRecipe.objects.create(
            ingredient=cls.ingredient,
            recipe=cls.recipe
        )
        cls.recipes_url = reverse('api:recipe-list')
        cls.recipe_detail_url = reverse(
            'api:recipe-detail', args=(cls.recipe.id,))
        cls.tags_url = reverse('api:tag-list')
        cls.tag_detail_url = reverse('api:tag-detail', args=(cls.tag.id,))
        cls.ingredients_url = reverse('api:ingredient-list')
        cls.ingredient_detail_url = reverse(
            'api:ingredient-detail', args=(cls.ingredient.id,))
        cls.users_url = reverse('api:user-list')
        cls.user_detail_url = reverse(
            'api:user-detail', args=(cls.user_one.id,))
        cls.user_profile_url = reverse('api:user-me')
        cls.user_subscriptions = reverse('api:user-subscriptions')
        cls.user_shopping_cart = reverse('api:recipe-download-shopping-cart')

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_url_exists_at_desired_location(self):
        """
        Тестирует доступность адресов для неавторизованных пользователей.
        """
        unexisting_page = reverse('api:recipe-detail', args=('0000',))
        pages_for_all_users = {
            self.recipes_url: HTTPStatus.OK,
            self.recipe_detail_url: HTTPStatus.OK,
            self.tags_url: HTTPStatus.OK,
            self.tag_detail_url: HTTPStatus.OK,
            self.ingredients_url: HTTPStatus.OK,
            self.ingredient_detail_url: HTTPStatus.OK,
            self.users_url: HTTPStatus.OK,
            self.user_detail_url: HTTPStatus.OK,
            unexisting_page: HTTPStatus.NOT_FOUND
        }
        for address, status in pages_for_all_users.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code, status,
                    f'Что-то не так с адресом {address}'
                )

    def test_url_available_for_authorized_users(self):
        """
        Тестирует доступность адресов для авторизованных
        пользователей по токену.
        """
        pages_for_auth_users = {
            self.user_profile_url: HTTPStatus.OK,
            self.user_shopping_cart: HTTPStatus.OK,
            self.user_subscriptions: HTTPStatus.OK
        }
        headers = {'Authorization': f'Token {self.user_one_token.key}'}
        for address, status in pages_for_auth_users.items():
            with self.subTest(address=address):
                response = self.authorized_client_one.get(
                    address, headers=headers)
                self.assertEqual(
                    response.status_code, status,
                    f'Адрес {address} недоступен.'
                )
