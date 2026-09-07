from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from autorizacion.models import Asignacion, Rol
from identidad.models import Usuario


class Command(BaseCommand):
    help = (
        "Crea un usuario y le asigna el rol de negocio Superadministrador. "
        "Sirve para arrancar el sistema: sin esto no hay con quien iniciar sesion."
    )

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--nombre", required=True, help="Nombre completo")
        parser.add_argument("--password", required=True)

    @transaction.atomic
    def handle(self, *args, **opciones):
        email = opciones["email"].strip().lower()

        if Usuario.objects.filter(email=email).exists():
            raise CommandError(f"Ya existe un usuario con el correo {email}.")

        try:
            rol = Rol.objects.get(es_superadmin=True)
        except Rol.DoesNotExist:
            raise CommandError(
                "No existe el rol de Superadministrador. Corré primero las migraciones."
            )

        usuario = Usuario.objects.create_user(
            email=email,
            password=opciones["password"],
            nombre_completo=opciones["nombre"],
            # is_staff da acceso al admin de Django (/admin/), que por ahora
            # hace de panel de superadministrador hasta que exista el propio.
            is_staff=True,
        )
        Asignacion.objects.create(usuario=usuario, rol=rol, asignado_por=usuario)

        self.stdout.write(
            self.style.SUCCESS(
                f"Superadministrador creado: {email}\n"
                f"  Rol: {rol.nombre} ({rol.permisos.count()} permisos)\n"
                f"  Pantalla de inicio: {rol.pantalla_inicio}\n"
                f"  Admin de Django: http://localhost:8000/admin/"
            )
        )
