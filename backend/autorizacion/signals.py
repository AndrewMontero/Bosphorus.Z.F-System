from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from identidad.models import Usuario

from .models import Asignacion, BitacoraPermisos


def _describir_ambito(asignacion):
    partes = []
    if asignacion.empresa_id:
        partes.append(f"empresa={asignacion.empresa}")
    if asignacion.finca_id:
        partes.append(f"finca={asignacion.finca}")
    if asignacion.bodega_id:
        partes.append(f"bodega={asignacion.bodega}")
    if asignacion.punto_venta_id:
        partes.append(f"punto_venta={asignacion.punto_venta}")
    return ", ".join(partes) or "sin ámbito (global para el rol)"


@receiver(post_save, sender=Asignacion)
def registrar_en_bitacora(sender, instance, created, **kwargs):
    """
    La bitacora es un efecto de la accion de dominio, no algo que el
    codigo que llama tenga que acordarse de hacer aparte.
    """
    if created:
        accion = "asignado"
    else:
        accion = "reactivado" if instance.activa else "revocado"

    BitacoraPermisos.objects.create(
        usuario_afectado=instance.usuario,
        rol=instance.rol,
        accion=accion,
        ambito_descripcion=_describir_ambito(instance),
        realizado_por=instance.asignado_por,
        es_autoasignacion=(instance.asignado_por_id == instance.usuario_id),
    )


@receiver(pre_save, sender=Usuario)
def evitar_desactivar_ultimo_superadmin(sender, instance, **kwargs):
    """
    Misma regla que Asignacion._validar_no_es_ultimo_superadmin, pero
    para cuando alguien desactiva el Usuario directamente (is_active=False)
    en vez de revocar la asignacion. Las dos puertas deben estar cerradas.
    """
    if not instance.pk:
        return
    try:
        anterior = Usuario.objects.get(pk=instance.pk)
    except Usuario.DoesNotExist:
        return

    if not (anterior.is_active and not instance.is_active):
        return

    tiene_rol_superadmin = Asignacion.objects.filter(
        usuario=instance, rol__es_superadmin=True, activa=True
    ).exists()
    if not tiene_rol_superadmin:
        return

    queda_otro = (
        Asignacion.objects.filter(rol__es_superadmin=True, activa=True, usuario__is_active=True)
        .exclude(usuario=instance)
        .exists()
    )
    if not queda_otro:
        raise ValidationError(
            "No se puede desactivar este usuario: es el último superadministrador activo."
        )
