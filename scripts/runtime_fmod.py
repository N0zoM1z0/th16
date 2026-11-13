"""Closed pinned x87 fmod family identity; no generic runtime interior aliases."""
import hashlib
from pathlib import Path
import struct

from linked_image import LinkedImageError, linked_code_fields, pdb_section_contributions
from runtime_identity import RuntimeEvidenceError, decode_scope, readonly, require


PARTS = {
    "fmod": ("_fmod", "87fmod.obj", 34, 80),
    "dispatch": ("__trandisp1", "87disp.obj", 500, 62),
    "c_dispatch": ("__cintrindisp2", "87cdisp.obj", 645, 48),
}
FIELDS = {
    "fmod": [(1, "DIR32"), (6, "REL32"), (11, "DIR32"), (16, "REL32")],
    "dispatch": [(x, "DIR32") for x in [41, 144, 325, 441, 470, 486]],
    "c_dispatch": sorted([(x, "REL32") for x in [22, 34, 89, 101, 188, 517, 573]]
                         + [(x, "DIR32") for x in [209, 358, 374, 386, 404, 420, 432]]),
}


def unique_public(context, name, producer):
    rows = [p for p in context.publics if p["symbol"] == name]
    require(len(rows) == 1 and rows[0]["object"].lower() == "libucrt:" + producer,
            "fmod public leaves its unique pinned producer")
    return rows[0]["address"]


def virtual_zero(image, address):
    rows = [s for s in image.sections if image.image_base+s.rva+s.raw_size <= address
            and address+4 <= image.image_base+s.rva+s.virtual_size]
    require(len(rows) == 1 and rows[0].characteristics & 0xc0000000 == 0xc0000000
            and not rows[0].characteristics & 0x20000020 and address % 4 == 0,
            "fmod fast flag lacks its complete writable virtual zero storage")


def review_fmod(context, row):
    keys = {"profile", "evidence", "fastflag_address", "witness_parent", "witness_parent_sha256", "witnesses"}
    keys |= {name+suffix for name in PARTS for suffix in ["_address", "_sha256", "_data_address", "_data_sha256"]}
    require(set(row) == keys and row["profile"] == "msvc-x86-fmod-v1",
            "unreviewed fmod family declaration")
    require(all(type(row[n+suffix]) is int for n in PARTS for suffix in ["_address", "_data_address"])
            and type(row["fastflag_address"]) is int, "fmod family addresses must be integral")
    root = Path(__file__).resolve().parents[1]
    library = "Z:" + str(root/".tools/toolchain/sdk/Program Files/Windows Kits/10/Lib/10.0.10240.0/ucrt/x86/libucrt.lib")
    normalize = lambda x: str(x).replace("\\", "/").lower()
    pdb = pdb_section_contributions(context.directory/"th16.pdb")["contributions"]
    parts = {}
    for name,(symbol,producer,size,data_size) in PARTS.items():
        target, data_target = row[name+"_address"], row[name+"_data_address"]
        original = context.target.read_address(target,size)
        data = context.target.read_address(data_target,data_size)
        require(hashlib.sha256(original).hexdigest() == row[name+"_sha256"], "fmod original code hash differs")
        require(hashlib.sha256(data).hexdigest() == row[name+"_data_sha256"], "fmod original data hash differs")
        require(not any(target-3 <= a < target+size or data_target-3 <= a < data_target+data_size
                        for a in context.target.base_relocations()),
                "fmod original fixed contribution unexpectedly relocates")
        owners = [f for f in context.linked["functions"] if f["symbol"] == symbol]
        require(len(owners) == 1 and owners[0]["size"] == size, "fmod lacks its complete code owner")
        owner = owners[0]
        require(normalize(owner["pdb_object"]) == normalize(library)
                and owner["map_object"].lower() == "libucrt:"+producer,
                "fmod code owner leaves pinned UCRT")
        address = unique_public(context,symbol,producer)
        require(address == int(owner["address"],0), "fmod public does not begin its complete parent")
        records = [p for p in pdb if p["module_index"] == owner["pdb_module_index"]]
        code = [p for p in records if p["characteristics"] & 0x20]
        pools = [p for p in records if not p["characteristics"] & 0x20]
        require(len(records) == 2 and len(code) == len(pools) == 1
                and code[0]["size"] == size and pools[0]["size"] == data_size
                and all(normalize(p["object"]) == normalize(library)
                        and p["module"] == owner["pdb_module"] for p in records),
                "fmod requires all complete code/data contributions from each producer")
        record_address = lambda p: context.image.image_base+context.image.section(p["section_number"]).rva+p["section_offset"]
        require(record_address(code[0]) == address, "fmod code contribution starts elsewhere")
        data_address = record_address(pools[0])
        if name != "fmod":
            require(readonly(context.target,data_target,data_size) == readonly(context.image,data_address,data_size),
                    "fmod complete constant pool replay differs")
        else:
            for image, at in [(context.target,data_target),(context.image,data_address)]:
                require(any(not s.characteristics & (0x20|0x80000000)
                            and image.image_base+s.rva <= at and at+80 <= image.image_base+s.rva+s.raw_size
                            for s in image.sections), "fmod descriptor leaves complete read-only storage")
        parts[name] = dict(target=target,candidate=address,size=size,data_target=data_target,
                           data_candidate=data_address,data_size=data_size,original=original,data=data,owner=owner)
    fmod, dispatch, c_dispatch = [parts[n] for n in PARTS]
    for name,offset,producer,parent in [
        ("__CIfmod",10,"87fmod.obj",fmod),
        ("__trandisp2",103,"87disp.obj",dispatch),
        ("__cintrindisp1",68,"87cdisp.obj",c_dispatch),
        ("__ctrandisp2",135,"87cdisp.obj",c_dispatch)]:
        require(unique_public(context,name,producer) == parent["candidate"]+offset,
                "fmod entry public differs from its fixed complete parent offset")
    require(unique_public(context,"__OP_FMODjmptab","87fmod.obj") == fmod["data_candidate"],
            "fmod descriptor public starts elsewhere")
    fastflag = unique_public(context,"___fastflag","fp_flags.obj")
    typed = [p for p in context.typed_globals if p["name"] == "__fastflag"]
    require(len(typed) == 1 and typed[0]["address"] == fastflag and typed[0]["size"] == 4
            and typed[0]["type_index"] == 0x74, "fmod fast flag lacks its complete typed integer")
    virtual_zero(context.target,row["fastflag_address"]); virtual_zero(context.image,fastflag)
    external = {}
    for symbol,size in [("___acrt_has_user_matherr",25),("__87except",267)]:
        binding = context.reviewed_linkages.get(symbol,{})
        publics = [p for p in context.publics if p["symbol"] == symbol]
        require(binding.get("kind") == "runtime-function" and binding.get("size") == size and len(publics) == 1,
                "fmod external edge lacks its complete reviewed runtime identity")
        external[publics[0]["address"]] = binding["target"]
    for name in PARTS:
        p = parts[name]
        try:
            fields = linked_code_fields(context.image,context.publics,p["candidate"],p["size"])
        except LinkedImageError as error:
            raise RuntimeEvidenceError("fmod complete linked fields are invalid: " + str(error)) from error
        require(fields["normalization_complete"] and fields["decoded_bytes"] == p["size"]
                and sorted((f["offset"],f["type"]) for f in fields["fields"]) == FIELDS[name]
                and all(f["width"] == 4 for f in fields["fields"]), "fmod complete field set differs")
        relocations = {a-p["candidate"] for a in context.image.base_relocations()
                       if p["candidate"]-3 <= a < p["candidate"]+p["size"]}
        require(relocations == {f["offset"] for f in fields["fields"] if f["type"] == "DIR32"},
                "fmod complete code relocation footprint differs")
        patched = bytearray(context.image.read_address(p["candidate"],p["size"]))
        for field in fields["fields"]:
            value = field["candidate_target"]
            if field["type"] == "DIR32":
                if p["data_candidate"] <= value < p["data_candidate"]+p["data_size"]:
                    value = p["data_target"]+value-p["data_candidate"]
                else:
                    require(name == "c_dispatch" and field["offset"] == 209 and value == fastflag,
                            "fmod address field leaves its reviewed data roles")
                    value = row["fastflag_address"]
            else:
                expected = {("fmod",6):(c_dispatch,135), ("fmod",16):(c_dispatch,0),
                            ("c_dispatch",34):(dispatch,103), ("c_dispatch",101):(dispatch,0),
                            ("c_dispatch",188):(dispatch,103), ("c_dispatch",573):(dispatch,0)}
                pair = expected.get((name,field["offset"]))
                if pair:
                    parent,offset = pair
                    require(value == parent["candidate"]+offset, "fmod internal family edge differs")
                    value = parent["target"]+offset
                else:
                    require(name == "c_dispatch" and field["offset"] in [22,89,517] and value in external,
                            "fmod external family edge differs")
                    value = external[value]
                value -= p["target"]+field["instruction_end"]
            struct.pack_into("<I",patched,field["offset"],value & 0xffffffff)
        require(bytes(patched) == p["original"], "fmod complete code replay differs")
    descriptor = bytearray(context.image.read_address(fmod["data_candidate"],80))
    relocs = {a-fmod["data_candidate"] for a in context.image.base_relocations()
              if fmod["data_candidate"]-3 <= a < fmod["data_candidate"]+80}
    require(relocs == set(range(16,80,4)), "fmod descriptor requires exactly all sixteen pointer relocations")
    require(descriptor[:16] == fmod["data"][:16] and descriptor[:5] == b"\x04fmod",
            "fmod operation descriptor header differs")
    for offset in range(16,80,4):
        value = struct.unpack_from("<I",descriptor,offset)[0]
        if offset == 16:
            require(value == fmod["candidate"]+20, "fmod private FPREM callback differs")
            value = fmod["target"]+20
        else:
            require(dispatch["candidate"] <= value < dispatch["candidate"]+500,
                    "fmod descriptor handler leaves the complete dispatcher")
            value += dispatch["target"]-dispatch["candidate"]
        struct.pack_into("<I",descriptor,offset,value)
    require(bytes(descriptor) == fmod["data"], "fmod complete descriptor replay differs")
    for name,before,after in [("fmod",12,14),("dispatch",9,12),("c_dispatch",8,11)]:
        p = parts[name]
        require(context.target.read_address(p["target"]-before,before) == b"\xcc"*before
                and context.target.read_address(p["target"]+p["size"],after) == b"\xcc"*after,
                "fmod original complete contribution padding differs")
    parent = row["witness_parent"]; boundary = context.boundaries.get(parent)
    require(parent == 0x417bc0 and boundary and int(boundary["size"]) == 418
            and int(boundary["span_end"],0) == parent+417
            and hashlib.sha256(context.target.read_address(parent,418)).hexdigest() == row["witness_parent_sha256"],
            "fmod witness requires the complete original spellcard parent")
    instructions,_ = decode_scope(context.target,parent,418,[0])
    calls = {i.address:i for i in instructions if i.mnemonic == "call"}
    call = calls.get(parent+106)
    require(row["witnesses"] == [parent+106] and call is not None and call.size == 5
            and bytes(call.bytes)[0] == 0xe8 and call.operands[0].imm == fmod["target"]+10,
            "fmod interior lacks its fixed original x87 CALL witness")
    binding = dict(target=fmod["target"]+10,kind="runtime-interior-v1",candidate=fmod["candidate"]+10,
                   parent_target=fmod["target"],parent_candidate=fmod["candidate"],parent_size=34,
                   entry_offset=10,evidence=row["evidence"])
    evidence = dict(profile=row["profile"],code_bytes=1179,data_bytes=190,entry_offset=10,
                    complete_code_equal=True,complete_data_equal=True,primary_exact_credit=0,
                    parents={n:{k:v for k,v in p.items() if k not in ["original","data"]} for n,p in parts.items()})
    return {"__CIfmod":binding},evidence
