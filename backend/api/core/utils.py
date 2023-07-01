import uuid
from pathlib import Path

from django.shortcuts import get_object_or_404
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4

from contents.models import (
    Tag, Ingredient, TagRecipe, IngredientRecipe, Recipe)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
FILE_DIR = BASE_DIR / 'media/files/'


def get_tag_and_create_related(tags: dict, instance: Recipe):
    """
    Проверяет наличие объекта из входящего списка в базе.
    Если объект существует, создаем связь со связанной моделью.
    """
    for tag in tags:
        tag_slug = tag.get('slug')
        tag_object = get_object_or_404(Tag, slug=tag_slug)
        TagRecipe.objects.get_or_create(tag=tag_object, recipe=instance)


def get_ingredient_and_create_related(ingredients: dict, instance: Recipe):
    """
    Проверяет наличие объекта из входящего списка в базе.
    Если объект существует, создаем связь со связанной моделью.
    """
    for ingredient in ingredients:
        ingredient_name = ingredient.get('name')
        ingredient_object = get_object_or_404(
            Ingredient, name=ingredient_name)
        IngredientRecipe.objects.get_or_create(
            ingredient=ingredient_object, recipe=instance)


def filter_ingredients_and_renew_attrs(queryset, new_set):
    """
    Сравнивает элементы в существуещем списке объектов в рецепте
    с входящим списком. Если объект существует, обновляем информацию
    о нем и удаляем элемент из ходящего списка. Если объекта нет во входящем
    списке, удаляем его из существующего списка объектов.
    """
    count_ingredients = len(new_set)
    for ingredient_set in queryset:
        ingredient_found = False
        if count_ingredients == 0:
            queryset.filter(
                ingredient__name=ingredient_set.ingredient.name).delete()
            count_ingredients = len(new_set)
        for ingredient in new_set:
            if ingredient_found:
                break
            if ingredient.get('name') == ingredient_set.ingredient.name:
                ingredient_set.ingredient.amount = ingredient.get('amount')
                del new_set[len(new_set) - count_ingredients]
                ingredient_found = True
                count_ingredients -= 1
            else:
                count_ingredients -= 1
    return new_set


def filter_tags_and_renew_attrs(queryset, new_set):
    """
    Сравнивает элементы в существуещем списке объектов в рецепте
    с входящим списком. Если объект существует, обновляем информацию
    о нем и удаляем элемент из ходящего списка. Если объекта нет во входящем
    списке, удаляем его из существующего списка объектов.
    """
    count_tags = len(new_set)
    for tag_set in queryset:
        tag_found = False
        if count_tags == 0:
            queryset.filter(
                tag__name=tag_set.tag.name).delete()
            count_tags = len(new_set)
        for tag in new_set:
            if tag_found:
                break
            if tag.get('name') == tag_set.tag.name:
                del new_set[len(new_set) - count_tags]
                tag_found = True
                count_tags -= 1
            else:
                count_tags -= 1
    return new_set


def save_shopping_list(author, shopping_list):
    """Сохраняет список покупок в формате .txt."""
    filename = str(uuid.uuid4())
    extension = 'txt'
    full_name = FILE_DIR / f'shop_list{filename}.{extension}'
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


def get_recipes_queryset(queryset):
    """
    Получает список id объектов во входящем queryset
    и возвращает новый queryset из модели рецептов.
    """
    recipes_ids = [recipe_set.recipe.id for recipe_set in queryset]
    new_queryset = Recipe.objects.filter(id__in=recipes_ids)
    return new_queryset
