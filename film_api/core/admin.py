from django.contrib import admin

from . import models

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email"),
            },
        ),
    )
