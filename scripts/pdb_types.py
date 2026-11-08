"""Read bounded CodeView global-variable sizes from an attested MSF 7 PDB.

Record layouts follow LLVM 18 CodeView TypeRecord / RawTypes definitions.
Unknown leaves, forward declarations and ambiguous storage remain unsupported.
"""
from functools import lru_cache
import struct

from linked_image import LinkedImageError, _msf_streams


def numeric(data, offset):
    value = struct.unpack_from("<H", data, offset)[0]
    if value < 0x8000:
        return value
    formats = {0x8000: "b", 0x8001: "h", 0x8002: "H", 0x8003: "i", 0x8004: "I", 0x8009: "q", 0x800A: "Q"}
    if value not in formats:
        raise LinkedImageError("unsupported CodeView size encoding")
    return struct.unpack_from("<" + formats[value], data, offset + 2)[0]


class Types:
    def __init__(self, data):
        version, header, first, end, size = struct.unpack_from("<5I", data)
        if version != 20040203 or header < 56 or header + size != len(data):
            raise LinkedImageError("invalid TPI stream extent or version")
        self.records = {}
        cursor = header
        for index in range(first, end):
            length = struct.unpack_from("<H", data, cursor)[0]
            if length < 2 or cursor + 2 + length > len(data):
                raise LinkedImageError("invalid TPI record extent")
            kind = struct.unpack_from("<H", data, cursor + 2)[0]
            self.records[index] = kind, data[cursor + 4:cursor + 2 + length]
            cursor += length + 2
        if cursor != len(data):
            raise LinkedImageError("TPI records do not cover their stream")

    @lru_cache(maxsize=None)
    def size(self, index, depth=0):
        if depth > 64:
            return None
        if index < 0x1000:
            mode, kind = (index >> 8) & 15, index & 255
            if mode:
                return {4: 4, 6: 8}.get(mode)
            return {0x10: 1, 0x20: 1, 0x70: 1, 0x71: 2, 0x11: 2, 0x21: 2,
                    0x12: 4, 0x22: 4, 0x74: 4, 0x75: 4, 0x13: 8, 0x23: 8,
                    0x76: 8, 0x77: 8, 0x40: 4, 0x41: 8, 0x30: 1, 0x31: 2,
                    0x32: 4, 0x33: 8, 0x7A: 2, 0x7B: 4}.get(kind)
        if index not in self.records:
            return None
        kind, data = self.records[index]
        if kind == 0x1001:  # LF_MODIFIER
            return self.size(struct.unpack_from("<I", data)[0], depth + 1)
        if kind == 0x1002:  # LF_POINTER: encoded pointer storage size
            return (struct.unpack_from("<I", data, 4)[0] >> 13) & 255 or None
        if kind in {0x1504, 0x1505, 0x1506}:  # CLASS, STRUCTURE, UNION
            if struct.unpack_from("<H", data, 2)[0] & 0x80:
                return None
            return numeric(data, 8 if kind == 0x1506 else 16)
        if kind == 0x1503:  # LF_ARRAY stores its complete byte extent
            return numeric(data, 8)
        if kind == 0x1507:  # LF_ENUM underlying type
            return self.size(struct.unpack_from("<I", data, 4)[0], depth + 1)
        return None


def globals_with_sizes(path, image):
    streams = _msf_streams(path)
    if len(streams) < 4 or streams[2] is None or streams[3] is None:
        raise LinkedImageError("PDB lacks TPI or DBI data")
    types = Types(streams[2])
    stream = struct.unpack_from("<H", streams[3], 20)[0]
    if stream >= len(streams) or streams[stream] is None:
        raise LinkedImageError("PDB lacks its global symbol record stream")
    data = streams[stream]
    cursor = 0
    result = []
    while cursor < len(data):
        length, kind = struct.unpack_from("<HH", data, cursor)
        end = cursor + length + 2
        if length < 2 or end > len(data):
            raise LinkedImageError("invalid global symbol record extent")
        if kind == 0x110D:  # S_GDATA32
            index, offset, section_number = struct.unpack_from("<IIH", data, cursor + 4)
            raw = data[cursor + 14:end]
            if b"\0" not in raw:
                raise LinkedImageError("unterminated global symbol name")
            name = raw.split(b"\0", 1)[0].decode("utf-8")
            size = types.size(index)
            if size is not None and size > 0 and 1 <= section_number <= len(image.sections):
                section = image.section(section_number)
                if not section.characteristics & 0x20 and offset + size <= max(section.virtual_size, section.raw_size):
                    result.append(dict(name=name, type_index=index, size=size,
                                       address=image.image_base + section.rva + offset))
        cursor = end
    return result
