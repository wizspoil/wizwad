import cProfile
import tempfile
from pathlib import Path

import wizwad

ROOT = Path(__file__)
noshare = ROOT.parent.parent / "tests" / "noshare_ki_data"

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir_str:
    temp_dir = Path(temp_dir_str)

    extract = temp_dir / "extract"
    extract.mkdir()

    wad = wizwad.Wad(noshare / "_Shared-WorldData.wad")

    with cProfile.Profile() as pr:
        wad.extract_all(extract)

    pr.print_stats("time")
