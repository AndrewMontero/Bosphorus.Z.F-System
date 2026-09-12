"""
Primeras pruebas del proyecto. Van sobre el calculo del cobro y sobre el
control de permisos -- son reglas de negocio donde un error cuesta plata o
abre una puerta, no andamiaje.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from autorizacion.models import Asignacion, Rol
from identidad.models import Usuario
from organizacion.models import Empresa

from .models import Ingreso, Tarifa, TipoVehiculo


class CalculoDeTarifaTest(TestCase):
    def setUp(self):
        self.tipo = TipoVehiculo.objects.create(nombre="Liviano")
        self.tarifa = Tarifa.objects.create(
            tipo_vehiculo=self.tipo,
            monto_hora=Decimal("1000.00"),
            monto_minimo=Decimal("500.00"),
        )

    def test_una_hora_exacta_cobra_una_hora(self):
        horas, monto = self.tarifa.calcular(3600)
        self.assertEqual(horas, 1)
        self.assertEqual(monto, Decimal("1000.00"))

    def test_hora_iniciada_se_cobra_completa(self):
        # 61 minutos son dos horas: asi funciona un parqueo real.
        horas, monto = self.tarifa.calcular(3660)
        self.assertEqual(horas, 2)
        self.assertEqual(monto, Decimal("2000.00"))

    def test_estadia_corta_cobra_la_hora_iniciada(self):
        horas, monto = self.tarifa.calcular(300)
        self.assertEqual(horas, 1)
        self.assertEqual(monto, Decimal("1000.00"))

    def test_el_minimo_manda_cuando_supera_el_calculo_por_hora(self):
        tarifa = Tarifa.objects.create(
            tipo_vehiculo=TipoVehiculo.objects.create(nombre="Moto"),
            monto_hora=Decimal("200.00"),
            monto_minimo=Decimal("1000.00"),
        )
        horas, monto = tarifa.calcular(3600)
        self.assertEqual(horas, 1)
        self.assertEqual(monto, Decimal("1000.00"))

    def test_salida_anterior_al_ingreso_es_error(self):
        with self.assertRaises(ValueError):
            self.tarifa.calcular(-60)

    def test_toma_la_tarifa_mas_reciente_y_no_una_vieja(self):
        # setUp ya dejo la tarifa de hoy en 1000. Una tarifa anterior no
        # debe ganarle: solo hay una vigente por tipo y fecha.
        hoy = timezone.localdate()
        Tarifa.objects.create(
            tipo_vehiculo=self.tipo,
            monto_hora=Decimal("500.00"),
            vigente_desde=hoy - timedelta(days=30),
        )
        vigente = Tarifa.vigente_para(self.tipo, hoy)
        self.assertEqual(vigente.monto_hora, Decimal("1000.00"))

    def test_una_tarifa_futura_no_se_aplica_todavia(self):
        # Se pueden dejar cargadas las tarifas del proximo mes sin que
        # empiecen a cobrarse antes de tiempo.
        hoy = timezone.localdate()
        Tarifa.objects.create(
            tipo_vehiculo=self.tipo,
            monto_hora=Decimal("1500.00"),
            vigente_desde=hoy + timedelta(days=7),
        )
        vigente = Tarifa.vigente_para(self.tipo, hoy)
        self.assertEqual(vigente.monto_hora, Decimal("1000.00"))

    def test_no_se_pueden_cargar_dos_tarifas_el_mismo_dia(self):
        from django.db.utils import IntegrityError

        with self.assertRaises(IntegrityError):
            Tarifa.objects.create(
                tipo_vehiculo=self.tipo,
                monto_hora=Decimal("1500.00"),
                vigente_desde=self.tarifa.vigente_desde,
            )


class CobroDeIngresoTest(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            cedula_juridica="3-101-000001", razon_social="Prueba S.A."
        )
        self.tipo = TipoVehiculo.objects.create(nombre="Liviano")
        Tarifa.objects.create(
            tipo_vehiculo=self.tipo,
            monto_hora=Decimal("1000.00"),
            monto_minimo=Decimal("500.00"),
        )
        self.usuario = Usuario.objects.create_user(
            email="caseta@prueba.cr", password="x", nombre_completo="Caseta"
        )

    def _ingreso(self, hace_segundos=7200):
        return Ingreso.objects.create(
            empresa=self.empresa,
            placa="ABC123",
            tipo_vehiculo=self.tipo,
            hora_ingreso=timezone.now() - timedelta(seconds=hace_segundos),
        )

    def test_cobrar_marca_salida_y_monto(self):
        ingreso = self._ingreso(7200)
        ingreso.cobrar(self.usuario)
        self.assertEqual(ingreso.estado, Ingreso.ESTADO_COBRADO)
        self.assertEqual(ingreso.horas_cobradas, 2)
        self.assertEqual(ingreso.monto_cobrado, Decimal("2000.00"))
        self.assertIsNotNone(ingreso.hora_salida)
        self.assertEqual(ingreso.cobrado_por, self.usuario)

    def test_no_se_puede_cobrar_dos_veces(self):
        ingreso = self._ingreso()
        ingreso.cobrar(self.usuario)
        with self.assertRaises(ValidationError):
            ingreso.cobrar(self.usuario)

    def test_sin_tarifa_vigente_no_deja_cobrar(self):
        tipo_sin_tarifa = TipoVehiculo.objects.create(nombre="Furgon")
        ingreso = Ingreso.objects.create(
            empresa=self.empresa,
            placa="XYZ789",
            tipo_vehiculo=tipo_sin_tarifa,
            hora_ingreso=timezone.now() - timedelta(hours=1),
        )
        with self.assertRaises(ValidationError):
            ingreso.cobrar(self.usuario)

    def test_la_tarifa_usada_queda_guardada(self):
        ingreso = self._ingreso()
        ingreso.cobrar(self.usuario)
        self.assertIsNotNone(ingreso.tarifa_aplicada)
        self.assertEqual(ingreso.tarifa_aplicada.monto_hora, Decimal("1000.00"))


class PermisosDeParqueoTest(TestCase):
    """
    Lo que de verdad protege el sistema es el servidor, no el menu.
    """

    def setUp(self):
        self.empresa = Empresa.objects.create(
            cedula_juridica="3-101-000002", razon_social="Prueba Dos S.A."
        )
        self.tipo = TipoVehiculo.objects.create(nombre="Liviano")
        Tarifa.objects.create(tipo_vehiculo=self.tipo, monto_hora=Decimal("1000.00"))
        self.ingreso = Ingreso.objects.create(
            empresa=self.empresa,
            placa="AAA111",
            tipo_vehiculo=self.tipo,
            hora_ingreso=timezone.now() - timedelta(hours=1),
        )
        self.cliente = APIClient()

    def _usuario_con(self, nombre_rol, correo):
        usuario = Usuario.objects.create_user(
            email=correo, password="Prueba2026!", nombre_completo=nombre_rol
        )
        Asignacion.objects.create(usuario=usuario, rol=Rol.objects.get(nombre=nombre_rol))
        return usuario

    def test_sin_sesion_no_se_ve_nada(self):
        respuesta = self.cliente.get("/api/parqueo/ingresos/")
        self.assertEqual(respuesta.status_code, 401)

    def test_rol_parqueo_puede_cobrar(self):
        self.cliente.force_authenticate(self._usuario_con("Parqueo", "caseta@prueba.cr"))
        respuesta = self.cliente.post(f"/api/parqueo/ingresos/{self.ingreso.pk}/cobrar/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["estado"], "cobrado")

    def test_operador_de_linea_no_puede_cobrar(self):
        self.cliente.force_authenticate(
            self._usuario_con("Operador de línea", "linea@prueba.cr")
        )
        respuesta = self.cliente.post(f"/api/parqueo/ingresos/{self.ingreso.pk}/cobrar/")
        self.assertEqual(respuesta.status_code, 403)

    def test_operador_de_linea_no_puede_ni_listar(self):
        self.cliente.force_authenticate(
            self._usuario_con("Operador de línea", "linea2@prueba.cr")
        )
        respuesta = self.cliente.get("/api/parqueo/ingresos/")
        self.assertEqual(respuesta.status_code, 403)

    def test_usuario_desactivado_pierde_el_acceso(self):
        usuario = self._usuario_con("Parqueo", "inactivo@prueba.cr")
        usuario.is_active = False
        usuario.save()
        self.cliente.force_authenticate(usuario)
        respuesta = self.cliente.get("/api/parqueo/ingresos/")
        self.assertEqual(respuesta.status_code, 403)
