"""
Cada modulo trae sus propios permisos. Asi el catalogo crece junto con el
sistema en vez de vivir todo en una semilla gigante que hay que tocar cada
vez que aparece un modulo nuevo.
"""

from django.db import migrations

PERMISOS_NUEVOS = [
    ("parqueo:leer", "Consultar el parqueo y sus tarifas", "parqueo"),
    ("parqueo:mantener", "Mantener tipos de vehículo y tarifas", "parqueo"),
]

# Los otros dos ya venian de la semilla inicial de autorizacion.
TODOS_LOS_DE_PARQUEO = [
    "parqueo:leer",
    "parqueo:mantener",
    "parqueo:registrar_ingreso",
    "parqueo:cobrar",
]


def agregar(apps, schema_editor):
    Permiso = apps.get_model("autorizacion", "Permiso")
    Rol = apps.get_model("autorizacion", "Rol")

    for codigo, descripcion, dominio in PERMISOS_NUEVOS:
        Permiso.objects.get_or_create(
            codigo=codigo, defaults={"descripcion": descripcion, "dominio": dominio}
        )

    permisos = list(Permiso.objects.filter(codigo__in=TODOS_LOS_DE_PARQUEO))

    # El superadministrador siempre tiene todo.
    for rol in Rol.objects.filter(es_superadmin=True):
        rol.permisos.add(*permisos)

    # Rol operativo del modulo: quien atiende la caseta.
    rol_parqueo, _ = Rol.objects.get_or_create(
        nombre="Parqueo",
        defaults={
            "descripcion": "Registra ingresos y cobra salidas en la caseta.",
            "pantalla_inicio": "/parqueo",
            "es_superadmin": False,
        },
    )
    rol_parqueo.permisos.set(permisos)


def quitar(apps, schema_editor):
    Permiso = apps.get_model("autorizacion", "Permiso")
    Rol = apps.get_model("autorizacion", "Rol")
    Rol.objects.filter(nombre="Parqueo").delete()
    Permiso.objects.filter(codigo__in=[c for c, _, _ in PERMISOS_NUEVOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("parqueo", "0001_initial"),
        ("autorizacion", "0002_seed_permisos_y_roles"),
    ]

    operations = [
        migrations.RunPython(agregar, quitar),
    ]
