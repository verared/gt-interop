# Especificación INTEROP — Puentes con estándares heredados

- **Estado:** Estable (perfil RFC 3339); el resto adaptadores estables de
  traducción · **Versión:** 1.0.0 · **Línea base:** GUS v3.1.1
- **Edición consolidada:** [`../spec/gus-3.0.0.md`](../spec/gus-3.0.0.md) (§9.3, §10) ·
  Perfil: [`../profiles/gus-3339-perfil.md`](../profiles/gus-3339-perfil.md) ·
  Decisión: [`../decisions/D-001-frontera-utc-tai.md`](../decisions/D-001-frontera-utc-tai.md)
- **Licencia:** CC-BY-4.0 · Mantenida por: verared contributors

## 1. Alcance

Conversión exacta y auditable entre GUS y los formatos heredados:
RFC 3339 / ISO 8601, tiempo Unix, y la frontera UTC↔TAI que los
conecta (decisión D-001). Los formatos heredados son de
**entrada/salida e interoperabilidad**: nunca sustituyen a la coordenada
GUS como referencia de «hoy» ni como base de firmas.

## 2. Reglas normativas

1. **RFC 3339 (perfil GUS-3339):** mapeo determinista entre sellos GUS
   y `RFC 3339` con desplazamiento UTC; los casos negativos (segundos
   intercalares `:60`, offsets no canónicos, fechas imposibles) se
   rechazan con error explícito, nunca se normalizan en silencio.
2. **Unix:** conversión vía la tabla TAI−UTC versionada
   (`tai_unix = unix + tai_minus_utc(unix)`;
   `tcj_unix = tai_unix + 8400`;
   `instant = tcj_unix + 62_318_160_000`). La inversa es exacta por
   segmentos; el round-trip es exacto en ambos sentidos.
3. **Frontera UTC↔TAI (D-001):** el instante GUS se define sobre TAI
   (cierra D-001 en GUS 3.0.0); UTC es una escala de tiempo y RFC 3339
   un formato de presentación, no bases temporales del estándar.
4. **Segundos intercalares:** viven SOLO en la tabla del adaptador; un
   segundo intercalar histórico produce una diferencia de enteros de 2 s
   en el cruce: las diferencias de `instant` son duraciones físicas
   exactas.
5. **Gregoriano proléptico:** convertibilidad exacta vía JDN en ambas
   direcciones, sin ventana de exclusión; es un servicio derivado y no
   parte de la definición del calendario GUS.
6. **Forks del formato** (`1404IY-…`, `5786AH-…`): siguen siendo válidos;
   el fork es una elección de época, nunca de algoritmo.

## 3. Fuentes de verdad

| Plataforma | Implementación |
|---|---|
| Python | `src/gerarion/interop/profiles.py`, `src/gerarion/tcj/tai.py` |
| C11 | `impl-c/tai/gus_tai.c` |
| JavaScript | `web/engine/tcj-tai.mjs` |

## 4. Vectores aplicables

- `vectors/gus-3339-002.json` — positivos RFC 3339 (normativo).
- `vectors/gus-3339-negative-001.json` — rechazos normativos.
- `vectors/gus-normative-003.json` — bloques `tgs`/`fgs` (Unix↔instante).

## 5. Madurez y límites

- Perfil RFC 3339 y puente Unix: **estables** (vector 002 + negativos).
- UTC es una escala de tiempo y RFC 3339 un formato: ninguna interfaz de
  este dominio declara sincronización NTP ni certificación.
- Las fechas posteriores a `valid_until_unix` de la tabla generan aviso
  de extrapolación (ver dominio TCJ).

## 6. Referencias

- `docs/comparison/iso-8601-vs-rfc3339-vs-gus.md`,
  `docs/audit/AUDIT-REPORT-v3.0.0.md`.
