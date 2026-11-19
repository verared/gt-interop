# Puentes con estándares heredados

Parte de la suite de referencia **Gerarion** (verared/gerarion `v3.2.0`,
Gerarion Universal Standard). Este directorio es un **paquete de
exportación** listo para publicarse (o consumirse) como repositorio
satélite `verared/gt-interop`; conserva las rutas relativas del repositorio
base para componer módulos.

## El problema único que resuelve

Conversión exacta y auditable entre GUS y RFC 3339 / ISO 8601 / Unix, y el perfil RFC 3161 (TSA). Los formatos heredados son de entrada/salida: nunca sustituyen a la coordenada GUS.

## Estado normativo

- **Estable (RFC 3339) / Experimental (RFC 3161)** — línea base `v3.2.0` (aritmética y vectores
  congelados: GUS v3.0.0).
- Especificación(es) incluida(s): `docs/specs/INTEROP.es.md`, `docs/specs/INTEROP.en.md`

## Dependencias

- `gt-core` (*verared/gt-core*): tipos base y servicios del núcleo.
- `gt-tcj` (*verared/gt-tcj*): módulo hermano de esta suite.
Base común: `verared/gerarion` `v3.2.0`.

## Contenido

- `LICENSE`
- `NOTICE`
- `docs/specs/INTEROP.en.md`
- `docs/specs/INTEROP.es.md`
- `src/gerarion/interop/__init__.py`
- `src/gerarion/interop/profiles.py`
- `src/gerarion/interop/tsa.py`
- `vectors/gus-3339-002.json`
- `vectors/gus-3339-negative-001.json`

## Uso offline

No requiere red, cuentas, registro de paquetes ni frameworks:

```bash
python3 -c 'import sys; sys.path.insert(0, "src"); import gerarion'
```

## Verificación

Con Python ≥ 3.9 y `reuse` instalado:

```bash
reuse lint                                    # licencias al 100 %
# (las pruebas viven en la suite de verared/gerarion)
```

## Contrato de sincronización con `verared/gerarion`

Este paquete es **generado, no editado a mano**: se regenera byte a
byte desde `verared/gerarion v3.2.0` con
`python3 tools/export_module.py --module gt-interop --out <dir>`. La fuente
de verdad normativa (especificaciones, vectores CC0, núcleos de
referencia de las tres plataformas y la batería completa) permanece en
`verared/gerarion`; los satélites `verared/gt-interop` la consumen y no forkean la
aritmética. Las actualizaciones fluyen regenerando la exportación desde
un tag del repositorio base; nunca editando los archivos exportados.
