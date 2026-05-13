import hashlib
import struct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Case


FREESECT = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT = 0xFFFFFFFD
OLE_SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def import_legacy_ppp(data: bytes, filename: str = "legacy.ppp") -> "Case":
    contents = extract_ole_stream(data, "Contents")
    return import_contents_stream(contents, filename, data)


def import_contents_stream(contents: bytes, filename: str = "legacy.ppp", source_data: bytes | None = None) -> "Case":
    project_name = read_ascii_string(contents, 0x0004)
    run_id = read_ascii_string(contents, 0x001f)
    stern_label = read_ascii_string(contents, 0x008c)
    propulsion_label = read_ascii_string(contents, 0x00bf)
    return {
        "schema": "navarch.ppp.case",
        "version": 1,
        "source": {
            "legacy_file": filename,
            "sha256": hashlib.sha256(source_data if source_data is not None else contents).hexdigest(),
            "format": "OLE Compound Document" if source_data is not None else "Contents stream",
            "stream": "Contents",
            "stream_size": len(contents),
            "confidence": "binary_offset_parse"
        },
        "project": {
            "name": project_name,
            "run_id": run_id
        },
        "speed_sweep": {
            "initial_speed_knots": read_double(contents, 0x01f6),
            "speed_increment_knots": read_double(contents, 0x01fe),
            "status": "candidate_from_binary_offsets"
        },
        "hull": {
            "lwl_m": read_double(contents, 0x0028),
            "beam_lwl_m": read_double(contents, 0x0030),
            "draft_forward_m": read_double(contents, 0x0038),
            "draft_aft_m": read_double(contents, 0x0040),
            "block_coefficient": read_double(contents, 0x0048),
            "midship_coefficient": read_double(contents, 0x0050),
            "waterplane_coefficient": read_double(contents, 0x0058),
            "lcb_percent_lwl_from_midships_forward_positive": read_double(contents, 0x0060)
        },
        "features": {
            "bulb_area_station_0_m2": read_double(contents, 0x0078),
            "bulb_vertical_center_m": read_double(contents, 0x0070),
            "transom_immersed_area_zero_speed_m2": read_double(contents, 0x0068),
            "stern_type": normalize_stern(stern_label)
        },
        "propulsion": {
            "type": normalize_propulsion(propulsion_label),
            "propeller_diameter_m": read_double(contents, 0x00a3),
            "expanded_area_ratio": read_double(contents, 0x00ab),
            "pitch_diameter_ratio": None
        },
        "appendages": {
            "mode": "percent_bare_hull_resistance",
            "percent_bare_hull_resistance": read_double(contents, 0x00e6) * 100,
            "equivalent_wetted_area_form_factor_m2": None
        },
        "modeling": {
            "air_drag": True,
            "depth_at_bow_m": read_double(contents, 0x01ae),
            "deckhouse_cargo_frontal_area_m2": read_double(contents, 0x01b6),
            "wetted_surface_mode": "user",
            "wetted_surface_m2": read_double(contents, 0x01be),
            "half_angle_entrance_mode": "user",
            "half_angle_entrance_degrees": read_double(contents, 0x01c6)
        },
        "water": {
            "type": "salt_water_15_c",
            "density_kg_m3": read_double(contents, 0x01e2),
            "kinematic_viscosity_m2_s": read_double(contents, 0x01ea)
        },
        "margin": {
            "design_margin_percent": read_double(contents, 0x01da) * 100
        },
        "legacy_labels": {
            "stern_type": stern_label,
            "propulsion_type": propulsion_label,
            "water_type": "Salt Water at 15 degrees Celsius"
        }
    }


def extract_ole_stream(data, stream_name):
    if data[:8] != OLE_SIGNATURE:
        raise ValueError("not an OLE Compound Document")
    sector_shift = struct.unpack_from("<H", data, 0x1e)[0]
    mini_sector_shift = struct.unpack_from("<H", data, 0x20)[0]
    sector_size = 1 << sector_shift
    mini_sector_size = 1 << mini_sector_shift
    fat_count = struct.unpack_from("<I", data, 0x2c)[0]
    dir_start = struct.unpack_from("<I", data, 0x30)[0]
    mini_cutoff = struct.unpack_from("<I", data, 0x38)[0]
    mini_fat_start = struct.unpack_from("<I", data, 0x3c)[0]
    difat = list(struct.unpack_from("<109I", data, 0x4c))[:fat_count]
    fat = read_allocation_table(data, sector_size, difat)
    directory = read_chain(data, sector_size, fat, dir_start)
    entries = parse_directory(directory)
    root = next(entry for entry in entries if entry["type"] == 5)
    target = next(entry for entry in entries if entry["name"] == stream_name)
    if target["size"] >= mini_cutoff:
        return read_chain(data, sector_size, fat, target["start"])[:target["size"]]
    mini_fat = read_allocation_table(data, sector_size, chain_ids(fat, mini_fat_start))
    mini_stream = read_chain(data, sector_size, fat, root["start"])[:root["size"]]
    return read_mini_chain(mini_stream, mini_sector_size, mini_fat, target["start"])[:target["size"]]


def read_allocation_table(data, sector_size, sector_ids):
    entries = []
    for sector_id in sector_ids:
        if sector_id >= 0xFFFFFFF0:
            continue
        sector = read_sector(data, sector_size, sector_id)
        entries.extend(struct.unpack("<" + "I" * (sector_size // 4), sector))
    return entries


def read_chain(data, sector_size, fat, start):
    return b"".join(read_sector(data, sector_size, sector_id) for sector_id in chain_ids(fat, start))


def read_mini_chain(mini_stream, mini_sector_size, mini_fat, start):
    chunks = []
    for sector_id in chain_ids(mini_fat, start):
        offset = sector_id * mini_sector_size
        chunks.append(mini_stream[offset:offset + mini_sector_size])
    return b"".join(chunks)


def chain_ids(fat, start):
    sector_ids = []
    sector_id = start
    seen = set()
    while sector_id < 0xFFFFFFF0 and sector_id not in seen:
        sector_ids.append(sector_id)
        seen.add(sector_id)
        sector_id = fat[sector_id]
    return sector_ids


def read_sector(data, sector_size, sector_id):
    offset = (sector_id + 1) * sector_size
    return data[offset:offset + sector_size]


def parse_directory(directory):
    entries = []
    for offset in range(0, len(directory), 128):
        entry = directory[offset:offset + 128]
        if len(entry) < 128:
            continue
        name_length = struct.unpack_from("<H", entry, 64)[0]
        if name_length < 2:
            continue
        name = entry[:name_length - 2].decode("utf-16le", errors="replace")
        entries.append({
            "name": name,
            "type": entry[66],
            "start": struct.unpack_from("<I", entry, 116)[0],
            "size": struct.unpack_from("<Q", entry, 120)[0]
        })
    return entries


def read_ascii_string(data, offset):
    if offset >= len(data):
        return ""
    length = data[offset]
    start = offset + 1
    end = start + length
    return data[start:end].split(b"\x00", 1)[0].decode("ascii", errors="replace")


def read_double(data, offset):
    return struct.unpack_from("<d", data, offset)[0]


def normalize_stern(label):
    value = label.lower()
    if "normal" in value:
        return "normal_shaped_sections"
    if "v-shaped" in value:
        return "v_shaped_sections"
    if "u-shaped" in value:
        return "u_shaped_sections_with_hogner_stern"
    if "pram" in value:
        return "pram_with_gondola"
    return "unknown"


def normalize_propulsion(label):
    value = label.lower()
    if "conventional" in value:
        return "single_screw_conventional_stern"
    if "open" in value:
        return "single_screw_open_flow_stern"
    if "twin" in value:
        return "twin_screw"
    return "unknown"
