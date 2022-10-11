import tempfile
import zlib
import time
from pprint import pprint
from pathlib import Path

import wizwad


noshare = Path("tests/noshare_ki_data")

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
    temp_dir = Path(temp_dir)

    extract = temp_dir / "extract"
    extract.mkdir()

    wad = wizwad.Wad(noshare / "Root.wad")

    start_extract_all = time.perf_counter()
    wad.extract_all(extract)
    end_extract_all = time.perf_counter()
    print(f"{(end_extract_all - start_extract_all)=}")

    start_full_add = time.perf_counter()
    new_wad = wizwad.Wad.from_full_add(extract, temp_dir / "NewWad.wad", wad_version=2, workers=4)
    end_full_add = time.perf_counter()
    print(f"{(end_full_add - start_full_add)=}")

    for old_entry, new_entry in zip(wad.info_list(), new_wad.info_list()):
        assert old_entry.offset == new_entry.offset, f"{old_entry.offset} != {new_entry.offset}"
