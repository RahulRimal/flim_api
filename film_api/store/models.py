
from uuid import uuid4
from django.db import models

from django.conf import settings

from django.core.validators import MinValueValidator

from .validators import validate_file_size

# Create your models here.


class Customer(models.Model):
    # user = models.OneToOneField(
    #     settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

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
    name = models.CharField(max_length=255)
    featured_equipment = models.ForeignKey(
        'Equipment', on_delete=models.SET_NULL, null=True,  blank=True, related_name='+')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Equipment(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    # price = models.OneToOneField(EquipmentPrice, on_delete=models.PROTECT)
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    site_delivery = models.BooleanField(default=False)
    free_delivery = models.BooleanField(default=False)
    featured_image = models.ImageField(upload_to='equipment/images',
                                       validators=[validate_file_size])
    last_update = models.DateTimeField(auto_now=True)
    # technical_specs:

    def __str__(self) -> str:
        return self.name


class EquipmentPrice(models.Model):
    price_1_day = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(1)])
    price_2_to_4_days = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(1)])
    price_5_to_7_days = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(1)])
    price_8_and_more_days = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(1)])

    equipment = models.OneToOneField(
        Equipment, on_delete=models.CASCADE, related_name='price')


class TechnicalSpecification(models.Model):
    specification = models.CharField(max_length=255)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)


class EquipmentImage(models.Model):
    image = models.ImageField(upload_to='equipment/images',
                              validators=[validate_file_size])
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name='images')


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)])
    tenure = models.CharField(max_length=255)
    location = models.CharField(max_length=255)


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    full_payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    booking_payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    # class Meta:
    #     permissions = [
    #         ('cancel_order', 'Can cancel order')
    #     ]


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='items')
    equipment = models.ForeignKey(
        Equipment, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    tenure = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
