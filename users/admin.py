from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserCreateForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreateForm
    list_display = ('username', 'role', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_active')
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Роль и права', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Даты', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'is_staff', 'is_superuser'),
        }),
    )
