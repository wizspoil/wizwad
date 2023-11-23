import sys
import tempfile
import zlib
from pathlib import Path
from typing import Literal

import pytest

import wizwad


def get_worker_count() -> int:
    # windows can only do 61
    if sys.platform == "win32":
        return 60

    return 100


# noshare dir holds proprietary game data and must be created yourself
def get_noshare_dir() -> Path | Literal[False]:
    root = Path(__file__)
    noshare = root.parent / "noshare_ki_data"

    if not noshare.exists():
        return False

    return noshare


def get_test_data_dir() -> Path:
    root = Path(__file__)
    return root.parent / "test_data"


def test_noshare_remake_wad_krok():
    if (noshare := get_noshare_dir()) is False:
        pytest.skip("No noshare data")

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        temp_dir = Path(temp_dir)

        extract = temp_dir / "extract"
        extract.mkdir()

        wad = wizwad.Wad(noshare / "Krokotopia-Interiors-KT_HallofDoors.wad")
        wad.extract_all(extract)

        new_wad = wizwad.Wad.from_full_add(
            extract, temp_dir / "NewWad.wad", workers=get_worker_count()
        )

        for old_entry, new_entry in zip(wad.info_list(), new_wad.info_list()):
            assert old_entry == new_entry

        with open(wad.file_path, "rb") as old, open(new_wad.file_path, "rb") as new:
            old_data = old.read()
            new_data = new.read()

            assert zlib.crc32(old_data) == zlib.crc32(new_data)


def test_noshare_remake_wad_root():
    if (noshare := get_noshare_dir()) is False:
        pytest.skip("No noshare data")

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        temp_dir = Path(temp_dir)

        extract = temp_dir / "extract"
        extract.mkdir()

        wad = wizwad.Wad(noshare / "Root.wad")
        wad.extract_all(extract)

        new_wad = wizwad.Wad.from_full_add(
            extract,
            temp_dir / "NewWad.wad",
            workers=get_worker_count(),
            wad_version=2,
        )

        for old_entry, new_entry in zip(wad.info_list(), new_wad.info_list()):
            assert old_entry == new_entry

        with open(wad.file_path, "rb") as old, open(new_wad.file_path, "rb") as new:
            old_data = old.read()
            new_data = new.read()

            assert zlib.crc32(old_data) == zlib.crc32(new_data)


def test_data_make_wad():
    test_data = get_test_data_dir()

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        temp_dir = Path(temp_dir)

        extract = temp_dir / "extract"
        extract.mkdir()

        wad = wizwad.Wad.from_full_add(
            test_data,
            temp_dir / "Wad.wad",
            workers=get_worker_count(),
            wad_version=2,
        )
        wad.extract_all(extract)

        new_wad = wizwad.Wad.from_full_add(
            extract,
            temp_dir / "NewWad.wad",
            workers=get_worker_count(),
            wad_version=2,
        )

        for old_entry, new_entry in zip(wad.info_list(), new_wad.info_list()):
            assert old_entry == new_entry

        with open(wad.file_path, "rb") as old, open(new_wad.file_path, "rb") as new:
            old_data = old.read()
            new_data = new.read()

            assert zlib.crc32(old_data) == zlib.crc32(new_data)
