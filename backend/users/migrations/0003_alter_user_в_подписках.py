# Generated by Django 4.2.2 on 2023-06-12 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_в_подписках'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='В подписках',
            field=models.BooleanField(blank=True, null=True, verbose_name='В подписках'),
        ),
    ]
