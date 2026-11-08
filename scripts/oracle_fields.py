"""Strict extent coverage and field replay, reused from the TH10 Oracle.

Source: local th10 reconstruction commit 54fbd717d78537c773c8663470115cf93c558ff3.
No instruction similarity or unbound address masking is performed.
"""

def expected_data_spans(
    unit: dict[str, object], compare_size: int, occupied: set[int]
) -> list[dict[str, int]]:
    raw_spans = unit.get("data_spans", [])
    if not isinstance(raw_spans, list):
        raise ValueError("linked unit data_spans must be a list")
    result: list[dict[str, int]] = []
    for raw in raw_spans:
        if not isinstance(raw, dict):
            raise ValueError("linked unit contains an invalid data span")
        offset = int(raw["offset"])
        width = int(raw["width"])
        extent = set(range(offset, offset + width))
        if (
            width <= 0
            or offset < 0
            or offset + width > compare_size
            or occupied & extent
        ):
            raise ValueError("linked unit contains an invalid data-span extent")
        occupied.update(extent)
        result.append({"offset": offset, "width": width})
    result.sort(key=lambda row: int(row["offset"]))
    if result:
        cursor = compare_size - sum(int(row["width"]) for row in result)
        for row in result:
            if int(row["offset"]) != cursor:
                raise ValueError(
                    "linked unit data spans must form one contiguous trailing extent"
                )
            cursor += int(row["width"])
        if cursor != compare_size:
            raise ValueError("linked unit data spans leave a trailing gap")
    return result


def require_decode_coverage(
    field_report: dict[str, object], data_spans: list[dict[str, int]], size: int
) -> None:
    if field_report["normalization_complete"]:
        if data_spans:
            raise ValueError(
                "linked unit declares data spans despite complete Capstone normalization"
            )
        return
    decoded = int(field_report["decoded_bytes"])
    if not 0 <= decoded <= size:
        raise ValueError("linked decoder extent leaves the compared contribution")
    if not data_spans:
        raise ValueError(f"Capstone decoded {decoded} of {size} bytes")
    covered = set(range(decoded))
    # Absolute table entries are already accounted for by authoritative PE
    # relocations. An unlinked selector suffix may follow those entries.
    for field in field_report["fields"]:
        if field["type"] == "DIR32" and int(field["width"]) == 4:
            covered.update(range(int(field["offset"]), int(field["offset"]) + 4))
    for span in data_spans:
        if int(span["offset"]) < decoded:
            raise ValueError("data spans overlap the decoded instruction extent")
        covered.update(range(int(span["offset"]), int(span["offset"]) + int(span["width"])))
    if not set(range(size)).issubset(covered):
        raise ValueError(
            "complete PE fields and declared data spans do not cover the undecoded trailing extent"
        )


def pack_linked_value(
    code: bytearray,
    field: dict[str, object],
    instruction_end: int | None,
    target_address: int,
) -> int:
    kind = str(field["type"])
    width = int(field["width"])
    destination = int(field["target"]) + int(field["addend"])
    if kind == "DIR32":
        if not 0 <= destination <= 0xFFFFFFFF:
            raise ValueError("DIR32 replay value leaves the 32-bit address space")
        encoded = destination
        code[int(field["offset"]) : int(field["offset"]) + width] = encoded.to_bytes(
            width, "little"
        )
        return encoded
    if instruction_end is None:
        raise ValueError(f"{kind} field lacks a decoded instruction end")
    encoded = destination - (target_address + instruction_end)
    minimum = -(1 << (width * 8 - 1))
    maximum = (1 << (width * 8 - 1)) - 1
    if not minimum <= encoded <= maximum:
        raise ValueError(f"{kind} replay displacement is out of range")
    code[int(field["offset"]) : int(field["offset"]) + width] = encoded.to_bytes(
        width, "little", signed=True
    )
    return encoded
