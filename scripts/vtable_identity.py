"""Prove reviewed PE32 primary vftable identities from complete storage and RTTI."""
from __future__ import annotations

from collections import defaultdict
import re
import struct

from linked_image import LinkedImageError


class VftableEvidenceError(ValueError):
    pass


def review_vftable(context, row, candidate, reviewed):
    """Identify an address point; grant no exact claim to RTTI, slots or callees."""
    try:
        return _review(context, row, candidate, reviewed)
    except (LinkedImageError, struct.error) as error:
        raise VftableEvidenceError("unmapped or malformed vftable evidence") from error


def _review(context, row, candidate, reviewed):
    def require(condition, message):
        if not condition:
            raise VftableEvidenceError(message)

    match = re.fullmatch(r"\?\?_7(.+@@)6B@", row["symbol"])
    require(match is not None, "vftable public is not a primary address point")
    require(match[1].isascii(), "unsupported non-ASCII vftable public")
    stem = match[1].encode("ascii")
    size, original = int(row["size"]), int(row["target_address"], 0)
    require(0 < size <= 1024 and size % 4 == 0 and candidate % 4 == 0 and original % 4 == 0,
            "invalid complete vftable slot extent")
    require(not any(row.get(k) for k in ("candidate_library", "candidate_size",
                                         "witness_instruction", "witness_mnemonic")),
            "vftable evidence mixes incompatible witness schemas")

    def storage(image, address, length, readonly=True):
        require(length > 0 and any(
            section.characteristics & 0x40000000 and not section.characteristics & (0x20 | 0x20000000)
            and (not readonly or not section.characteristics & 0x80000000)
            and image.image_base + section.rva <= address
            and address + length <= image.image_base + section.rva + max(section.raw_size, section.virtual_size)
            for section in image.sections), "vftable evidence leaves mapped read-only data")
        return image.read_address(address, length)

    def owned(address, length):
        require(context.data_contributions.get(address) == [length],
                "vftable evidence lacks one complete PDB storage contribution")

    def code(image, address, length=1):
        return any(section.characteristics & 0x20000000
                   and image.image_base + section.rva <= address
                   and address + length <= image.image_base + section.rva + max(section.raw_size, section.virtual_size)
                   for section in image.sections)

    def words(data):
        return struct.unpack("<" + "I" * (len(data) // 4), data)

    owned(candidate - 4, size + 4)
    relocations = set(context.image.base_relocations())
    actual = {a for a in relocations if candidate - 4 <= a < candidate + size}
    require(actual == set(range(candidate - 4, candidate + size, 4)),
            "vftable lacks its complete relocated pointer storage")

    def rtti(image, address, candidate_image):
        visiting, completed, definitions, types = set(), set(), {}, {}

        def typed_name(descriptor):
            if descriptor in types:
                return types[descriptor]
            header = words(storage(image, descriptor, 8, readonly=False))
            require(header[1] == 0, "unsupported initialized RTTI type cache")
            storage(image, header[0], 4)
            value = bytearray()
            for offset in range(512):
                byte = storage(image, descriptor + 8 + offset, 1, readonly=False)[0]
                if byte == 0:
                    break
                require(0x20 <= byte < 0x7f, "unsupported RTTI type name")
                value.append(byte)
            else:
                raise VftableEvidenceError("unterminated RTTI type name")
            require(bytes(value).startswith((b".?AV", b".?AU")) and bytes(value).endswith(b"@@"),
                    "unsupported RTTI class-name encoding")
            if candidate_image:
                owned(descriptor, 8 + len(value) + 1)
            types[descriptor] = bytes(value)
            return bytes(value)

        def hierarchy(address, own_type):
            key = (address, own_type)
            if key in completed:
                return
            require(key not in visiting, "cyclic RTTI base inheritance")
            require(len(visiting) + len(completed) < 128, "RTTI hierarchy exceeds the supported finite graph")
            visiting.add(key)
            header = words(storage(image, address, 16))
            require(header[0:2] == (0, 0) and 1 <= header[2] <= 64,
                    "unsupported multiple, virtual or malformed RTTI hierarchy")
            count, array = header[2:4]
            payload = storage(image, array, count * 4 + 1)
            require(payload[-1] == 0, "RTTI base array lacks its complete trailing byte")
            if candidate_image:
                owned(address, 16)
                owned(array, count * 4 + 1)
            entries = []
            for index, base in enumerate(words(payload[:-1])):
                fields = words(storage(image, base, 28))
                if candidate_image:
                    owned(base, 28)
                # A base without its own vftable follows the derived class's
                # vptr, at member displacement 4; the class itself stays at 0.
                require(fields[2] in ((0,) if index == 0 else (0, 4))
                        and fields[3:5] == (0xffffffff, 0) and fields[5] == 0x40,
                        "unsupported RTTI base displacement or attributes")
                if index == 0:
                    require(fields[0] == own_type and fields[1] == count - 1 and fields[6] == address,
                            "RTTI hierarchy does not describe its own complete class")
                require(fields[1] == count - index - 1, "unsupported RTTI base containment")
                entries.append((typed_name(fields[0]), *fields[1:6]))
                if index:
                    require(fields[0] != own_type, "cyclic RTTI self inheritance")
                    hierarchy(fields[6], fields[0])
            name = typed_name(own_type)
            definition = tuple(entries)
            require(name not in definitions or definitions[name] == definition,
                    "conflicting RTTI definitions of one class")
            definitions[name] = definition
            visiting.remove(key)
            completed.add(key)

        locator = words(storage(image, address - 4, size + 4))[0]
        fields = words(storage(image, locator, 20))
        require(fields[:3] == (0, 0, 0), "unsupported non-primary or construction vftable locator")
        if candidate_image:
            owned(locator, 20)
        name = typed_name(fields[3])
        require(name in (b".?AV" + stem, b".?AU" + stem), "RTTI class differs from the vftable public")
        hierarchy(fields[4], fields[3])
        return name, definitions

    candidate_rtti = rtti(context.image, candidate, True)
    target_rtti = rtti(context.target, original, False)
    require(candidate_rtti == target_rtti, "candidate and target RTTI class hierarchies differ")
    after = words(storage(context.target, original + size, 4))[0]
    require(not code(context.target, after), "original vftable slot extent is truncated")

    # These fixed function identities predate this consumer comparison. Unknown
    # or conflicting symbols never acquire an identity from the observed slot.
    bindings = defaultdict(set)
    for line in (context.directory / "functions.txt").read_text().splitlines():
        target, address, _ = line.split()
        bindings[int(address, 16)].add(int(target, 16))
    for symbol, entry in reviewed.items():
        if entry["kind"] != "runtime-function":
            continue
        publics = [p for p in context.publics if p["symbol"] == symbol]
        if len(publics) == 1:
            bindings[publics[0]["address"]].add(entry["target"])
    left = words(storage(context.image, candidate, size))
    right = words(storage(context.target, original, size))
    for candidate_slot, target_slot in zip(left, right):
        records = [f for f in context.linked["functions"] if int(f["address"], 0) == candidate_slot]
        owners = {(f["size"], f["pdb_object"], f["pdb_module_index"]) for f in records}
        require(code(context.target, target_slot) and len(owners) == 1
                and all(f["extent_source"] == "pdb-section-contribution" and f["size"] > 0
                        and code(context.image, candidate_slot, f["size"]) for f in records)
                and target_slot in context.boundaries
                and bindings.get(candidate_slot) == {target_slot},
                "vftable slot lacks one complete owner and an independent function identity")
    return {"class": candidate_rtti[0].decode("ascii"), "slots": size // 4}
