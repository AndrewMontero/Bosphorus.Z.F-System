"""
Resuelve que puede hacer un usuario y donde aterriza al entrar.

Todo el resto del sistema pregunta aca -- ninguna vista debe recorrer
asignaciones por su cuenta.
"""

from .models import Asignacion, Permiso


def asignaciones_activas(usuario):
    if not getattr(usuario, "is_authenticated", False) or not usuario.is_active:
        return Asignacion.objects.none()
    return Asignacion.objects.filter(usuario=usuario, activa=True).select_related(
        "rol", "empresa", "finca", "bodega", "punto_venta"
    )


def permisos_efectivos(usuario):
    """Conjunto de codigos 'recurso:accion' que el usuario tiene hoy."""
    if not getattr(usuario, "is_authenticated", False) or not usuario.is_active:
        return set()
    return set(
        Permiso.objects.filter(
            roles__asignaciones__usuario=usuario,
            roles__asignaciones__activa=True,
        )
        .values_list("codigo", flat=True)
        .distinct()
    )


def es_superadmin(usuario):
    return asignaciones_activas(usuario).filter(rol__es_superadmin=True).exists()


def pantalla_inicio_de(usuario):
    """
    Donde aterriza al iniciar sesion. Es distinto de que PUEDE hacer:
    los permisos dicen que ve, la pantalla de inicio dice donde cae.
    """
    asignaciones = asignaciones_activas(usuario)
    superadmin = asignaciones.filter(rol__es_superadmin=True).first()
    if superadmin and superadmin.rol.pantalla_inicio:
        return superadmin.rol.pantalla_inicio
    primera = asignaciones.exclude(rol__pantalla_inicio="").first()
    return primera.rol.pantalla_inicio if primera else "/"


def ambitos_de(usuario):
    """
    A que empresa/finca/bodega alcanza cada rol del usuario. Un supervisor
    de El Encanto no deberia ver los lotes de otra finca aunque su rol
    permita 'lote:leer' -- el ambito es lo que lo acota.
    """
    return [
        {
            "rol": a.rol.nombre,
            "es_superadmin": a.rol.es_superadmin,
            "pantalla_inicio": a.rol.pantalla_inicio,
            "empresa": str(a.empresa) if a.empresa_id else None,
            "empresa_id": a.empresa_id,
            "finca": str(a.finca) if a.finca_id else None,
            "finca_id": a.finca_id,
            "bodega": str(a.bodega) if a.bodega_id else None,
            "bodega_id": a.bodega_id,
            "punto_venta": str(a.punto_venta) if a.punto_venta_id else None,
            "punto_venta_id": a.punto_venta_id,
        }
        for a in asignaciones_activas(usuario)
    ]
