from django.contrib import admin

from .models import Asignacion, BitacoraPermisos, Permiso, Rol, RolPermiso


class RolPermisoInline(admin.TabularInline):
    model = RolPermiso
    extra = 1
    autocomplete_fields = ["permiso"]


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descripcion", "dominio")
    list_filter = ("dominio",)
    search_fields = ("codigo", "descripcion")


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("nombre", "es_superadmin", "pantalla_inicio")
    list_filter = ("es_superadmin",)
    search_fields = ("nombre",)
    inlines = [RolPermisoInline]
    exclude = ["permisos"]


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol", "empresa", "finca", "activa", "asignado_por", "asignado_en")
    list_filter = ("rol", "activa", "empresa")
    search_fields = ("usuario__email", "usuario__nombre_completo")
    autocomplete_fields = ["usuario", "rol", "empresa", "finca", "bodega", "punto_venta", "asignado_por"]
    readonly_fields = ["asignado_en"]


@admin.register(BitacoraPermisos)
class BitacoraPermisosAdmin(admin.ModelAdmin):
    list_display = ("realizado_en", "accion", "usuario_afectado", "rol", "realizado_por", "es_autoasignacion")
    list_filter = ("accion", "es_autoasignacion")
    search_fields = ("usuario_afectado__email",)
    readonly_fields = [f.name for f in BitacoraPermisos._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
