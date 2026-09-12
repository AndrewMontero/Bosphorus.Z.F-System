from django.contrib import admin

from .models import Bodega, Empresa, Finca, PuntoVenta


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "nombre_comercial", "cedula_juridica", "activa")
    search_fields = ("razon_social", "nombre_comercial", "cedula_juridica")
    list_filter = ("activa",)


@admin.register(Finca)
class FincaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "area_hectareas", "activa")
    list_filter = ("empresa", "activa")
    search_fields = ("nombre",)


@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "tipo", "activa")
    list_filter = ("empresa", "tipo", "activa")
    search_fields = ("nombre",)


@admin.register(PuntoVenta)
class PuntoVentaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "empresa", "activo")
    list_filter = ("empresa", "activo")
    search_fields = ("nombre",)
