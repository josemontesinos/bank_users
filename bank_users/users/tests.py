import logging
from datetime import datetime, timezone, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from freezegun import freeze_time

from users.models import User


logging.disable(logging.CRITICAL)


class BaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IBANS = (
            'ES9121000418450200051332',
            'DE89370400440532013000',
            'FR1420041010050500013M02606'
        )
        cls.USER_DATA = {
            'username': 'test_username',
            'password': 'test_password',
            'first_name': 'Test_Name',
            'last_name': 'Test Lastname',
            'email': 'test@email.com',
            'iban': cls.IBANS[0],
            'balance': 1000,
            'currency': User.DOLLAR,
        }
        cls.NOW = datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        cls.REQUIRED_FIELDS = ('username', 'password', 'first_name', 'last_name', 'iban')
        cls.REQUIRED_DATA = {key: cls.USER_DATA[key] for key in cls.REQUIRED_FIELDS}
        cls.SECOND_USER_REQUIRED_DATA = {
            **{key: cls.USER_DATA[key] + '2' for key in cls.REQUIRED_FIELDS if key != 'iban'},
            **{'iban': cls.IBANS[1]}}
        cls.previous_users_pks = get_user_model().objects.values_list('pk', flat=True)
        cls.user_queryset = get_user_model().objects.exclude(pk__in=list(cls.previous_users_pks))

    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        del self.client


class UserModelTestCase(BaseTestCase):

    def tearDown(self):
        self.user_queryset.delete()
        self.assertEqual(get_user_model().objects.count(), len(self.previous_users_pks))

    def test_user_creation_with_default_values(self):
        self.assertEqual(self.user_queryset.count(), 0)
        with freeze_time(self.NOW):
            user = get_user_model().objects.create(**self.REQUIRED_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        self.assertIsInstance(user, get_user_model())
        for attr in self.REQUIRED_FIELDS:
            self.assertEqual(getattr(user, attr), self.USER_DATA[attr])
        self.assertEqual(user.email, '')
        self.assertEqual(user.balance, 0)
        self.assertEqual(user.currency, get_user_model().EURO)
        self.assertEqual(user.create_ts, self.NOW)
        self.assertEqual(user.update_ts, self.NOW)

    def test_user_creation_with_specific_values(self):
        self.assertEqual(self.user_queryset.count(), 0)
        with freeze_time(self.NOW):
            user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        self.assertIsInstance(user, get_user_model())
        for attr in self.USER_DATA:
            self.assertEqual(getattr(user, attr), self.USER_DATA[attr])
        self.assertEqual(user.create_ts, self.NOW)
        self.assertEqual(user.update_ts, self.NOW)

    def test_username_requirement(self):
        user_data = {**self.REQUIRED_DATA}
        user_data.pop('username')
        self.assertNotIn('username', user_data)
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_empty_username(self):
        user_data = {**self.REQUIRED_DATA, **{'username': ''}}
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_repeated_username(self):
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        with self.assertRaises(ValidationError):
            user = get_user_model()(**{**self.SECOND_USER_REQUIRED_DATA, **{'username': user.username}})
            user.full_clean()

    def test_password_requirement(self):
        user_data = {**self.REQUIRED_DATA}
        user_data.pop('password')
        self.assertNotIn('password', user_data)
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_empty_password(self):
        user_data = {**self.REQUIRED_DATA, **{'password': ''}}
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_repeated_password(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        new_user = get_user_model().objects.create(**{**self.SECOND_USER_REQUIRED_DATA, **{'password': user.password}})
        self.assertEqual(self.user_queryset.count(), 2)
        self.assertEqual(user.password, new_user.password)

    def test_fist_name_requirement(self):
        user_data = {**self.REQUIRED_DATA}
        user_data.pop('first_name')
        self.assertNotIn('first_name', user_data)
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_empty_first_name(self):
        user_data = {**self.REQUIRED_DATA, **{'first_name': ''}}
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_repeated_first_name(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        new_user = get_user_model().objects.create(
            **{**self.SECOND_USER_REQUIRED_DATA, **{'first_name': user.first_name}}
        )
        self.assertEqual(self.user_queryset.count(), 2)
        self.assertEqual(user.first_name, new_user.first_name)

    def test_last_name_requirement(self):
        user_data = {**self.REQUIRED_DATA}
        user_data.pop('last_name')
        self.assertNotIn('last_name', user_data)
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_empty_last_name(self):
        user_data = {**self.REQUIRED_DATA, **{'last_name': ''}}
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_repeated_last_name(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        new_user = get_user_model().objects.create(
            **{**self.SECOND_USER_REQUIRED_DATA, **{'last_name': user.last_name}}
        )
        self.assertEqual(self.user_queryset.count(), 2)
        self.assertEqual(user.last_name, new_user.last_name)

    def test_iban_requirement(self):
        user_data = {**self.REQUIRED_DATA}
        user_data.pop('iban')
        self.assertNotIn('iban', user_data)
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_empty_iban(self):
        user_data = {**self.REQUIRED_DATA, **{'iban': ''}}
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_repeated_iban(self):
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        with self.assertRaises(ValidationError):
            user = get_user_model()(**{**self.SECOND_USER_REQUIRED_DATA, **{'iban': user.iban}})
            user.full_clean()

    def test_iban_validation(self):
        user_data = {**self.REQUIRED_DATA, **{'iban': 'This is a wrong IBAN'}}
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_currency_validation(self):
        invalid_currency = max(currency[0] for currency in get_user_model().CURRENCIES) + 1
        user_data = {**self.REQUIRED_DATA, **{'currency': invalid_currency}}
        with self.assertRaises(ValidationError):
            user = get_user_model()(**user_data)
            user.full_clean()

    def test_representation(self):
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(str(user), f'{user.first_name} {user.last_name}: {user.iban}')


class CreateUserAPIEndpointTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.URL = reverse('user-list')

    def tearDown(self):
        self.user_queryset.delete()
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_default_values(self):
        self.assertEqual(self.user_queryset.count(), 0)
        with freeze_time(self.NOW):
            response = self.client.post(self.URL, data=self.REQUIRED_DATA, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user_queryset.count(), 1)
        for field in self.REQUIRED_FIELDS:
            if field == 'password':
                self.assertTrue(self.user_queryset.get().password)
            else:
                self.assertEqual(response.data[field], self.USER_DATA[field])
        self.assertEqual(response.data['balance'], 0)
        self.assertEqual(response.data['currency'], get_user_model().CURRENCIES[0][1])
        self.assertEqual(response.data['create_ts'], self.NOW.isoformat().replace('+00:00', 'Z'))
        self.assertEqual(response.data['update_ts'], self.NOW.isoformat().replace('+00:00', 'Z'))

    def test_create_user_with_specific_values(self):
        self.assertEqual(self.user_queryset.count(), 0)
        with freeze_time(self.NOW):
            response = self.client.post(self.URL, data=self.USER_DATA, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user_queryset.count(), 1)
        user = self.user_queryset.get()
        for field in self.USER_DATA:
            if field == 'password':
                self.assertTrue(user.password)
            elif field == 'currency':
                self.assertEqual(response.data['currency'], get_user_model().CURRENCIES[2][1])
            elif field in ('create_ts', 'update_ts'):
                self.assertEqual(response.data[field], self.NOW.isoformat().replace('+00:00', 'Z'))
            else:
                self.assertEqual(response.data[field], self.USER_DATA[field])

    def test_create_user_with_empty_body(self):
        self.assertEqual(self.user_queryset.count(), 0)
        response = self.client.post(self.URL)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_no_username(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA}
        user_data.pop('username')
        self.assertNotIn('username', user_data)
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_empty_username(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA, **{'username': ''}}
        self.assertEqual(user_data['username'], '')
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_repeated_username(self):
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'username': user.username}}
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 1)
        
    def test_create_user_with_no_password(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA}
        user_data.pop('password')
        self.assertNotIn('password', user_data)
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_empty_password(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA, **{'password': ''}}
        self.assertEqual(user_data['password'], '')
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_repeated_password(self):
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'password': user.password}}
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user_queryset.count(), 2)
        
    def test_create_user_with_no_first_name(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA}
        user_data.pop('first_name')
        self.assertNotIn('first_name', user_data)
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_empty_first_name(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA, **{'first_name': ''}}
        self.assertEqual(user_data['first_name'], '')
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_repeated_first_name(self):
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'first_name': user.first_name}}
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user_queryset.count(), 2)
        
    def test_create_user_with_no_last_name(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA}
        user_data.pop('last_name')
        self.assertNotIn('last_name', user_data)
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_empty_last_name(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA, **{'last_name': ''}}
        self.assertEqual(user_data['last_name'], '')
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_repeated_last_name(self):
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'last_name': user.last_name}}
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user_queryset.count(), 2)

    def test_create_user_with_no_iban(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA}
        user_data.pop('iban')
        self.assertNotIn('iban', user_data)
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_empty_iban(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA, **{'iban': ''}}
        self.assertEqual(user_data['iban'], '')
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_create_user_with_repeated_iban(self):
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'iban': user.iban}}
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 1)

    def test_create_user_with_invalid_iban(self):
        invalid_iban = 'This is a wrong IBAN'
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.USER_DATA, **{'iban': invalid_iban}}
        self.assertEqual(user_data['iban'], invalid_iban)
        response = self.client.post(self.URL, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 0)


class ListUserAPIEndpointTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.URL = reverse('user-list')

    def test_get_user_list(self):
        with freeze_time(self.NOW):
            users = (
                get_user_model().objects.create(**self.REQUIRED_DATA),
                get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA),
            )
        self.assertEqual(self.user_queryset.count(), len(users))
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(users))
        for index in range(len(response.data)):
            self.assertNotIn('password', response.data[index])
            for field in response.data[index]:
                if field == 'currency':
                    self.assertEqual(users[index].get_currency_display(), response.data[index][field])
                elif field in ('create_ts', 'update_ts'):
                    self.assertEqual(response.data[index][field], self.NOW.isoformat().replace('+00:00', 'Z'))
                else:
                    self.assertEqual(getattr(users[index], field), response.data[index][field])

    def test_get_empty_user_list(self):
        self.assertEqual(self.user_queryset.count(), 0)
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


class RetrieveUserAPIEndpointTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        with freeze_time(self.NOW):
            self.user = get_user_model().objects.create(**self.REQUIRED_DATA)
        self.assertEqual(self.user_queryset.count(), 1)

    def tearDown(self):
        self.user_queryset.delete()
        self.assertEqual(self.user_queryset.count(), 0)

    def test_retrieve_user(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('password', response.data)
        for field in response.data:
            if field == 'currency':
                self.assertEqual(self.user.get_currency_display(), response.data['currency'])
            elif field in ('create_ts', 'update_ts'):
                self.assertEqual(response.data[field], self.NOW.isoformat().replace('+00:00', 'Z'))
            else:
                self.assertEqual(getattr(self.user, field), response.data[field])

    def test_retrieve_unexisting_user(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk + 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class DeleteUserAPIEndpointTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        with freeze_time(self.NOW):
            self.user = get_user_model().objects.create(**self.REQUIRED_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        self.url = reverse('user-detail', kwargs={'pk': self.user.pk})

    def tearDown(self):
        self.user_queryset.delete()
        self.assertEqual(self.user_queryset.count(), 0)

    def test_delete_user(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_delete_unexisting_user(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk + 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.user_queryset.count(), 1)


class UpdateUserAPIEndpointTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        with freeze_time(self.NOW):
            self.user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        self.url = reverse('user-detail', kwargs={'pk': self.user.pk})

    def tearDown(self):
        self.user_queryset.delete()
        self.assertEqual(self.user_queryset.count(), 0)

    def check_user_did_not_change(self):
        user = self.user_queryset.get(pk=self.user.pk)
        for field in set(self.SECOND_USER_REQUIRED_DATA).difference({'password'}):
            self.assertEqual(getattr(user, field), self.USER_DATA[field])
        self.assertEqual(user.create_ts, user.update_ts)

    def test_update_user(self):
        now_but_later = self.NOW + timedelta(days=1)
        with freeze_time(now_but_later):
            response = self.client.put(self.url, data=self.SECOND_USER_REQUIRED_DATA, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_queryset.count(), 1)
        self.assertNotIn('password', response.data)
        user = self.user_queryset.last()
        for field in set(self.SECOND_USER_REQUIRED_DATA).difference({'password'}):
            self.assertEqual(response.data[field], self.SECOND_USER_REQUIRED_DATA[field])
            self.assertEqual(getattr(user, field), self.SECOND_USER_REQUIRED_DATA[field])
            self.assertNotEqual(response.data[field], self.USER_DATA[field])
        self.assertEqual(response.data['balance'], self.USER_DATA['balance'])
        self.assertEqual(response.data['currency'], get_user_model().CURRENCIES[2][1])
        self.assertEqual(response.data['create_ts'], self.NOW.isoformat().replace('+00:00', 'Z'))
        self.assertEqual(response.data['update_ts'], (now_but_later.isoformat().replace('+00:00', 'Z')))
        self.assertNotEqual(self.user.password, user.password)
        self.assertNotEqual(user.create_ts, user.update_ts)

    def test_update_unexisting_user(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk + 1})
        response = self.client.put(url, data=self.SECOND_USER_REQUIRED_DATA, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.user_queryset.count(), 1)
        self.assertNotIn('password', response.data)
        self.check_user_did_not_change()

    def test_update_user_with_empty_body(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.put(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user_queryset.count(), 1)
        self.check_user_did_not_change()

    def test_update_user_with_no_username(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA}
        user_data.pop('username')
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_update_user_with_empty_username(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'username': ''}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_update_user_with_repeated_username(self):
        second_user = get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA)
        user_data = {**self.USER_DATA, **{'username': second_user.username}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()
        
    def test_update_user_with_no_password(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA}
        user_data.pop('password')
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_update_user_with_empty_password(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'password': ''}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_update_user_with_repeated_password(self):
        second_user = get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA)
        user_data = {**self.USER_DATA, **{'password': second_user.password}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.user.password, self.user_queryset.get(pk=self.user.pk).password)
        
    def test_update_user_with_no_first_name(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA}
        user_data.pop('first_name')
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_update_user_with_empty_first_name(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'first_name': ''}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_update_user_with_repeated_first_name(self):
        second_user = get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA)
        user_data = {**self.USER_DATA, **{'first_name': second_user.first_name}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.user.first_name, self.user_queryset.get(pk=self.user.pk).first_name)
        self.assertEqual(second_user.first_name, self.user_queryset.get(pk=self.user.pk).first_name)
        
    def test_update_user_with_no_last_name(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA}
        user_data.pop('last_name')
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_update_user_with_empty_last_name(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'last_name': ''}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_update_user_with_repeated_last_name(self):
        second_user = get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA)
        user_data = {**self.USER_DATA, **{'last_name': second_user.last_name}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.user.last_name, self.user_queryset.get(pk=self.user.pk).last_name)
        self.assertEqual(second_user.last_name, self.user_queryset.get(pk=self.user.pk).last_name)

    def test_update_user_with_no_iban(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA}
        user_data.pop('iban')
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_update_user_with_empty_iban(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'iban': ''}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_update_user_with_repeated_iban(self):
        second_user = get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA)
        user_data = {**self.USER_DATA, **{'iban': second_user.iban}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()
        
    def test_update_user_with_invalid_iban(self):
        invalid_iban = 'This is a wrong IBAN'
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'iban': invalid_iban}}
        response = self.client.put(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()


class PartialUpdateUserAPIEndpointTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        with freeze_time(self.NOW):
            self.user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        self.url = reverse('user-detail', kwargs={'pk': self.user.pk})

    def tearDown(self):
        self.user_queryset.delete()
        self.assertEqual(self.user_queryset.count(), 0)

    def check_user_did_not_change(self, check_ts=True):
        user = self.user_queryset.get(pk=self.user.pk)
        for field in set(self.SECOND_USER_REQUIRED_DATA).difference({'password'}):
            self.assertEqual(getattr(user, field), self.USER_DATA[field])
        if check_ts:
            self.assertEqual(user.create_ts, user.update_ts)

    def test_partial_update_user(self):
        now_but_later = self.NOW + timedelta(days=1)
        with freeze_time(now_but_later):
            response = self.client.patch(self.url, data=self.SECOND_USER_REQUIRED_DATA, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_queryset.count(), 1)
        self.assertNotIn('password', response.data)
        user = self.user_queryset.last()
        for field in set(self.SECOND_USER_REQUIRED_DATA).difference({'password'}):
            self.assertEqual(response.data[field], self.SECOND_USER_REQUIRED_DATA[field])
            self.assertEqual(getattr(user, field), self.SECOND_USER_REQUIRED_DATA[field])
            self.assertNotEqual(response.data[field], self.USER_DATA[field])
        self.assertEqual(response.data['balance'], self.USER_DATA['balance'])
        self.assertEqual(response.data['currency'], get_user_model().CURRENCIES[2][1])
        self.assertEqual(response.data['create_ts'], self.NOW.isoformat().replace('+00:00', 'Z'))
        self.assertEqual(response.data['update_ts'], (now_but_later.isoformat().replace('+00:00', 'Z')))
        self.assertNotEqual(self.user.password, user.password)
        self.assertNotEqual(user.create_ts, user.update_ts)

    def test_partial_update_unexisting_user(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk + 1})
        response = self.client.patch(url, data=self.SECOND_USER_REQUIRED_DATA, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.user_queryset.count(), 1)
        self.assertNotIn('password', response.data)
        self.check_user_did_not_change()

    def test_partial_update_user_with_empty_body(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_queryset.count(), 1)
        self.check_user_did_not_change(check_ts=False)

    def test_partial_update_user_with_no_username(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA}
        user_data.pop('username')
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        updated_user = self.user_queryset.get(pk=self.user.pk)
        self.assertEqual(self.user.username, updated_user.username)
        self.assertNotEqual(self.user.update_ts, updated_user.update_ts)

    def test_partial_update_user_with_empty_username(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'username': ''}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_partial_update_user_with_repeated_username(self):
        second_user = get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA)
        user_data = {**self.USER_DATA, **{'username': second_user.username}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_partial_update_user_with_no_password(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA}
        user_data.pop('password')
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        updated_user = self.user_queryset.get(pk=self.user.pk)
        self.assertEqual(self.user.password, updated_user.password)
        self.assertNotEqual(self.user.update_ts, updated_user.update_ts)

    def test_partial_update_user_with_empty_password(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'password': ''}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_partial_update_user_with_repeated_password(self):
        second_user = get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA)
        user_data = {**self.USER_DATA, **{'password': second_user.password}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.user.password, self.user_queryset.get(pk=self.user.pk).password)

    def test_partial_update_user_with_no_first_name(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA}
        user_data.pop('first_name')
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        updated_user = self.user_queryset.get(pk=self.user.pk)
        self.assertEqual(self.user.first_name, updated_user.first_name)
        self.assertNotEqual(self.user.update_ts, updated_user.update_ts)

    def test_partial_update_user_with_empty_first_name(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'first_name': ''}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_partial_update_user_with_repeated_first_name(self):
        second_user = get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA)
        user_data = {**self.USER_DATA, **{'first_name': second_user.first_name}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.user.first_name, self.user_queryset.get(pk=self.user.pk).first_name)
        self.assertEqual(second_user.first_name, self.user_queryset.get(pk=self.user.pk).first_name)

    def test_partial_update_user_with_no_last_name(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA}
        user_data.pop('last_name')
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        updated_user = self.user_queryset.get(pk=self.user.pk)
        self.assertEqual(self.user.last_name, updated_user.last_name)
        self.assertNotEqual(self.user.update_ts, updated_user.update_ts)

    def test_partial_update_user_with_empty_last_name(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'last_name': ''}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_partial_update_user_with_repeated_last_name(self):
        second_user = get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA)
        user_data = {**self.USER_DATA, **{'last_name': second_user.last_name}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.user.last_name, self.user_queryset.get(pk=self.user.pk).last_name)
        self.assertEqual(second_user.last_name, self.user_queryset.get(pk=self.user.pk).last_name)

    def test_partial_update_user_with_no_iban(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA}
        user_data.pop('iban')
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 200)
        updated_user = self.user_queryset.get(pk=self.user.pk)
        self.assertEqual(self.user.iban, updated_user.iban)
        self.assertNotEqual(self.user.update_ts, updated_user.update_ts)

    def test_partial_update_user_with_empty_iban(self):
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'iban': ''}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_partial_update_user_with_repeated_iban(self):
        second_user = get_user_model().objects.create(**self.SECOND_USER_REQUIRED_DATA)
        user_data = {**self.USER_DATA, **{'iban': second_user.iban}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()

    def test_partial_update_user_with_invalid_iban(self):
        invalid_iban = 'This is a wrong IBAN'
        user_data = {**self.SECOND_USER_REQUIRED_DATA, **{'iban': invalid_iban}}
        response = self.client.patch(self.url, data=user_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.check_user_did_not_change()
