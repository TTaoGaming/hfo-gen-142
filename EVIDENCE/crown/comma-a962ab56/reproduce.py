#!/usr/bin/env python3
"""Reproduce the Gen142 comma.ai F26 lossless-rate candidate.

This script performs no submission and uses only the public F26 artifact. It
changes representation only: the decoded F24S model bytes and the residual +
RC64 tail must reconstruct exactly.
"""
from __future__ import annotations

import hashlib
import io
import json
import lzma
from pathlib import Path
import struct
import urllib.request
import zipfile

URL = "https://github.com/codexblack/comma_video_compression_challenge/releases/download/semantic-pose-HPAC_CPR1_polished-f26/archive.zip"
INCUMBENT_SHA256 = "12cf5d71a94065184f097c3e40dfe9f1db8402a1a76a80efc76a6956fe1e4004"
INCUMBENT_BYTES = 186_724
EXPECTED_F24S_SHA256 = "4e8d63a98dc7e42ccf17ee7d3fe15a44c8020a3c511838994c6039a673557bde"
EXPECTED_TAIL_SHA256 = "fd3e5617a130d194f65ce1540ed778bedc963ceebc0d5ca1ae64830b425bddb2"
EXPECTED_CANDIDATE_SHA256 = "8e5d806cb3da2e2e4bee2087844cbde1382d2e34ccd13e7c181dbc570c231e0f"
EXPECTED_CANDIDATE_BYTES = 186_709

BASE_FILTER = [{
    "id": lzma.FILTER_LZMA2, "dict_size": 1 << 16,
    "lc": 0, "lp": 1, "pb": 0, "mode": lzma.MODE_NORMAL,
    "nice_len": 273, "mf": lzma.MF_BT4, "depth": 0,
}]
WINNER_FILTER = [{
    "id": lzma.FILTER_LZMA2, "dict_size": 1 << 20,
    "lc": 0, "lp": 1, "pb": 0, "mode": lzma.MODE_NORMAL,
    "nice_len": 32, "mf": lzma.MF_BT2, "depth": 8,
}]
IHS2_BODY_BYTES = 16_593
WANS_BODY_BYTES = 36_040


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pack_n(values: list[int], bits: int, signed: bool = False) -> bytes:
    acc = count = 0
    out = bytearray()
    for value in values:
        if signed:
            lo, hi = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
            if not lo <= value <= hi:
                raise ValueError((value, bits))
            value &= (1 << bits) - 1
        elif not 0 <= value < (1 << bits):
            raise ValueError((value, bits))
        acc = (acc << bits) | value
        count += bits
        while count >= 8:
            count -= 8
            out.append((acc >> count) & 0xFF)
            acc &= (1 << count) - 1 if count else 0
    if count:
        out.append((acc << (8 - count)) & 0xFF)
    return bytes(out)


def unpack_n(raw: bytes, count: int, bits: int, signed: bool = False) -> list[int]:
    values: list[int] = []
    acc = available = offset = 0
    for _ in range(count):
        while available < bits:
            acc = (acc << 8) | raw[offset]
            offset += 1
            available += 8
        available -= bits
        value = (acc >> available) & ((1 << bits) - 1)
        acc &= (1 << available) - 1 if available else 0
        if signed and value & (1 << (bits - 1)):
            value -= 1 << bits
        values.append(value)
    return values


def deterministic_zip(payload: bytes) -> bytes:
    stream = io.BytesIO()
    info = zipfile.ZipInfo("p", date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        archive.writestr(info, payload)
    return stream.getvalue()


def main() -> None:
    incumbent = urllib.request.urlopen(URL, timeout=60).read()
    assert len(incumbent) == INCUMBENT_BYTES
    assert sha256(incumbent) == INCUMBENT_SHA256
    with zipfile.ZipFile(io.BytesIO(incumbent)) as archive:
        assert archive.namelist() == ["p"]
        outer = archive.read("p")

    decoder = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=BASE_FILTER)
    models = decoder.decompress(outer)
    tail = decoder.unused_data
    assert decoder.eof and models[:4] == b"F24S"
    assert sha256(models) == EXPECTED_F24S_SHA256
    assert sha256(tail) == EXPECTED_TAIL_SHA256

    model_offset = 4 + IHS2_BODY_BYTES + WANS_BODY_BYTES
    basis_bits = int.from_bytes(models[model_offset:model_offset + 3], "little")
    residual_bits = int.from_bytes(models[model_offset + 3:model_offset + 6], "little")
    cap_bytes = 6 + 96 + 36 + 32 + 12 + (basis_bits + 7) // 8 + (residual_bits + 7) // 8
    cap = models[model_offset:model_offset + cap_bytes]
    selector = models[model_offset + cap_bytes:]

    offset = 6
    scales = cap[offset:offset + 96]; offset += 96
    predictor = cap[offset:offset + 36]; offset += 36
    lengths = cap[offset:offset + 32]; offset += 32
    rice_ks = cap[offset:offset + 12]; offset += 12
    tail_cap = cap[offset:]

    factors = list(struct.unpack("<12h", predictor[:24]))
    biases = list(struct.unpack("<12b", predictor[24:]))
    basis_lengths = list(struct.unpack("<16H", lengths))
    ks = list(rice_ks)
    assert all(0 <= value <= 255 for value in factors)
    assert all(-32 <= value <= 31 for value in biases)
    assert all(0 <= value < 4096 for value in basis_lengths)
    assert all(0 <= value < 16 for value in ks)

    # F2M1 charges one flags byte. Bit 0=u8 Q8 factors, bit 1=s6 biases,
    # bit 2=u12 basis lengths, bit 3=u4 Rice parameters.
    flags = 0x0F
    compact = (
        bytes((flags,)) + cap[:6] + scales + bytes(factors)
        + pack_n(biases, 6, signed=True)
        + pack_n(basis_lengths, 12)
        + pack_n(ks, 4)
        + tail_cap
    )
    candidate_models = b"F2M1" + models[4:model_offset] + compact + selector

    # Frozen inverse proof: recover the original F24S byte stream exactly.
    pos = 1 + 6 + 96
    f8 = compact[pos:pos + 12]; pos += 12
    b6 = compact[pos:pos + 9]; pos += 9
    l12 = compact[pos:pos + 24]; pos += 24
    k4 = compact[pos:pos + 6]; pos += 6
    rebuilt_cap = (
        compact[1:7] + scales
        + struct.pack("<12h", *list(f8))
        + struct.pack("<12b", *unpack_n(b6, 12, 6, signed=True))
        + struct.pack("<16H", *unpack_n(l12, 16, 12))
        + bytes(unpack_n(k4, 12, 4))
        + compact[pos:]
    )
    reconstructed = b"F24S" + models[4:model_offset] + rebuilt_cap + selector
    assert reconstructed == models
    assert sha256(reconstructed) == EXPECTED_F24S_SHA256

    compressed = lzma.compress(candidate_models, format=lzma.FORMAT_RAW, filters=WINNER_FILTER)
    candidate = deterministic_zip(compressed + tail)
    assert len(candidate) == EXPECTED_CANDIDATE_BYTES
    assert sha256(candidate) == EXPECTED_CANDIDATE_SHA256
    Path("candidate.zip").write_bytes(candidate)
    print(json.dumps({
        "incumbent_bytes": len(incumbent),
        "candidate_bytes": len(candidate),
        "candidate_sha256": sha256(candidate),
        "candidate_model_sha256": sha256(candidate_models),
        "reconstructed_f24s_sha256": sha256(reconstructed),
        "unchanged_tail_sha256": sha256(tail),
        "threshold_beaten": len(candidate) < len(incumbent),
    }, indent=2))


if __name__ == "__main__":
    main()
