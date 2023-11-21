from django.urls import path
from rest_framework import routers

from habits.apps import HabitsConfig
from habits.views import PlaceViewSet, ActionViewSet, HabitListAPIView, HabitCreateAPIView, HabitRetrieveAPIView, \
    HabitUpdateAPIView, HabitDestroyAPIView, HabitPublicListAPIView

app_name = HabitsConfig.name

router = routers.DefaultRouter()
router.register('places', PlaceViewSet, basename='places')
router.register('actions', ActionViewSet, basename='actions')

urlpatterns = [
    path('', HabitListAPIView.as_view(), name='habit_list'),
    path('public/', HabitPublicListAPIView.as_view(), name='habit_public_list'),
    path('create/', HabitCreateAPIView.as_view(), name='habits_list'),
    path('<int:pk>/', HabitRetrieveAPIView.as_view(), name='habit'),
    path('<int:pk>/update/', HabitUpdateAPIView.as_view(), name='habit_update'),
    path('<int:pk>/delete/', HabitDestroyAPIView.as_view(), name='habit_delete'),
] + router.urls
