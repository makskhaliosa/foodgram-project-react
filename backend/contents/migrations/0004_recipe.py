# Generated by Django 4.2.2 on 2023-06-12 13:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contents', '0003_ingredient'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Название блюда', models.CharField(max_length=250, verbose_name='Название блюда')),
                ('Описание', models.TextField(help_text='Текст рецепта', verbose_name='Описание')),
                ('Время приготовления', models.IntegerField(help_text='Время приготовления в минутах', verbose_name='Время приготовления')),
                ('Изображение', models.ImageField(help_text='Фото блюда', upload_to='recipes/', verbose_name='Изображение')),
                ('В избранном', models.BooleanField(blank=True, null=True, verbose_name='В избранном')),
                ('В списке покупок', models.BooleanField(blank=True, null=True, verbose_name='В списке покупок')),
                ('Автор публикации', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
        ),
    ]
