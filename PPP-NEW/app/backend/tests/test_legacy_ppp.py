import json
import struct
import unittest
from pathlib import Path

from ppp_core.legacy_ppp import ENDOFCHAIN, FATSECT, FREESECT, import_contents_stream, import_legacy_ppp


ROOT = Path(__file__).resolve().parents[3]


class LegacyPppTest(unittest.TestCase):
    def test_import_contents_stream(self):
        expected = json.loads((ROOT / "tests" / "fixtures" / "pppin_sample_import.json").read_text())
        imported = import_contents_stream(sample_contents(), "PPPIN.PPP")

        self.assertEqual(imported["project"], expected["project"])
        self.assertEqual(imported["features"], expected["features"])
        self.assertEqual(imported["propulsion"], expected["propulsion"])
        self.assertEqual(imported["appendages"], expected["appendages"])
        self.assertEqual(imported["modeling"], expected["modeling"])
        self.assertEqual(imported["water"], expected["water"])
        self.assertEqual(imported["margin"], expected["margin"])

    def test_import_ole_document(self):
        imported = import_legacy_ppp(sample_ole_document(), "PPPIN.PPP")

        self.assertEqual(imported["source"]["stream"], "Contents")
        self.assertEqual(imported["source"]["stream_size"], 1880)
        self.assertEqual(imported["project"]["name"], "Holtrop and Mennen Example")
        self.assertAlmostEqual(imported["hull"]["lwl_m"], 212.0)
        self.assertAlmostEqual(imported["speed_sweep"]["initial_speed_knots"], 15.0)

    def test_appendage_and_margin_read_distinct_offsets(self):
        data = bytearray(sample_contents())
        put_double(data, 0x00e6, 0.03)
        put_double(data, 0x01da, 0.07)
        imported = import_contents_stream(bytes(data), "PPPIN.PPP")

        self.assertAlmostEqual(imported["appendages"]["percent_bare_hull_resistance"], 3.0)
        self.assertAlmostEqual(imported["margin"]["design_margin_percent"], 7.0)


def sample_contents():
    data = bytearray(1880)
    put_string(data, 0x0004, "Holtrop and Mennen Example")
    put_string(data, 0x001f, "Test 1.0")
    put_double(data, 0x0028, 212.0)
    put_double(data, 0x0030, 32.0)
    put_double(data, 0x0038, 11.0)
    put_double(data, 0x0040, 11.0)
    put_double(data, 0x0048, 0.6)
    put_double(data, 0x0050, 0.98)
    put_double(data, 0x0058, 0.75)
    put_double(data, 0x0060, -0.75)
    put_double(data, 0x0068, 16.0)
    put_double(data, 0x0070, 4.0)
    put_double(data, 0x0078, 21.0)
    put_string(data, 0x008c, "normal shaped sections")
    put_double(data, 0x00a3, 8.0)
    put_double(data, 0x00ab, 0.8)
    put_string(data, 0x00bf, 'single-screw with "conventional" stern')
    put_double(data, 0x01ae, 21.0)
    put_double(data, 0x00e6, 0.05)
    put_double(data, 0x01b6, 321.0)
    put_double(data, 0x01be, 7890.0)
    put_double(data, 0x01c6, 12.11)
    put_double(data, 0x01da, 0.05)
    put_double(data, 0x01e2, 1025.87)
    put_double(data, 0x01ea, 0.00000118831)
    put_double(data, 0x01f6, 15.0)
    put_double(data, 0x01fe, 2.0)
    return bytes(data)


def sample_ole_document():
    sector_size = 512
    sectors = [bytearray(sector_size) for _ in range(9)]
    fat_entries = [FREESECT] * 128
    fat_entries[2] = ENDOFCHAIN
    fat_entries[3] = FATSECT
    fat_entries[4] = ENDOFCHAIN
    fat_entries[5] = 6
    fat_entries[6] = 7
    fat_entries[7] = 8
    fat_entries[8] = ENDOFCHAIN
    sectors[3][:] = struct.pack("<128I", *fat_entries)
    mini_entries = [FREESECT] * 128
    for index in range(29):
        mini_entries[index] = index + 1
    mini_entries[29] = ENDOFCHAIN
    sectors[4][:] = struct.pack("<128I", *mini_entries)
    directory = bytearray(sector_size)
    directory[0:128] = directory_entry("Root Entry", 5, 5, 1920, child=1)
    directory[128:256] = directory_entry("Contents", 2, 0, 1880)
    sectors[2][:] = directory
    mini_stream = sample_contents() + bytes(40)
    for index, sector_id in enumerate([5, 6, 7, 8]):
        sectors[sector_id][:] = mini_stream[index * sector_size:(index + 1) * sector_size]
    header = bytearray(sector_size)
    header[:8] = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
    struct.pack_into("<H", header, 0x18, 0x003e)
    struct.pack_into("<H", header, 0x1a, 0x0003)
    struct.pack_into("<H", header, 0x1c, 0xfffe)
    struct.pack_into("<H", header, 0x1e, 9)
    struct.pack_into("<H", header, 0x20, 6)
    struct.pack_into("<I", header, 0x2c, 1)
    struct.pack_into("<I", header, 0x30, 2)
    struct.pack_into("<I", header, 0x38, 4096)
    struct.pack_into("<I", header, 0x3c, 4)
    struct.pack_into("<I", header, 0x40, 1)
    struct.pack_into("<I", header, 0x44, ENDOFCHAIN)
    struct.pack_into("<I", header, 0x48, 0)
    struct.pack_into("<109I", header, 0x4c, 3, *([FREESECT] * 108))
    return bytes(header + b"".join(sectors))


def directory_entry(name, entry_type, start, size, child=FREESECT):
    entry = bytearray(128)
    encoded = name.encode("utf-16le") + b"\x00\x00"
    entry[:len(encoded)] = encoded
    struct.pack_into("<H", entry, 64, len(encoded))
    entry[66] = entry_type
    struct.pack_into("<I", entry, 68, FREESECT)
    struct.pack_into("<I", entry, 72, FREESECT)
    struct.pack_into("<I", entry, 76, child)
    struct.pack_into("<I", entry, 116, start)
    struct.pack_into("<Q", entry, 120, size)
    return entry


def put_string(data, offset, value):
    raw = value.encode("ascii")
    data[offset] = len(raw)
    data[offset + 1:offset + 1 + len(raw)] = raw


def put_double(data, offset, value):
    struct.pack_into("<d", data, offset, value)


if __name__ == "__main__":
    unittest.main()
