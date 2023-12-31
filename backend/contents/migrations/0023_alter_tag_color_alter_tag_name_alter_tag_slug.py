# Generated by Django 4.2.2 on 2023-06-19 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0022_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(help_text='Цветовое обозначение тэга', max_length=50, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=250, verbose_name='Слаг'),
        ),
    ]
