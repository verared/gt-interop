# SPDX-License-Identifier: MIT OR Apache-2.0
# SPDX-FileCopyrightText: 2026 verared contributors
"""Perfil GUS-3161: la marca GUS viaja dentro de RFC 3161 (TSA existentes).

Documento normativo: docs/profiles/gus-3161-perfil.md (ES espejo) /
docs/en/profiles/gus-3161-profile.md (EN normativo). Las pruebas usan un
TSA local efímero (openssl ts); no requieren red ni servicio externo.

Regla del perfil (resumen — el texto normativo es el .md):

- El dato sellado por la TSA es exactamente el bundle canónico de la GST
  (o los bytes que el usuario ancle). La TSA certifica la EXISTENCIA de
  esos bytes en su genTime; el notario GUS certifica el orden. Los dos
  sellos son complementarios, no redundantes.
- El genTime (UTC) de la TSA se convierte a instante GUS con el perfil
  GUS-3339 y se registra en el sidecar JSON:
      {"type": "gus3161-001", "gst_sha256": ..., "tsa_gen_time": "<RFC3339Z>",
       "tsa_gen_time_gus_instant": <int>, "token_b64": <TSR en base64>}
- Verificación offline: `openssl ts -verify -data <bundle> -in <tsr>`
  contra el trust root TSA que el verificador declare.

Este módulo solo orquesta el binario `openssl` (subprocess, stdlib puro).
Si `openssl ts` no está disponible, las funciones lo declaran con
RuntimeError — el perfil degrada explícitamente, nunca silenciosamente.
"""

from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from . import profiles

SIDECAR_TYPE = "gus3161-001"

# OID de política de referencia del perfil (bajo PEN 1373 de la spec;
# el TSA real usa su propia política — va registrada en el sidecar).
REF_POLICY_OID = "1.3.6.1.5.5.7.1.1"


def openssl_available() -> bool:
    return shutil.which("openssl") is not None


def _run(args: list, input_bytes: Optional[bytes] = None) -> bytes:
    proc = subprocess.run(
        ["openssl", *args],
        input=input_bytes,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"openssl {' '.join(args)} falló: {proc.stderr.decode(errors='replace')[:300]}"
        )
    return proc.stdout


def timestamp_request(data: bytes) -> bytes:
    """Genera la consulta de sellado: TSQ (DER) por el SHA-256 de `data` (RFC 3161).

    `-cert` pide la cadena de la TSA dentro de la respuesta (autocontenido).
    """
    if not openssl_available():
        raise RuntimeError("openssl no está disponible: perfil GUS-3161 inactivo")
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "data.bin"
        p.write_bytes(data)
        return _run(["ts", "-query", "-sha256", "-cert", "-data", str(p)])


def timestamp_reply(req: bytes, tsa_key: bytes, tsa_cert: bytes,
                    chain: Optional[bytes] = None) -> bytes:
    """TSA local de pruebas: responde un TSR (DER, TS_RESP) para la TSQ dada.

    `tsa_key`/`tsa_cert` son la identidad TSA (solo para pruebas; las claves
    viven y mueren en el proceso del test, nunca se versionan). La identidad
    necesita EKU critical timeStamping y keyUsage digitalSignature+nonRepudiation;
    `chain` es la cadena CA opcional (PEM) que se embebe en la respuesta.
    Se pasa `-config` propio para no depender del openssl.cnf de la máquina.
    """
    if not openssl_available():
        raise RuntimeError("openssl no está disponible: perfil GUS-3161 inactivo")
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        (tmpd / "req.tsq").write_bytes(req)
        (tmpd / "tsa.key").write_bytes(tsa_key)
        (tmpd / "tsa.pem").write_bytes(tsa_cert)
        chain_files = ""
        if chain:
            (tmpd / "chain.pem").write_bytes(chain)
            chain_files = str(tmpd / "chain.pem")
        conf = _tsa_conf(tmpd, tsa_cert_path=str(tmpd / "tsa.pem"),
                         chain_path=chain_files)
        (tmpd / "ts.conf").write_text(conf)
        (tmpd / "serial").write_text("1000\n")
        (tmpd / "serial").write_text("1000\n")
        return _run(
            [
                "ts", "-reply",
                "-config", str(tmpd / "ts.conf"),
                "-queryfile", str(tmpd / "req.tsq"),
                "-signer", str(tmpd / "tsa.pem"),
                "-inkey", str(tmpd / "tsa.key"),
                "-passin", "pass:",
            ]
        )


def _tsa_conf(tmpd: Path, tsa_cert_path: str, chain_path: str) -> str:
    certs = f"{tsa_cert_path}, {chain_path}" if chain_path else tsa_cert_path
    return f"""[tsa]
default_tsa = tsa_config1
[tsa_config1]
dir = {tmpd}
serial = {tmpd}/serial
signer_cert = {tsa_cert_path}
certs = {certs}
signer_digest = sha256
default_policy = 1.3.6.1.5.5.7.48.3.8
other_policies = 1.3.6.1.5.5.7.48.3.9
digests = sha256, sha384, sha512
ess_cert_id_alg = sha256
ess_cert_id_chain = no
tsa_name = yes
ordering = no
accuracy = secs:1, millisecs:0, microsecs:0
clock_precision_digits = 0
crypto_device = builtin
"""


def verify_token(token: bytes, data: bytes, trusted_certs: bytes) -> bool:
    """Verifica un TSR (DER, TS_RESP) contra el dato sellado y certs de confianza.

    `trusted_certs` es un PEM (CA raíz o TSA autofirmada; puede concatenar
    varios PEM). Con la TSA local de pruebas, el propio cert TSA hace de
    trust root.
    """
    if not openssl_available():
        raise RuntimeError("openssl no está disponible: perfil GUS-3161 inactivo")
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        tmpd.joinpath("tok.tsr").write_bytes(token)
        tmpd.joinpath("data.bin").write_bytes(data)
        tmpd.joinpath("trust.pem").write_bytes(trusted_certs)
        proc = subprocess.run(
            ["openssl", "ts", "-verify",
             "-data", str(tmpd / "data.bin"),
             "-in", str(tmpd / "tok.tsr"),
             "-CAfile", str(tmpd / "trust.pem"),
             "-untrusted", str(tmpd / "trust.pem")],
            capture_output=True,
        )
        return proc.returncode == 0


def gen_time_from_token(token: bytes) -> str:
    """Extrae el genTime del TSR (DER) y lo normaliza a RFC 3339 Z (perfil GUS-3339).

    RFC 3161 porta el genTime en GeneralizedTime (siempre). Caminante ASN.1
    mínimo, stdlib puro — sin depender del formato `-text` del binario
    openssl. Un TSR contiene un único genTime; si aparecieran varios,
    se toma el primero. Fracciones: si la TSA emitió precisión sub-segundo,
    se TRUNCA a segundos (el lado forense GUS registra la cota; ver el .md).
    """
    times = [n for n, tag in _asn1_walk(token) if tag in (0x17, 0x18)]  # UTCTime/GeneralizedTime
    if not times:
        raise RuntimeError("no se encontró genTime en el token TSR")
    digits = times[0].decode("ascii", errors="strict")
    # GeneralizedTime: AAAAMMDDHHMMSS[.fff]Z — UTCTime: AAMMDDHHMMSSZ
    if len(digits) > 6 and digits[0] in "19" and digits[1] in "0123456789" and digits[0:2] in (
        "19", "20"
    ) and "Z" in digits and len(digits) >= 15:
        year, rest = int(digits[:4]), digits[4:]
    else:  # UTCTime (openssl emite UTCTime para años 1950..2049)
        yy, rest = int(digits[:2]), digits[2:]
        if rest[0] == "9":
            raise RuntimeError(f"genTime unreadable: {digits!r}")
        year = 2000 + yy if yy < 50 else 1900 + yy
    if "." in rest:
        rest = rest.split(".")[0]
    rest = rest.rstrip("Z")
    return f"{year:04d}-{int(rest[0:2]):02d}-{int(rest[2:4]):02d}T" \
           f"{int(rest[4:6]):02d}:{int(rest[6:8]):02d}:{int(rest[8:10]):02d}Z"


def _asn1_walk(data: bytes, _start: int = 0, _end: int = None):
    """Itera los TLV de un DER: cede (contenido, tag) recursivamente.

    Suficiente para encontrar UTCTime/GeneralizedTime en un PKCS#7/TSR:
    sin validación de OID ni esquemas, solo estructura.
    """
    if _end is None:
        _end = len(data)
    i = _start
    out = []
    while i < _end:
        try:
            tag = data[i]
            idx = i + 1
            b = data[idx]
            idx += 1
            if b & 0x80:
                n = b & 0x7F
                if n == 0 or n > 4:
                    break
                length = int.from_bytes(data[idx:idx + n], "big")
                idx += n
            elif b == 0x80 or b == 0x81:
                break  # indefinido: un TSR real SIEMPRE es longitud definida
            else:
                length = b
            content = data[idx:idx + length]
            if len(content) < length:
                break
            if tag == 0x17 or tag == 0x18:  # UTCTime / GeneralizedTime: hojas
                out.append((content, tag))
            elif tag & 0x20:  # construido: recurse
                out.extend(_asn1_walk(data, idx, idx + length))
            i = idx + length
        except (IndexError, ValueError):
            break
    return out


def attach_sidecar(gst_json: str, token: bytes,
                   gen_time_rfc3339: Optional[str] = None) -> str:
    """Construye el sidecar JSON del perfil a partir del token TSR.

    El genTime (UTC) se toma del argumento si se pasa; en su defecto se
    extrae del propio token (ver :func:`gen_time_from_token`).
    """
    if gen_time_rfc3339 is None:
        gen_time_rfc3339 = gen_time_from_token(token)
    ins = profiles.instant_from_rfc3339(gen_time_rfc3339)
    doc = json.loads(gst_json) if isinstance(gst_json, str) else gst_json
    gst_sha = hashlib.sha256(
        json.dumps(doc, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return json.dumps(
        {
            "type": SIDECAR_TYPE,
            "gst_sha256": gst_sha,
            "tsa_gen_time": gen_time_rfc3339,
            "tsa_gen_time_gus_instant": ins,
            "token_b64": base64.b64encode(token).decode("ascii"),
        },
        indent=2,
        ensure_ascii=False,
    )
