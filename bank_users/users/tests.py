import logging
from datetime import datetime, timezone

from django.db import transaction
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from freezegun import freeze_time

from users.models import User


logging.disable(logging.CRITICAL)


class UserModelTestCase(TestCase):

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
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA}
        del user_data['username']
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_empty_username(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA, **{'username': ''}}
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_repeated_username(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**{**self.SECOND_USER_REQUIRED_DATA, **{'username': user.username}})
        self.assertEqual(self.user_queryset.count(), 1)

    def test_password_requirement(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA}
        del user_data['password']
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_empty_password(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA, **{'password': ''}}
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_repeated_password(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        new_user = get_user_model().objects.create(**{**self.SECOND_USER_REQUIRED_DATA, **{'password': user.password}})
        self.assertEqual(self.user_queryset.count(), 2)
        self.assertEqual(user.password, new_user.password)

    def test_fist_name_requirement(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA}
        del user_data['first_name']
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_empty_first_name(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA, **{'first_name': ''}}
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

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
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA}
        del user_data['last_name']
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_empty_last_name(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA, **{'last_name': ''}}
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

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
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA}
        del user_data['iban']
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_empty_iban(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA, **{'iban': ''}}
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_repeated_iban(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(self.user_queryset.count(), 1)
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**{**self.SECOND_USER_REQUIRED_DATA, **{'iban': user.iban}})
        self.assertEqual(self.user_queryset.count(), 1)

    def test_iban_validation(self):
        self.assertEqual(self.user_queryset.count(), 0)
        user_data = {**self.REQUIRED_DATA, **{'iban': 'This is a wrong IBAN'}}
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_currency_validation(self):
        self.assertEqual(self.user_queryset.count(), 0)
        invalid_currency = max(currency[0] for currency in get_user_model().CURRENCIES) + 1
        user_data = {**self.REQUIRED_DATA, **{'currency': invalid_currency}}
        with transaction.atomic():
            with self.assertRaises(ValidationError):
                get_user_model().objects.create(**user_data)
        self.assertEqual(self.user_queryset.count(), 0)

    def test_representation(self):
        user = get_user_model().objects.create(**self.USER_DATA)
        self.assertEqual(str(user), f'{user.first_name} {user.last_name}: {user.iban}')

