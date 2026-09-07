from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "nombre_completo", "is_active", "is_staff")
    search_fields = ("email", "nombre_completo")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informacion personal", {"fields": ("nombre_completo",)}),
        (
            "Permisos tecnicos (Django admin)",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nombre_completo", "password1", "password2"),
            },
        ),
    )
