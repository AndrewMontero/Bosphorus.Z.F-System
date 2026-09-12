from rest_framework import serializers

from .models import Ingreso, Tarifa, TipoVehiculo


class TipoVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoVehiculo
        fields = ["id", "nombre", "activo"]


class TarifaSerializer(serializers.ModelSerializer):
    tipo_vehiculo_nombre = serializers.CharField(source="tipo_vehiculo.nombre", read_only=True)

    class Meta:
        model = Tarifa
        fields = [
            "id", "tipo_vehiculo", "tipo_vehiculo_nombre",
            "monto_hora", "monto_minimo", "vigente_desde",
        ]


class IngresoSerializer(serializers.ModelSerializer):
    tipo_vehiculo_nombre = serializers.CharField(source="tipo_vehiculo.nombre", read_only=True)
    segundos_dentro = serializers.IntegerField(read_only=True)
    registrado_por_nombre = serializers.CharField(
        source="registrado_por.nombre_completo", read_only=True, default=None
    )

    class Meta:
        model = Ingreso
        fields = [
            "id", "empresa", "placa", "tipo_vehiculo", "tipo_vehiculo_nombre",
            "hora_ingreso", "hora_salida", "segundos_dentro",
            "horas_cobradas", "monto_cobrado", "estado",
            "registrado_por_nombre",
        ]
        read_only_fields = [
            "hora_ingreso", "hora_salida", "horas_cobradas",
            "monto_cobrado", "estado",
        ]

    def validate_placa(self, valor):
        placa = valor.strip().upper().replace(" ", "")
        if not placa:
            raise serializers.ValidationError("La placa es obligatoria.")
        return placa
