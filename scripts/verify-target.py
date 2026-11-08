#!/usr/bin/env python3
"""Attest the private PE against the tracked TH16 manifest."""
import argparse
import hashlib
from pathlib import Path
import struct
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def verify(path=None):
    manifest = tomllib.loads((ROOT / "config/target.toml").read_text())
    target, pe = manifest["target"], manifest["pe"]
    path = Path(path) if path else ROOT / "resources" / target["filename"]
    data = path.read_bytes()
    if len(data) != target["size"]:
        raise ValueError("target size mismatch")
    for algorithm in ("sha256", "sha1", "md5"):
        if hashlib.new(algorithm, data).hexdigest() != target[algorithm]:
            raise ValueError(f"target {algorithm} mismatch")
    offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[:2] != b"MZ" or data[offset:offset + 4] != b"PE\0\0":
        raise ValueError("target is not a PE image")
    machine, count = struct.unpack_from("<HH", data, offset + 4)
    optional = offset + 24
    magic = struct.unpack_from("<H", data, optional)[0]
    entry = struct.unpack_from("<I", data, optional + 16)[0]
    base = struct.unpack_from("<I", data, optional + 28)[0]
    image_size = struct.unpack_from("<I", data, optional + 56)[0]
    if (machine, count, magic, base, base + entry, image_size) != (
        pe["machine_id"], pe["section_count"], 0x10B,
        int(pe["image_base"], 0), int(pe["entry_point"], 0), pe["size_of_image"]
    ):
        raise ValueError("PE metadata mismatch")
    return manifest, data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?")
    args = parser.parse_args()
    manifest, _ = verify(args.path)
    print(f"TH16 target verified: {manifest['target']['sha256']}")
