import tempfile
import zlib
from pathlib import Path

import pytest

import wizwad


# noshare dir holds proprietary game data and must be created yourself
def get_noshare_dir() -> Path | bool:
    root = Path(__file__)
    noshare = root.parent / "noshare_ki_data"

    if not noshare.exists():
        return False

    return noshare


def test_noshare_remake_wad_krok():
    if (noshare := get_noshare_dir()) is False:
        pytest.skip("No noshare data")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        extract = temp_dir / "extract"
        extract.mkdir()

        wad = wizwad.Wad(noshare / "Krokotopia-Interiors-KT_HallofDoors.wad")
        wad.extract_all(extract)

        new_wad = wizwad.Wad(temp_dir / "NewWad.wad")
        new_wad.insert_all(extract)

        for old_entry, new_entry in zip(wad.info_list(), new_wad.info_list()):
            assert old_entry == new_entry

        with open(wad.file_path, "rb") as old, open(new_wad.file_path, "rb") as new:
            old_data = old.read()
            new_data = new.read()

            assert zlib.crc32(old_data) == zlib.crc32(new_data)


def test_noshare_remake_wad_root():
    if (noshare := get_noshare_dir()) is False:
        pytest.skip("No noshare data")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        extract = temp_dir / "extract"
        extract.mkdir()

        wad = wizwad.Wad(noshare / "Root.wad")
        wad.extract_all(extract)

        new_wad = wizwad.Wad(temp_dir / "NewWad.wad")
        new_wad.insert_all(extract, wad_version=2)

        for old_entry, new_entry in zip(wad.info_list(), new_wad.info_list()):
            assert old_entry == new_entry

        with open(wad.file_path, "rb") as old, open(new_wad.file_path, "rb") as new:
            old_data = old.read()
            new_data = new.read()

            assert zlib.crc32(old_data) == zlib.crc32(new_data)
