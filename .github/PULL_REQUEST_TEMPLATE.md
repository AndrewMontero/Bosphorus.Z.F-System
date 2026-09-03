## Módulo / fase

<!-- Ej: F1 · Paletizado — o el nombre del dominio si es fuera de fases (ej: Infraestructura, Identidad) -->

**Rama:** `modulo/nombre-corto`
**Cierra:** <!-- referencia al plan/concepto, o "N/A" -->

---

## Resumen

<!-- Una o dos frases: qué cambia y por qué, no un listado del diff.
     El "qué" ya está en los archivos tocados de abajo. -->

## Motivo

<!-- El porqué detrás del cambio. Si corrige algo de MiFiNet o cierra un
     hallazgo del reconocimiento, decilo aquí (ej: "Cierra H-07"). -->

---

## Cambios

<!-- Lista de archivos o carpetas tocados, agrupados por tipo -->

- **Modelos / migraciones:**
- **API:**
- **Frontend:**
- **Infraestructura (Docker, CI):**
- **Documentación:**

## Migraciones de base de datos

- [ ] Esta PR incluye migraciones nuevas
- [ ] Se probaron `migrate` y su reversa (`migrate <app> <migración_anterior>`) localmente
- [ ] No hay migraciones (marcar si aplica)

## Permisos y roles

<!-- Si esta PR toca el catálogo de permisos, roles o ámbitos: qué código(s)
     de permiso agrega/cambia y quién debería tenerlo. Si no aplica, borrar. -->

---

## Cómo probar localmente

```bash
git checkout modulo/nombre-corto
docker compose up -d
# pasos concretos: endpoint a llamar, usuario de prueba, qué se espera ver
```

## Evidencia

<!-- Salida de comandos, capturas de pantalla si es UI, o resultado de pruebas.
     "Confío en que funciona" no es evidencia. -->

---

## Riesgos y radio de impacto

<!-- Qué se rompe si esto falla, y a quién afecta (¿solo local?, ¿algún
     módulo ya en producción?, ¿datos de otros usuarios?) -->

## Ruta de reversa

<!-- Cómo se deshace esto si algo sale mal después de mergear:
     revert del commit, migración reversa, feature flag, etc. -->

---

## Checklist

- [ ] Sin secretos ni credenciales reales en el diff (revisar `.env`, claves, tokens)
- [ ] Sin cambios fuera del alcance de este módulo (no hay "de paso arreglé...")
- [ ] Pruebas relevantes agregadas o actualizadas
- [ ] `docker compose up` levanta limpio desde cero con esta rama
- [ ] La descripción de arriba está completa, no son solo los títulos

## Pendientes / fuera de alcance

<!-- Cosas notadas durante el trabajo pero no resueltas aquí a propósito.
     Si no hay ninguna, escribir "Ninguno". -->
