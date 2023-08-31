from enum import unique
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(unique=True, null=False)
    # email = models.EmailField(_('email address'), unique=True)
    REQUIRED_FIELDS = ['username']  # removes email from REQUIRED_FIELDS
