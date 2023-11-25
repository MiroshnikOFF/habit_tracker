from django.contrib import admin

from habits.models import Place, Action, Habit


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description',)


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description',)


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('pk', 'owner', 'action', 'time_to_perform', 'place',)
