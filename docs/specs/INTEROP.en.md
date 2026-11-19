# INTEROP Specification — Bridges with Legacy Standards

- **Status:** Stable (RFC 3339 profile); remaining adapters are stable
  translation layers · **Version:** 1.0.0 · **Baseline:** GUS v3.1.1
- **Consolidated edition:** [`../en/gus-3.0.0.md`](../en/gus-3.0.0.md) (§9.3, §10) ·
  Profile: [`../en/profiles/gus-3339-profile.md`](../en/profiles/gus-3339-profile.md) ·
  Decision: [`../en/decisions/D-001-utc-tai-boundary.md`](../en/decisions/D-001-utc-tai-boundary.md)
- **License:** CC-BY-4.0 · Maintained by: verared contributors

## 1. Scope

Exact, auditable conversion between GUS and legacy formats: RFC 3339 /
ISO 8601, Unix time, and the UTC↔TAI boundary that connects them
(decision D-001). Legacy formats are for **input/output and
interoperability**: they never replace the GUS coordinate as the "today"
reference nor as the basis of signatures.

## 2. Normative rules

1. **RFC 3339 (GUS-3339 profile):** deterministic mapping between GUS
   stamps and `RFC 3339` with UTC offset; negative cases (leap-second
   `:60`, non-canonical offsets, impossible dates) are rejected with an
   explicit error, never silently normalised.
2. **Unix:** conversion via the versioned TAI−UTC table
   (`tai_unix = unix + tai_minus_utc(unix)`;
   `tcj_unix = tai_unix + 8400`;
   `instant = tcj_unix + 62_318_160_000`). The inverse is exact per
   segment; the round-trip is exact in both directions.
3. **UTC↔TAI boundary (D-001):** the GUS instant is defined over TAI
   (closing D-001 in GUS 3.0.0); UTC is a timescale and RFC 3339 a
   presentation format, not the standard's time bases.
4. **Leap seconds:** they live ONLY in the adapter's table; a historical
   leap second produces a 2 s integer difference across it, so
   `instant` differences are exact physical durations.
5. **Proleptic Gregorian:** exact convertibility via JDN in both
   directions, no exclusion window; it is a derived service, not part of
   the GUS calendar definition.
6. **Format forks** (`1404IY-…`, `5786AH-…`): still valid; a fork is an
   epoch choice, never an algorithm change.

## 3. Sources of truth

| Platform | Implementation |
|---|---|
| Python | `src/gerarion/interop/profiles.py`, `src/gerarion/tcj/tai.py` |
| C11 | `impl-c/tai/gus_tai.c` |
| JavaScript | `web/engine/tcj-tai.mjs` |

## 4. Applicable vectors

- `vectors/gus-3339-002.json` — positive RFC 3339 cases (normative).
- `vectors/gus-3339-negative-001.json` — normative rejections.
- `vectors/gus-normative-003.json` — `tgs`/`fgs` blocks (Unix↔instant).

## 5. Maturity and limits

- RFC 3339 profile and Unix bridge: **stable** (vector 002 + negatives).
- UTC is a timescale and RFC 3339 a format: no interface in this domain
  claims NTP synchronisation or certification.
- Dates after the table's `valid_until_unix` raise an extrapolation
  warning (see the TCJ domain).

## 6. References

- `docs/en/comparison/iso-8601-vs-rfc3339-vs-gus.md`,
  `docs/en/audit/AUDIT-REPORT-v3.0.0.md`.
