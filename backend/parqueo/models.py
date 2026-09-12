from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from organizacion.models import Empresa

UNA_HORA = Decimal("3600")


class TipoVehiculo(models.Model):
    nombre = models.CharField("nombre", max_length=60, unique=True)
    activo = models.BooleanField("activo", default=True)

    class Meta:
        verbose_name = "tipo de vehículo"
        verbose_name_plural = "tipos de vehículo"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Tarifa(models.Model):
    """
    Tarifa vigente por tipo de vehiculo. No se edita una tarifa pasada:
    se crea una nueva con otra fecha de vigencia, para que un cobro viejo
    siga siendo explicable con la tarifa que realmente se le aplico.
    """

    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT, related_name="tarifas")
    monto_hora = models.DecimalField(
        "monto por hora", max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    monto_minimo = models.DecimalField(
        "monto mínimo", max_digits=10, decimal_places=2, default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Lo que se cobra aunque el vehículo salga a los pocos minutos.",
    )
    vigente_desde = models.DateField("vigente desde", default=timezone.localdate)

    class Meta:
        verbose_name = "tarifa"
        verbose_name_plural = "tarifas"
        ordering = ["tipo_vehiculo", "-vigente_desde"]
        constraints = [
            models.UniqueConstraint(
                fields=["tipo_vehiculo", "vigente_desde"], name="tarifa_unica_por_tipo_y_fecha"
            ),
        ]

    def __str__(self):
        return f"{self.tipo_vehiculo} — ₡{self.monto_hora}/h desde {self.vigente_desde}"

    @classmethod
    def vigente_para(cls, tipo_vehiculo, fecha=None):
        fecha = fecha or timezone.localdate()
        return (
            cls.objects.filter(tipo_vehiculo=tipo_vehiculo, vigente_desde__lte=fecha)
            .order_by("-vigente_desde")
            .first()
        )

    def calcular(self, segundos):
        """
        Cobra por hora iniciada: 61 minutos son dos horas. Es como funciona
        un parqueo real y como lo hacia MiFiNet.

        Devuelve (horas_cobradas, monto).
        """
        if segundos < 0:
            raise ValueError("La salida no puede ser anterior al ingreso.")

        horas = int(Decimal(segundos) / UNA_HORA)
        if Decimal(segundos) % UNA_HORA:
            horas += 1
        horas = max(horas, 1)

        monto = max(self.monto_hora * horas, self.monto_minimo)
        return horas, monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Ingreso(models.Model):
    ESTADO_DENTRO = "dentro"
    ESTADO_COBRADO = "cobrado"
    ESTADO_CHOICES = [
        (ESTADO_DENTRO, "Dentro"),
        (ESTADO_COBRADO, "Cobrado y salió"),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="ingresos_parqueo")
    placa = models.CharField("placa", max_length=15, db_index=True)
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT, related_name="ingresos")

    hora_ingreso = models.DateTimeField("hora de ingreso", default=timezone.now)
    hora_salida = models.DateTimeField("hora de salida", null=True, blank=True)

    # Se guarda la tarifa usada, no solo el monto: si manana cambia la
    # tarifa, este cobro se sigue pudiendo explicar.
    tarifa_aplicada = models.ForeignKey(
        Tarifa, on_delete=models.PROTECT, null=True, blank=True, related_name="cobros"
    )
    horas_cobradas = models.PositiveIntegerField("horas cobradas", null=True, blank=True)
    monto_cobrado = models.DecimalField(
        "monto cobrado", max_digits=10, decimal_places=2, null=True, blank=True
    )

    estado = models.CharField("estado", max_length=10, choices=ESTADO_CHOICES, default=ESTADO_DENTRO)

    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="ingresos_registrados",
    )
    cobrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="cobros_parqueo",
    )

    class Meta:
        verbose_name = "ingreso a parqueo"
        verbose_name_plural = "ingresos a parqueo"
        ordering = ["-hora_ingreso"]
        constraints = [
            # Una placa no puede estar dentro dos veces a la vez.
            models.UniqueConstraint(
                fields=["placa", "empresa"],
                condition=models.Q(estado="dentro"),
                name="placa_unica_mientras_esta_dentro",
            ),
        ]

    def __str__(self):
        return f"{self.placa} ({self.get_estado_display()})"

    @property
    def segundos_dentro(self):
        fin = self.hora_salida or timezone.now()
        return int((fin - self.hora_ingreso).total_seconds())

    def cobrar(self, usuario, momento=None):
        if self.estado == self.ESTADO_COBRADO:
            raise ValidationError("Este ingreso ya fue cobrado.")

        momento = momento or timezone.now()
        if momento < self.hora_ingreso:
            raise ValidationError("La hora de salida no puede ser anterior a la de ingreso.")

        tarifa = Tarifa.vigente_para(self.tipo_vehiculo, momento.date())
        if tarifa is None:
            raise ValidationError(
                f"No hay tarifa vigente para «{self.tipo_vehiculo}». "
                "Configurela antes de cobrar."
            )

        segundos = int((momento - self.hora_ingreso).total_seconds())
        horas, monto = tarifa.calcular(segundos)

        self.hora_salida = momento
        self.tarifa_aplicada = tarifa
        self.horas_cobradas = horas
        self.monto_cobrado = monto
        self.estado = self.ESTADO_COBRADO
        self.cobrado_por = usuario
        self.save()
        return self
