from django.db import models

from config import settings

NULLABLE = {'null': True, 'blank': True}


class Place(models.Model):
    name = models.CharField(max_length=150, verbose_name='название')
    description = models.TextField(**NULLABLE, verbose_name='описание')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'место'
        verbose_name_plural = 'места'
        ordering = ('pk',)


class Action(models.Model):
    name = models.CharField(max_length=150, verbose_name='название')
    description = models.TextField(**NULLABLE, verbose_name='описание')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'действие'
        verbose_name_plural = 'действия'
        ordering = ('pk',)


class Habit(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, related_name='habit',
                              verbose_name='создатель')
    place = models.ForeignKey(Place, on_delete=models.PROTECT, related_name='habit', verbose_name='место')
    time_to_perform = models.DateTimeField(auto_now_add=True, verbose_name='время и дата, когда необходимо выполнять')
    action = models.ForeignKey(Action, on_delete=models.PROTECT, related_name='habit', verbose_name='действие')
    is_pleasure = models.BooleanField(default=False, verbose_name='признак приятной привычки')
    pleasure_habit = models.ForeignKey('self', on_delete=models.PROTECT, **NULLABLE, verbose_name='приятная привычка')
    periodicity = models.PositiveSmallIntegerField(default=1, verbose_name='периодичность в днях')
    reward = models.CharField(max_length=150, **NULLABLE, verbose_name='вознаграждение')
    execution_time = models.PositiveSmallIntegerField(default=60, verbose_name='время на выполнение в секундах')
    is_public = models.BooleanField(default=False, verbose_name='признак публичности')

    def __str__(self):
        return f'{self.action}'

    class Meta:
        verbose_name = 'привычка'
        verbose_name_plural = 'привычки'
        ordering = ('pk',)


