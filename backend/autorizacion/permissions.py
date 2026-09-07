from rest_framework.permissions import BasePermission

from .services import permisos_efectivos


class TienePermiso(BasePermission):
    """
    Verificacion de permiso en el servidor, en cada peticion.

        class CrearTarima(APIView):
            permission_classes = [TienePermiso.para("tarima:crear")]

    Que el menu muestre u oculte una opcion es comodidad visual, nunca
    seguridad. Si la unica defensa es que el boton no aparece, no hay
    defensa.
    """

    codigo_requerido = None

    @classmethod
    def para(cls, codigo):
        nombre = "TienePermiso_" + codigo.replace(":", "_")
        return type(nombre, (cls,), {"codigo_requerido": codigo})

    def has_permission(self, request, view):
        usuario = getattr(request, "user", None)
        if not usuario or not usuario.is_authenticated:
            return False
        if not self.codigo_requerido:
            return False
        return self.codigo_requerido in permisos_efectivos(usuario)
