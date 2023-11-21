from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User


class UserTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            email='test@test.ru',
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        self.user.set_password('0000')
        self.user.save()
        self.access_token = str(AccessToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_create_user(self):
        """ Тестирование создания пользователя """
        data = {'email': 'newtest@test.ru', 'password': '0000'}
        response = self.client.post('/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('email'), data.get('email'))
        self.assertTrue(User.objects.filter(pk=response.json().get('pk')).exists())

    def test_list_user(self):
        """ Тестирование получения списка пользователей """
        users = list(User.objects.all())
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), len(users))
        self.assertEqual(response.json()[0]['pk'], users[0].pk)

    def test_retrieve_user(self):
        """ Тестирование получения пользователя """
        response = self.client.get(f'/users/{self.user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('pk'), self.user.pk)
        self.assertEqual(response.json().get('email'), self.user.email)

    def test_update_user(self):
        """ Тестирование изменения пользователя """
        data = {'first_name': 'test', 'last_name': 'test'}
        response = self.client.patch(f'/users/{self.user.pk}/update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('first_name'), data.get('first_name'))
        self.assertEqual(response.json().get('last_name'), data.get('last_name'))

    def test_delete_user(self):
        """ Тестирование удаления пользователя """
        response = self.client.delete(f'/users/{self.user.pk}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

