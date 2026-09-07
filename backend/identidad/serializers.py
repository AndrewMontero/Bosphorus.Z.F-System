from django.contrib.auth import authenticate
from rest_framework import serializers

from autorizacion.services import (
    ambitos_de,
    es_superadmin,
    pantalla_inicio_de,
    permisos_efectivos,
)

from .models import Usuario


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        usuario = authenticate(
            request=self.context.get("request"),
            username=attrs["email"],
            password=attrs["password"],
        )
        # Mismo mensaje para usuario inexistente y contrasena mala: decir
        # cual de los dos fallo le confirma a un atacante que ese correo
        # existe en el sistema.
        if usuario is None:
            raise serializers.ValidationError(
                {"detalle": "Correo o contraseña incorrectos."}
            )
        if not usuario.is_active:
            raise serializers.ValidationError(
                {"detalle": "Esta cuenta está desactivada. Contactá al administrador."}
            )
        attrs["usuario"] = usuario
        return attrs


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Lo que el frontend necesita para armar el menu y decidir a donde entrar.
    Los permisos van explicitos para que la interfaz no tenga que adivinar.
    """

    permisos = serializers.SerializerMethodField()
    pantalla_inicio = serializers.SerializerMethodField()
    es_superadmin = serializers.SerializerMethodField()
    ambitos = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            "id",
            "email",
            "nombre_completo",
            "es_superadmin",
            "pantalla_inicio",
            "permisos",
            "ambitos",
        ]

    def get_permisos(self, obj):
        return sorted(permisos_efectivos(obj))

    def get_pantalla_inicio(self, obj):
        return pantalla_inicio_de(obj)

    def get_es_superadmin(self, obj):
        return es_superadmin(obj)

    def get_ambitos(self, obj):
        return ambitos_de(obj)
