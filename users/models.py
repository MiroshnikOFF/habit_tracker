from django.contrib.auth.models import AbstractUser
from django.db import models

from habits.models import NULLABLE


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name='email')
    telegram_chat_id = models.IntegerField(unique=True, **NULLABLE, verbose_name='telegram chat_id')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('pk',)

