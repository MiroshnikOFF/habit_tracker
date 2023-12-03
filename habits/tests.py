import pytz

from django_celery_beat.models import PeriodicTask
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from config import settings
from habits.models import Place, Action, Habit
from habits.permissions import IsOwnerOrStaff
from habits.services import set_schedule, delete_schedule
from habits.tasks import send_telegram_message
from habits.views import HabitRetrieveAPIView
from users.models import User


class HabitTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            email='test@test.ru',
            telegram_chat_id=settings.SUPERUSER_TELEGRAM_CHAT_ID,
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        self.user.set_password('0000')
        self.user.save()
        self.access_token = str(AccessToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.place = Place.objects.create(
            name='test_place',
        )

        self.action = Action.objects.create(
            name='test_action',
        )

        self.useful_habit = Habit.objects.create(
            owner=self.user,
            place=self.place,
            action=self.action,
            reward='yes'
        )

        self.pleasure_habit = Habit.objects.create(
            owner=self.user,
            place=self.place,
            action=self.action,
            is_pleasure=True
        )

    # Тестирование места
    def test_create_place(self):
        """ Тестирование создания места """
        data = {'name': 'new_test'}
        no_data = {}
        response = self.client.post('/habits/places/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], data.get('name'))
        self.assertTrue(Place.objects.filter(id=response.json()['id']).exists())
        response = self.client.post('/habits/places/', no_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'name': ['Обязательное поле.']})

    def test_list_place(self):
        """ Тестирование получения списка мест """
        places = list(Place.objects.all())
        response = self.client.get('/habits/places/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(places))
        self.assertEqual(response.json()['results'][0]['id'], places[0].pk)

    def test_retrieve_place(self):
        """ Тестирование получения места """
        response = self.client.get(f'/habits/places/{self.place.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.place.pk)
        self.assertEqual(response.json()['name'], self.place.name)

    def test_update_place(self):
        """ Тестирование изменения места """
        data = {'name': 'new_test'}
        response = self.client.put(f'/habits/places/{self.place.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data.get('name'))
        response = self.client.patch(f'/habits/places/{self.place.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data.get('name'))

    def test_delete_place(self):
        """ Тестирование удаления места """
        response = self.client.delete(f'/habits/places/{self.place.pk}')
        # Нельзя удалить место если оно связано с привычкой
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    # Тестирование действия
    def test_create_action(self):
        """ Тестирование создания действия """
        data = {'name': 'new_test'}
        no_data = {}
        response = self.client.post('/habits/actions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], data.get('name'))
        self.assertTrue(Action.objects.filter(id=response.json()['id']).exists())
        response = self.client.post('/habits/places/', no_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'name': ['Обязательное поле.']})

    def test_list_action(self):
        """ Тестирование получения списка действий """
        actions = list(Action.objects.all())
        response = self.client.get('/habits/actions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(actions))
        self.assertEqual(response.json()['results'][0]['id'], actions[0].pk)

    def test_retrieve_action(self):
        """ Тестирование получения действия """
        response = self.client.get(f'/habits/actions/{self.action.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.action.pk)
        self.assertEqual(response.json()['name'], self.action.name)

    def test_update_action(self):
        """ Тестирование изменения действия """
        data = {'name': 'new_test'}
        response = self.client.put(f'/habits/actions/{self.action.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data.get('name'))
        response = self.client.patch(f'/habits/actions/{self.action.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data.get('name'))

    def test_delete_action(self):
        """ Тестирование удаления действия """
        response = self.client.delete(f'/habits/actions/{self.action.pk}')
        # Нельзя удалить действие если оно связано с привычкой
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    # Тестирование привычки
    def test_create_habit(self):
        """ Тестирование создания привычки """
        no_data = {}
        response = self.client.post('/habits/create/', no_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'place': ['Обязательное поле.'], 'action': ['Обязательное поле.']})

        invalid_habit = {'place': self.place.pk, 'action': self.action.pk}
        response = self.client.post('/habits/create/', invalid_habit)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(),
                         {'non_field_errors': ['У привычки должно быть вознаграждение или связанная привычка!']})

        invalid_useful_habit = {'place': self.place.pk, 'action': self.action.pk, 'reward': 'yes',
                                'pleasure_habit': self.useful_habit.pk, 'periodicity': 8, 'execution_time': 130}
        response = self.client.post('/habits/create/', invalid_useful_habit)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {
            'non_field_errors': ['у привычки не может быть одновременно вознаграждения и связанной привычки!',
                                 'Время выполнения должно быть не больше 120 секунд!',
                                 'В связанные привычки могут попадать только привычки с признаком приятной привычки!',
                                 'Нельзя выполнять привычку реже, чем 1 раз в 7 дней!']})

        invalid_pleasure_habit = {'place': self.place.pk, 'action': self.action.pk, 'reward': 'yes',
                                  'pleasure_habit': self.pleasure_habit.pk, 'is_pleasure': True}
        response = self.client.post('/habits/create/', invalid_pleasure_habit)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {
            'non_field_errors': ['У приятной привычки не может быть вознаграждения или связанной привычки!']})

        valid_habit = {'place': self.place.pk, 'action': self.action.pk, 'pleasure_habit': self.pleasure_habit.pk,
                       'periodicity': 7, 'execution_time': 120}
        response = self.client.post('/habits/create/', valid_habit)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Habit.objects.filter(id=response.json().get('id')).exists())
        # Проверка автоматического создания периодической задачи для привычки при создании привычки
        self.assertTrue(PeriodicTask.objects.filter(name=response.json().get('id')).exists())


    def test_list_habit(self):
        """ Тестирование получения списка привычек """
        habits = list(Habit.objects.all())
        response = self.client.get('/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(habits))
        self.assertEqual(response.json()['results'][0]['id'], habits[0].pk)

    def test_retrieve_habit(self):
        """ Тестирование получения привычки """
        response = self.client.get(f'/habits/{self.useful_habit.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.useful_habit.pk)

    def test_update_habit(self):
        """ Тестирование изменения привычки """
        invalid_data = {'pleasure_habit': self.pleasure_habit.pk}
        response = self.client.patch(f'/habits/{self.useful_habit.pk}/update/', invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ['У привычки есть вознаграждение, у нее не может быть связанной привычки!'])

        invalid_data = {'is_pleasure': True}
        response = self.client.patch(f'/habits/{self.useful_habit.pk}/update/', invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(),
                         ['У привычки есть вознаграждение или связанная привычка, поэтому она не может быть приятной!'])

        valid_data = {'reward': 'new_reward', 'periodicity': 3, 'execution_time': 90}
        response = self.client.patch(f'/habits/{self.useful_habit.pk}/update/', valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('reward'), valid_data.get('reward'))
        self.assertEqual(response.json().get('periodicity'), valid_data.get('periodicity'))
        self.assertEqual(response.json().get('execution_time'), valid_data.get('execution_time'))

    def test_delete_habit(self):
        """ Тестирование удаление привычки """
        response = self.client.delete(f'/habits/{self.useful_habit.pk}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(pk=self.useful_habit.pk).exists())

    def test_list_public_habits(self):
        """ Тестирование получения списка публичных привычек """
        public_habits = Habit.objects.filter(is_public=True)
        response = self.client.get('/habits/public/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('count'), len(public_habits))

    def test_create_periodic_task(self):
        """ Тестирование создания периодической задачи """
        self.assertFalse(PeriodicTask.objects.filter(name=self.useful_habit.pk).exists())
        set_schedule(self.useful_habit)
        self.assertTrue(PeriodicTask.objects.filter(name=self.useful_habit.pk).exists())

    def test_delite_periodic_task(self):
        """ Тестирование удаления периодической задачи """
        set_schedule(self.useful_habit)
        self.assertTrue(PeriodicTask.objects.filter(name=self.useful_habit.pk).exists())
        delete_schedule(self.useful_habit.pk)
        self.assertFalse(PeriodicTask.objects.filter(name=self.useful_habit.pk).exists())

    def test_send_telegram_message(self):
        """ Тестирование отправки телеграмм сообщения """
        target_timezone = pytz.timezone(settings.TIME_ZONE)
        converted_datetime = self.useful_habit.time_to_perform.astimezone(target_timezone)
        kwargs = {
            'chat_id': self.useful_habit.owner.telegram_chat_id,
            'action': self.useful_habit.action.name,
            'time': str(converted_datetime.time().replace(second=0, microsecond=0)),
            'place': self.useful_habit.place.name
        }

        send_telegram_message.apply_async(kwargs=kwargs)

    # def test_has_permission_user_is_owner(self):
    #     user = self.user
    #     user.is_staff = False
    #     habit = self.useful_habit
    #     request = self.client.get(f'/habits/{habit.pk}/')
    #     request.user = user
    #     view = HabitRetrieveAPIView()
    #     view.kwargs = {'pk': habit.pk}
    #     permission = IsOwnerOrStaff()
    #
    #     self.assertTrue(permission.has_permission(request, view))




