from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from organizacion.models import Bodega, Empresa, Finca, PuntoVenta

codigo_permiso_validator = RegexValidator(
    regex=r"^[a-z_]+:[a-z_]+$",
    message="El código debe tener la forma 'recurso:accion', solo minúsculas y "
    "guiones bajos (ej: tarima:crear).",
)


class Permiso(models.Model):
    """
    Un permiso es SIEMPRE recurso:accion, nunca "acceso a la pantalla X".
    Atar permisos a pantallas amarra la seguridad al diseño de la interfaz
    -- es el error que evitamos aprendiendo de como esta hecho MiFiNet.
    """

    DOMINIO_CHOICES = [
        ("contabilidad", "Contabilidad y finanzas"),
        ("cuentas", "Cuentas por cobrar y pagar"),
        ("facturacion", "Facturación, ventas y factura electrónica"),
        ("agricola", "Agrícola y finca"),
        ("produccion", "Producción y empaque"),
        ("inventario", "Inventario y bodega"),
        ("proveeduria", "Proveeduría y compras"),
        ("rrhh", "Recursos humanos y planilla"),
        ("parqueo", "Parqueo"),
        ("sistema", "Sistema y administración"),
    ]

    codigo = models.CharField(
        "código", max_length=100, unique=True, validators=[codigo_permiso_validator]
    )
    descripcion = models.CharField("descripción", max_length=200)
    dominio = models.CharField("dominio", max_length=30, choices=DOMINIO_CHOICES)

    class Meta:
        verbose_name = "permiso"
        verbose_name_plural = "permisos"
        ordering = ["dominio", "codigo"]

    def __str__(self):
        return self.codigo


class Rol(models.Model):
    nombre = models.CharField("nombre", max_length=100, unique=True)
    descripcion = models.CharField("descripción", max_length=250, blank=True)
    pantalla_inicio = models.CharField(
        "pantalla de inicio",
        max_length=100,
        blank=True,
        help_text="Ruta del frontend a la que cae este rol al iniciar sesión.",
    )
    es_superadmin = models.BooleanField(
        "es superadministrador",
        default=False,
        help_text="Puede asignar roles y ámbitos a otros usuarios.",
    )
    permisos = models.ManyToManyField(Permiso, through="RolPermiso", related_name="roles")

    class Meta:
        verbose_name = "rol"
        verbose_name_plural = "roles"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class RolPermiso(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "permiso de rol"
        verbose_name_plural = "permisos de rol"
        constraints = [
            models.UniqueConstraint(fields=["rol", "permiso"], name="permiso_unico_por_rol"),
        ]

    def __str__(self):
        return f"{self.rol} → {self.permiso}"


class Asignacion(models.Model):
    """
    Une un usuario con un rol, con un ambito opcional (empresa/finca/bodega/
    punto de venta) que acota donde aplica. Sin ambito, el rol aplica a todo
    lo que ese rol ya permite -- uso tipico del rol de superadministrador.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="asignaciones"
    )
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name="asignaciones")

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    finca = models.ForeignKey(Finca, on_delete=models.CASCADE, null=True, blank=True)
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, null=True, blank=True)
    punto_venta = models.ForeignKey(PuntoVenta, on_delete=models.CASCADE, null=True, blank=True)

    activa = models.BooleanField("activa", default=True)

    asignado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asignaciones_realizadas",
    )
    asignado_en = models.DateTimeField("asignado en", auto_now_add=True)

    class Meta:
        verbose_name = "asignación"
        verbose_name_plural = "asignaciones"
        ordering = ["-asignado_en"]

    def __str__(self):
        return f"{self.usuario} — {self.rol}"

    def clean(self):
        if not self.pk or self.activa:
            return
        estaba_activa = (
            Asignacion.objects.filter(pk=self.pk).values_list("activa", flat=True).first()
        )
        if estaba_activa and self.rol.es_superadmin:
            self._validar_no_es_ultimo_superadmin()

    def _validar_no_es_ultimo_superadmin(self):
        queda_otro = (
            Asignacion.objects.filter(rol__es_superadmin=True, activa=True, usuario__is_active=True)
            .exclude(pk=self.pk)
            .exists()
        )
        if not queda_otro:
            raise ValidationError(
                "No se puede desactivar esta asignación: es la última que otorga el rol "
                "de superadministrador. Debe existir al menos un superadministrador activo."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BitacoraPermisos(models.Model):
    ACCION_CHOICES = [
        ("asignado", "Asignado"),
        ("revocado", "Revocado"),
        ("reactivado", "Reactivado"),
    ]

    usuario_afectado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bitacora_como_afectado"
    )
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    accion = models.CharField("acción", max_length=20, choices=ACCION_CHOICES)
    ambito_descripcion = models.CharField(
        "ámbito",
        max_length=250,
        blank=True,
        help_text="Descripción textual del ámbito al momento de la acción -- "
        "asi el registro se sigue entendiendo aunque el ambito se borre despues.",
    )
    realizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bitacora_como_autor",
    )
    es_autoasignacion = models.BooleanField("es autoasignación", default=False)
    realizado_en = models.DateTimeField("realizado en", auto_now_add=True)

    class Meta:
        verbose_name = "entrada de bitácora de permisos"
        verbose_name_plural = "bitácora de permisos"
        ordering = ["-realizado_en"]

    def __str__(self):
        return f"{self.get_accion_display()} · {self.rol} · {self.usuario_afectado}"
