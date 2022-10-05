from django.contrib import admin

from . import models

# Register your models here.


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'username']


class EquipmentImageInline(admin.TabularInline):
    # min_num = 1
    max_num = 5
    model = models.EquipmentImage


@admin.register(models.Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'inventory',
                    'category', 'company', 'site_delivery', 'free_delivery', 'last_update']
    prepopulated_fields = {'slug': ['name']}
    inlines = [EquipmentImageInline]


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


# @admin.register(models.EquipmentImage)
# class EquipmentImageAdmin(admin.ModelAdmin):
#     list_display = ['image']
