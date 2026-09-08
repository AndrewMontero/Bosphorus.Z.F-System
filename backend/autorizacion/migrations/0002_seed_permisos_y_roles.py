"""
Catalogo inicial de permisos y roles base, derivado del inventario de 230
formularios extraido de MiFiNet.exe (ver docs/adr/0001-permisos-con-ambito.md).

Esto es semilla, no codigo de negocio: si un permiso o rol no calza con como
trabaja Donatella en la practica, se corrige aqui -- es un dato, no un
refactor.
"""

from django.db import migrations

PERMISOS = [
    # contabilidad
    ("asiento:crear", "Crear asiento contable", "contabilidad"),
    ("asiento:leer", "Consultar asientos contables", "contabilidad"),
    ("asiento:anular", "Anular asiento contable", "contabilidad"),
    ("cierre_contable:ejecutar", "Ejecutar cierre contable del periodo", "contabilidad"),
    ("reporte_contable:leer", "Consultar reportes contables", "contabilidad"),
    # cuentas por cobrar / pagar
    ("cxc:leer", "Consultar cuentas por cobrar", "cuentas"),
    ("cxc:cobrar", "Registrar abono de cuentas por cobrar", "cuentas"),
    ("cxp:leer", "Consultar cuentas por pagar", "cuentas"),
    ("cxp:pagar", "Registrar pago de cuentas por pagar", "cuentas"),
    ("cheque:emitir", "Emitir cheque", "cuentas"),
    # facturacion
    ("factura:emitir", "Emitir factura electrónica", "facturacion"),
    ("factura:anular", "Anular factura electrónica", "facturacion"),
    ("factura:leer", "Consultar facturas", "facturacion"),
    ("nota_credito:emitir", "Emitir nota de crédito", "facturacion"),
    ("precio:editar", "Editar lista de precios", "facturacion"),
    ("cabys:mantener", "Mantener catálogo CABYS", "facturacion"),
    # agricola
    ("lote:leer", "Consultar lotes de finca", "agricola"),
    ("lote:editar", "Editar datos de un lote", "agricola"),
    ("cosecha:registrar", "Registrar cosecha", "agricola"),
    ("paquete_tecnologico:leer", "Consultar paquete tecnológico", "agricola"),
    ("paquete_tecnologico:aprobar", "Aprobar paquete tecnológico", "agricola"),
    ("muestreo_brix:registrar", "Registrar muestreo de grados Brix", "agricola"),
    # produccion y empaque
    ("tarima:crear", "Crear tarima", "produccion"),
    ("tarima:leer", "Consultar tarimas", "produccion"),
    ("tarima:anular", "Anular tarima", "produccion"),
    ("contenedor:crear", "Crear contenedor", "produccion"),
    ("contenedor:cerrar", "Cerrar contenedor", "produccion"),
    ("bill_of_lading:emitir", "Emitir bill of lading", "produccion"),
    # inventario
    ("inventario:leer", "Consultar existencias de inventario", "inventario"),
    ("inventario:ajustar", "Ajustar existencias de inventario", "inventario"),
    ("traslado:crear", "Crear traslado entre bodegas", "inventario"),
    ("kardex:leer", "Consultar kardex", "inventario"),
    # proveeduria
    ("orden_compra:crear", "Crear orden de compra", "proveeduria"),
    ("orden_compra:aprobar", "Aprobar orden de compra", "proveeduria"),
    ("proveedor:mantener", "Mantener catálogo de proveedores", "proveeduria"),
    # rrhh
    ("empleado:mantener", "Mantener datos de empleados", "rrhh"),
    ("planilla:calcular", "Calcular planilla", "rrhh"),
    ("planilla:aprobar", "Aprobar planilla", "rrhh"),
    ("marca_biometrica:leer", "Consultar marcas biométricas", "rrhh"),
    # parqueo
    ("parqueo:registrar_ingreso", "Registrar ingreso de vehículo", "parqueo"),
    ("parqueo:cobrar", "Cobrar tarifa de parqueo", "parqueo"),
    # sistema
    ("usuario:crear", "Crear usuario", "sistema"),
    ("usuario:desactivar", "Desactivar usuario", "sistema"),
    ("usuario:asignar_rol", "Asignar rol y ámbito a un usuario", "sistema"),
    ("bitacora:leer", "Consultar bitácora de permisos", "sistema"),
    ("empresa:mantener", "Mantener catálogo de empresas del grupo", "sistema"),
]

PERMISOS_LECTURA = [
    "asiento:leer", "reporte_contable:leer", "cxc:leer", "cxp:leer", "factura:leer",
    "lote:leer", "paquete_tecnologico:leer", "tarima:leer", "inventario:leer",
    "kardex:leer", "marca_biometrica:leer", "bitacora:leer",
]

TODOS_LOS_CODIGOS = [codigo for codigo, _, _ in PERMISOS]

ROLES = [
    ("Superadministrador", "Administra usuarios, roles y ámbitos.", "/panel-superadmin", True, TODOS_LOS_CODIGOS),
    ("Operador de línea", "Paletizado en planta.", "/paletizado", False,
        ["tarima:crear", "tarima:leer", "contenedor:crear"]),
    ("Supervisor de planta", "Producción, empaque e inventario.", "/contenedores-del-dia", False,
        ["tarima:crear", "tarima:leer", "tarima:anular", "contenedor:crear", "contenedor:cerrar",
         "bill_of_lading:emitir", "inventario:leer", "inventario:ajustar"]),
    ("Supervisor agrícola", "Fincas y lotes de su ámbito.", "/lotes", False,
        ["lote:leer", "lote:editar", "cosecha:registrar", "paquete_tecnologico:leer",
         "paquete_tecnologico:aprobar", "muestreo_brix:registrar"]),
    ("Facturación", "Ventas y factura electrónica.", "/facturacion", False,
        ["factura:emitir", "factura:anular", "factura:leer", "nota_credito:emitir",
         "precio:editar", "cabys:mantener"]),
    ("Contabilidad", "Asientos, cierre y cuentas.", "/asientos", False,
        ["asiento:crear", "asiento:leer", "asiento:anular", "cierre_contable:ejecutar",
         "reporte_contable:leer", "cxc:leer", "cxc:cobrar", "cxp:leer", "cxp:pagar", "cheque:emitir"]),
    ("Proveeduría", "Compras y bodega.", "/ordenes-pendientes", False,
        ["orden_compra:crear", "orden_compra:aprobar", "proveedor:mantener", "inventario:leer"]),
    ("Recursos Humanos", "Planilla y empleados.", "/planilla", False,
        ["empleado:mantener", "planilla:calcular", "planilla:aprobar", "marca_biometrica:leer"]),
    ("Consulta", "Solo lectura, transversal.", "/tablero", False, PERMISOS_LECTURA),
]


def crear_permisos_y_roles(apps, schema_editor):
    Permiso = apps.get_model("autorizacion", "Permiso")
    Rol = apps.get_model("autorizacion", "Rol")

    permisos_por_codigo = {
        codigo: Permiso.objects.create(codigo=codigo, descripcion=descripcion, dominio=dominio)
        for codigo, descripcion, dominio in PERMISOS
    }

    for nombre, descripcion, pantalla_inicio, es_superadmin, codigos in ROLES:
        rol = Rol.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            pantalla_inicio=pantalla_inicio,
            es_superadmin=es_superadmin,
        )
        rol.permisos.set([permisos_por_codigo[c] for c in codigos])


def eliminar_permisos_y_roles(apps, schema_editor):
    Rol = apps.get_model("autorizacion", "Rol")
    Permiso = apps.get_model("autorizacion", "Permiso")
    Rol.objects.all().delete()
    Permiso.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("autorizacion", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_permisos_y_roles, eliminar_permisos_y_roles),
    ]
