from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from localflavor.generic.models import IBANField

SCHEMA = 'accounts'
DB_TABLE_PREFIX = SCHEMA + '\".\"' if SCHEMA else ''


class User(AbstractUser):
    """
    Custom user model
    """
    EURO = 0
    POUND = 1
    DOLLAR = 2
    YEN = 3
    FRANC = 4
    CROWN = 5

    CURRENCIES = (
        (EURO, 'Euro'),
        (POUND, 'Pound Sterling'),
        (DOLLAR, 'US Dollar'),
        (YEN, 'Yen'),
        (FRANC, 'Swiss Franc'),
        (CROWN, 'Swedish Crown')
    )

    first_name = models.CharField(
        max_length=30,
        blank=False,
        validators=[MinLengthValidator(1)],
        help_text="This user's first name."
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        validators=[MinLengthValidator(1)],
        help_text="This user's last name."
    )
    iban = IBANField(
        unique=True,
        help_text='IBAN code to identify this account.'
    )
    balance = models.FloatField(
        default=0,
        blank=True,
        help_text='Current amount of money in this account.'
    )
    currency = models.IntegerField(
        choices=CURRENCIES,
        default=EURO,
        help_text='Currency of this account.'
    )
    create_ts = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        help_text='Time when this account was created.'
    )
    update_ts = models.DateTimeField(
        auto_now=True,
        blank=True,
        help_text='Time when this account was last updated.'
    )

    class Meta:
        db_table = DB_TABLE_PREFIX + 'user'

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_full_name()}: {self.iban}'
