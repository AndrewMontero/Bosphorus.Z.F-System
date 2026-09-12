from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from autorizacion.permissions import TienePermiso

from .models import Ingreso, Tarifa, TipoVehiculo
from .serializers import IngresoSerializer, TarifaSerializer, TipoVehiculoSerializer


class TipoVehiculoViewSet(viewsets.ModelViewSet):
    queryset = TipoVehiculo.objects.all()
    serializer_class = TipoVehiculoSerializer

    def get_permissions(self):
        codigo = "parqueo:leer" if self.action in ("list", "retrieve") else "parqueo:mantener"
        return [TienePermiso.para(codigo)()]


class TarifaViewSet(viewsets.ModelViewSet):
    queryset = Tarifa.objects.select_related("tipo_vehiculo")
    serializer_class = TarifaSerializer

    def get_permissions(self):
        codigo = "parqueo:leer" if self.action in ("list", "retrieve") else "parqueo:mantener"
        return [TienePermiso.para(codigo)()]


class IngresoViewSet(viewsets.ModelViewSet):
    serializer_class = IngresoSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = Ingreso.objects.select_related("tipo_vehiculo", "registrado_por")
        estado = self.request.query_params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            codigo = "parqueo:leer"
        elif self.action == "cobrar":
            codigo = "parqueo:cobrar"
        else:
            codigo = "parqueo:registrar_ingreso"
        return [TienePermiso.para(codigo)()]

    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)

    @action(detail=True, methods=["post"])
    def cobrar(self, request, pk=None):
        ingreso = self.get_object()
        try:
            ingreso.cobrar(usuario=request.user)
        except DjangoValidationError as e:
            return Response(
                {"detalle": e.messages}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(self.get_serializer(ingreso).data)
