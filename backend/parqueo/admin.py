from django.contrib import admin

from .models import Ingreso, Tarifa, TipoVehiculo


@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ("tipo_vehiculo", "monto_hora", "monto_minimo", "vigente_desde")
    list_filter = ("tipo_vehiculo",)
    autocomplete_fields = ["tipo_vehiculo"]


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ("placa", "tipo_vehiculo", "estado", "hora_ingreso", "hora_salida", "monto_cobrado")
    list_filter = ("estado", "tipo_vehiculo", "empresa")
    search_fields = ("placa",)
    autocomplete_fields = ["tipo_vehiculo", "empresa"]
    readonly_fields = ("hora_salida", "horas_cobradas", "monto_cobrado", "tarifa_aplicada", "cobrado_por")
