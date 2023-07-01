import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from contents.models import Ingredient

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
filename = BASE_DIR / 'data/ingredients.csv'


class Command(BaseCommand):
    """Записывает данные об ингридиентах из файла csv в базу."""
    def handle(self, *args, **kwargs):
        try:
            with open(filename, 'r', encoding='utf-8') as file_obj:
                reader = csv.DictReader(
                    file_obj, fieldnames=['name', 'measure'])
                for row in reader:
                    Ingredient.objects.get_or_create(
                        name=row['name'].capitalize(),
                        measurement_unit=row['measure'])
        except Exception as err:
            raise CommandError('Ошибка при загрузке базы Ingredients', err)
        self.stdout.write(
            self.style.SUCCESS('Данные успешно записаны в базу!')
        )
