from django.contrib import admin

from . import models

# Register your models here.


class AddressAdminInline(admin.TabularInline):
    # list_display = ['city', 'street', 'zipcode']
    model = models.Address
    max_num = 1


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'username']
    search_fields = ['first_name']
    inlines = [AddressAdminInline]


class EquipmentImageInline(admin.TabularInline):
    # min_num = 1
    max_num = 5
    model = models.EquipmentImage


class EquipmentPriceInline(admin.TabularInline):
    min_num = 4
    max_num = 4
    model = models.EquipmentPrice


class TechnicalSpecificationInline(admin.TabularInline):
    # class TechnicalSpecificationInline(admin.StackedInline):
    model = models.TechnicalSpecification
    min_num = 4
    # max_num = 4
    extra = 0


@admin.register(models.Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'inventory',
                    'category', 'company', 'site_delivery', 'free_delivery', 'last_update']
    prepopulated_fields = {'slug': ['name']}
    inlines = [EquipmentPriceInline,
               TechnicalSpecificationInline, EquipmentImageInline]
    search_fields = ['name']


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


# @admin.register(models.EquipmentImage)
# class EquipmentImageAdmin(admin.ModelAdmin):
#     list_display = ['image']

class BillinfInfoInline(admin.StackedInline):
    model = models.BillingInfo
    min_num = 1
    max_num = 1
    extra = 0
    readonly_fields = ['first_name', 'last_name',
                       'email', 'phone', 'convenient_location', 'side_note']


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['equipment']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0
    readonly_fields = ['equipment', 'quantity', 'tenure', 'location']


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [BillinfInfoInline, OrderItemInline]
    list_display = ['id', 'placed_at', 'customer',
                    'booking_payment_status', 'full_payment_status']
    readonly_fields = ['customer']
