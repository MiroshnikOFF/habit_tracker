from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from habits.models import Place, Action, Habit
from habits.paginators import HabitPaginator, PlacePaginator, ActionPaginator
from habits.permissions import IsOwnerOrStaff
from habits.serializers import PlaceSerializer, ActionSerializer, HabitSerializer
from habits.services import set_schedule, delete_schedule


class PlaceViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    pagination_class = PlacePaginator


class ActionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    pagination_class = ActionPaginator


class HabitCreateAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = HabitSerializer

    def perform_create(self, serializer, **kwargs):
        """
        Сохраняет авторизованного пользователя в объекте привычки,
        создает периодическую задачу если привычка не является приятной.
        """

        new_habit = serializer.save()
        new_habit.owner = self.request.user
        new_habit.save()

        set_schedule(habit=new_habit)


class HabitListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = HabitSerializer
    pagination_class = HabitPaginator

    def get_queryset(self):
        """ Получает только привычки владельца. """

        queryset = Habit.objects.filter(owner=self.request.user)
        return queryset


class HabitPublicListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    pagination_class = HabitPaginator


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrStaff,)
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    

class HabitUpdateAPIView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrStaff,)
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def perform_update(self, serializer):
        """ Удаляет и создает периодическую задачу с новыми данными. """

        habit = serializer.save()
        delete_schedule(habit_pk=habit.pk)
        set_schedule(habit=habit)


class HabitDestroyAPIView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrStaff,)
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def perform_destroy(self, instance):
        """ Удаляет периодическую задачу. """

        delete_schedule(habit_pk=instance.pk)
        super().perform_destroy(instance)
