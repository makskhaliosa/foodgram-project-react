import os
import uuid

from django.shortcuts import get_object_or_404
from django.conf import settings
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4

from contents.models import (
    Tag, Ingredient, TagRecipe, IngredientRecipe, Recipe)

FILE_DIR = os.path.join(settings.BASE_DIR.parent, 'backend_media/media/files')


def get_tag_and_create_related(tags: dict, instance: Recipe):
    """
    Проверяет наличие объекта из входящего списка в базе.
    Если объект существует, создаем связь с рецептом.
    """
    for tag_id in tags:
        # tag_slug = tag.get('slug')
        tag_object = get_object_or_404(Tag, id=tag_id)
        TagRecipe.objects.get_or_create(tag=tag_object, recipe=instance)


def get_ingredient_and_create_related(ingredients: dict, instance: Recipe):
    """
    Проверяет наличие объекта из входящего списка в базе.
    Если объект существует, создаем связь с рецептом.
    """
    for ingredient in ingredients:
        ingredient_id = ingredient.get('id')
        ingredient_object = get_object_or_404(
            Ingredient, id=ingredient_id)
        IngredientRecipe.objects.get_or_create(
            ingredient=ingredient_object,
            recipe=instance,
            ingredient_amount=ingredient.get('amount'))


def filter_ingredients_and_create_related(instance, new_set):
    """
    Сравнивает элементы в существуещем списке ингредиентов в рецепте
    с входящим списком. Если объект существует, обновляем информацию
    о нем. Если ингредиента нет во входящем списке, удаляем его из
    существующего списка ингредиентов.
    """
    queryset = instance.ingredient_recipe_set
    ids_to_keep = []
    for ingredient in new_set:
        ingredient_id = ingredient.get('id')
        ingredient_amount = ingredient.get('amount')
        queryset_object = queryset.filter(ingredient__id=ingredient_id)
        if not queryset_object.exists():
            ingredient_object = get_object_or_404(Ingredient, id=ingredient_id)
            queryset.create(
                ingredient=ingredient_object,
                ingredient_amount=ingredient_amount
            )
            ids_to_keep.append(ingredient_id)
        else:
            instance_set = queryset_object.get()
            instance_set.ingredient_amount = ingredient_amount
            instance_set.save()
            ids_to_keep.append(ingredient_id)
    queryset.exclude(
        ingredient__id__in=ids_to_keep
    ).delete()


def filter_tags_and_create_related(instance, new_set):
    """
    Сравнивает элементы в существуещем списке тэгов в рецепте
    с входящим списком. Если объект существует, обновляет информацию
    о нем. Если тэга нет во входящем списке, удаляет его из
    существующего списка тэгов.
    """
    queryset = instance.tag_recipe_set
    ids_to_keep = []
    for tag_id in new_set:
        queryset_object = queryset.filter(tag__id=tag_id)
        if not queryset_object.exists():
            tag_object = get_object_or_404(Tag, id=tag_id)
            queryset.create(tag=tag_object)
            ids_to_keep.append(tag_id)
        else:
            ids_to_keep.append(tag_id)
    queryset.exclude(
        tag__id__in=ids_to_keep
    ).delete()
    """
    count_tags = len(new_set)
    for tag_set in queryset:
        tag_found = False
        if count_tags == 0:
            queryset.filter(
                tag__id=tag_set.tag.id).delete()
            count_tags = len(new_set)
        for tag_id in new_set:
            if tag_found:
                break
            if tag_id == tag_set.tag.id:
                del new_set[len(new_set) - count_tags]
                tag_found = True
                count_tags -= 1
            else:
                count_tags -= 1
    return new_set"""


def save_shopping_list(author, shopping_list):
    """Сохраняет список покупок в формате .txt."""
    if not os.path.exists(FILE_DIR):
        os.makedirs(FILE_DIR)
    filename = str(uuid.uuid4())
    extension = 'txt'
    full_name = os.path.join(FILE_DIR, f'shop_list{filename}.{extension}')
    with open(full_name, 'w', encoding='utf-8') as file_obj:
        header = f'Список покупок для пользователя {author.username}\n\n'
        file_obj.write(header.upper())
        count = 1
        for key, value in shopping_list.items():
            file_obj.write(
                f'{count}. {key} - {value["amount"]} '
                f'({value["measurement_unit"]})\n\n')
            count += 1
    return full_name


def save_shopping_list_to_pdf(shopping_list):
    filename = str(uuid.uuid4())
    extension = 'pdf'
    full_text = b''
    canvas = Canvas(f'{filename}.{extension}', pagesize=A4)
    count = 1
    for key, value in shopping_list.items():
        text = (bytes(f'{count}. {key} - {value["amount"]} '
                f'({value["measurement_unit"]})\n\n', encoding='utf-8'))
        full_text += text
        count += 1
    canvas.drawString(78, 78, full_text)
    canvas.showPage()
    canvas.save()
    return f'{filename}.{extension}'


def get_recipes_queryset(queryset, exclude=False):
    """
    Получает список id объектов во входящем queryset
    и возвращает новый queryset из модели рецептов.
    """
    recipes_ids = [recipe_set.recipe.id for recipe_set in queryset]
    if exclude:
        return Recipe.objects.exclude(id__in=recipes_ids)
    return Recipe.objects.filter(id__in=recipes_ids)
