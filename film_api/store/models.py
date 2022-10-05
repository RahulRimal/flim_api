
from uuid import uuid4
from django.db import models

from django.conf import settings

from django.core.validators import MinValueValidator

from .validators import validate_file_size

# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def email(self):
        return self.user.email

    def username(self):
        return self.user.username

    def __str__(self) -> str:
        return f"{self.user.id} => {self.user.first_name} {self.user.last_name}"


class Category(models.Model):
    name: models.CharField(max_length=255)
    featured_equipment = models.ForeignKey(
        'Equipment', on_delete=models.SET_NULL, null=True,  blank=True, related_name='+')

    def __str__(self) -> str:
        return self.name


class Equipment(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    # price = models.DecimalField(
    #     max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    company = models.CharField(max_length=255)
    siteDelivery = models.BooleanField(default=False)
    freeDeliver = models.BooleanField(default=False)
    featured_image = models.ForeignKey(
        'EquipmentImage', on_delete=models.PROTECT, related_name='+')
    last_update = models.DateTimeField(auto_now=True)
    # technical_specs:


class TechnicalSpecification(models.Model):
    specification = models.CharField(max_length=255)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)


class EquipmentImage(models.Model):
    image = models.ImageField(upload_to='store/images',
                              validators=[validate_file_size])
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)])
