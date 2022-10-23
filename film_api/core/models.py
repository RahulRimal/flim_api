from enum import unique
from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(unique=True, null=False)
    # email = models.EmailField(('email address'), unique=True)
    REQUIRED_FIELDS = []  # removes email from REQUIRED_FIELDS
