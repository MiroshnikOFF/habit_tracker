from rest_framework.serializers import ValidationError

from habits.models import Habit


class RewardValidator:
    """
    Исключает создание привычки без связанной с ней привычки или вознаграждения если привычка не является приятной,
    исключает одновременный выбор связанной привычки и вознаграждения.
    """

    def __init__(self, fields_list):
        self.fields = fields_list

    def __call__(self, value):
        print(value)
        if not value.get('is_pleasure'):
            if not value.get(self.fields[0]) and not value.get(self.fields[1]):
                raise ValidationError("У привычки должно быть вознаграждение или связанная привычка!")
            elif self.fields[0] in value and self.fields[1] in value:
                raise ValidationError("у привычки не может быть одновременно вознаграждения и связанной привычки!")


class TimeToCompleteValidator:
    """ Исключает время выполнения привычки больше чем 120 секунд. """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if self.field in value and value.get(self.field) > 120:
            raise ValidationError("Время выполнения должно быть не больше 120 секунд!")


class PleasureHabitValidator:
    """ Исключает добавление связанной привычки без признака приятной привычки. """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if value.get(self.field):
            habit_pk = dict(value).get(self.field).pk
            habit = Habit.objects.get(pk=habit_pk)
            if not habit.is_pleasure:
                raise ValidationError(
                    "В связанные привычки могут попадать только привычки с признаком приятной привычки!")


class IsPleasureValidator:
    """ Исключает добавление вознаграждения или связанной привычки к приятной привычке. """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if value.get(self.field):
            if 'pleasure_habit' in value or 'reward' in value:
                raise ValidationError("У приятной привычки не может быть вознаграждения или связанной привычки!")


class PeriodicityValidator:
    """ Исключает установку периодичности выполнения привычки реже чем 1 раз в 7 дней. """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if self.field in value and value.get(self.field) > 7:
            raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней!")


def patch_validator(habit, validated_data):
    """
    Исключает изменение полезной привычки на приятную если у нее есть вознаграждение или привязанная привычка,
    исключает добавление привязанной привычки к полезной привычке если у нее уже есть вознаграждение,
    исключает добавление вознаграждения к полезной привычке если у нее уже есть привязанная привычка.
    """

    if 'is_pleasure' in validated_data:
        if habit.reward or habit.pleasure_habit:
            raise ValidationError(
                "У привычки есть вознаграждение или связанная привычка, поэтому она не может быть приятной!")
    if habit.reward and validated_data.get('pleasure_habit'):
        raise ValidationError("У привычки есть вознаграждение, у нее не может быть связанной привычки!")
    if habit.pleasure_habit and validated_data.get('reward'):
        raise ValidationError("У привычки есть связанная привычка, у нее не может быть вознаграждения!")
