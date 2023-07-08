from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(
        verbose_name='имя пользователя',
        max_length=150,
        blank=False)
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=150,
        blank=False)
    email = models.EmailField(
        verbose_name='электронная почта',
        max_length=254,
        blank=False,
        unique=True)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['first_name']

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
