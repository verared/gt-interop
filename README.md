# Bridges with legacy standards

Part of the **Gerarion** reference suite (verared/gerarion `v3.2.2`,
Gerarion Universal Standard). This directory is an **export package**
ready to be published (or consumed) as the `verared/gt-interop` satellite
repository; it keeps the base repository's relative layout so modules
compose cleanly.

## The unique problem it solves

Exact, auditable conversion between GUS and RFC 3339 / ISO 8601 / Unix, plus the RFC 3161 (TSA) profile. Legacy formats are for input/output: they never replace the GUS coordinate.

## Normative status

- **Estable (RFC 3339) / Experimental (RFC 3161)** (`maturity: stable`) — baseline `v3.2.2` (frozen arithmetic and vectors:
  GUS v3.0.0).
- Included specification(s): `docs/specs/INTEROP.es.md`, `docs/specs/INTEROP.en.md`
- Verifiable integrity manifest: [`EXPORT-MANIFEST.json`](EXPORT-MANIFEST.json)
- Official compatibility matrix: [`COMPATIBILITY.md`](https://github.com/verared/gerarion/blob/v3.2.2/COMPATIBILITY.md)

## Dependencies

- `gt-core` (*verared/gt-core*): tipos base y servicios del núcleo.
- `gt-tcj` (*verared/gt-tcj*): sibling module of this suite.
Common base: `verared/gerarion` `3.2.2`.

## Contents

- `EXPORT-MANIFEST.json`
- `LICENSE`
- `NOTICE`
- `docs/specs/INTEROP.en.md`
- `docs/specs/INTEROP.es.md`
- `src/gerarion/interop/__init__.py`
- `src/gerarion/interop/profiles.py`
- `src/gerarion/interop/tsa.py`
- `vectors/gus-3339-002.json`
- `vectors/gus-3339-negative-001.json`

## Offline usage

No network, accounts, package registries, or frameworks required:

```bash
python3 -c 'import sys; sys.path.insert(0, "src"); import gerarion'
```

## Verification

With Python ≥ 3.9 and `reuse` installed:

```bash
reuse lint                                    # licensing 100 %
# (las pruebas viven en la suite de verared/gerarion)
```

From `verared/gerarion`, full integrity against `EXPORT-MANIFEST.json` is verified with:

```bash
python3 tools/export_module.py --verify-existing /path/to/gt-interop
```

## Synchronisation contract with `verared/gerarion`

This package is **generated, never hand-edited**: it is regenerated
byte for byte from `verared/gerarion v3.2.2` with
`python3 tools/export_module.py --module gt-interop --out <dir>`. The
normative source of truth (specifications, CC0 vectors, reference
cores for the three platforms, and the full test suite) stays in
`verared/gerarion`; `verared/gt-interop` satellites consume it and never fork the
arithmetic. Updates flow by regenerating the export from a tag of the
base repository — never by editing exported files.
