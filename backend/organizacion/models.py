from django.db import models


class Empresa(models.Model):
    """
    Una de las sociedades del grupo. El grupo opera con varias cedulas
    juridicas por razones fiscales y de tenencia de tierra -- esto NO es
    multi-tenant tipo SaaS, es multi-empresa dentro de un mismo grupo.
    """

    cedula_juridica = models.CharField("cédula jurídica", max_length=20, unique=True)
    razon_social = models.CharField("razón social", max_length=200)
    nombre_comercial = models.CharField("nombre comercial", max_length=200, blank=True)
    activa = models.BooleanField("activa", default=True)

    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        ordering = ["razon_social"]

    def __str__(self):
        return self.nombre_comercial or self.razon_social


class Finca(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="fincas")
    nombre = models.CharField("nombre", max_length=150)
    area_hectareas = models.DecimalField(
        "área (ha)", max_digits=8, decimal_places=2, null=True, blank=True
    )
    activa = models.BooleanField("activa", default=True)

    class Meta:
        verbose_name = "finca"
        verbose_name_plural = "fincas"
        ordering = ["empresa", "nombre"]
        constraints = [
            models.UniqueConstraint(fields=["empresa", "nombre"], name="finca_unica_por_empresa"),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.empresa})"


class Bodega(models.Model):
    TIPO_CHOICES = [
        ("insumos", "Insumos agrícolas"),
        ("empaque", "Material de empaque"),
        ("producto_terminado", "Producto terminado"),
        ("repuestos", "Repuestos y mantenimiento"),
        ("otro", "Otro"),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="bodegas")
    nombre = models.CharField("nombre", max_length=150)
    tipo = models.CharField("tipo", max_length=30, choices=TIPO_CHOICES, default="otro")
    activa = models.BooleanField("activa", default=True)

    class Meta:
        verbose_name = "bodega"
        verbose_name_plural = "bodegas"
        ordering = ["empresa", "nombre"]
        constraints = [
            models.UniqueConstraint(fields=["empresa", "nombre"], name="bodega_unica_por_empresa"),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.empresa})"


class PuntoVenta(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="puntos_venta")
    nombre = models.CharField("nombre", max_length=150)
    activo = models.BooleanField("activo", default=True)

    class Meta:
        verbose_name = "punto de venta"
        verbose_name_plural = "puntos de venta"
        ordering = ["empresa", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "nombre"], name="punto_venta_unico_por_empresa"
            ),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.empresa})"
