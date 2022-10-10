import os
import struct
import zlib
import concurrent.futures
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, List
from mmap import mmap, ACCESS_READ
from io import BytesIO

import more_itertools


_NO_COMPRESS = frozenset(
    (
        ".mp3",
        ".ogg",
    )
)


@dataclass
class WadFileInfo:
    name: str
    offset: int
    size: int
    zipped_size: int
    is_zip: bool
    crc: int


class Wad:
    # TODO: allow for `file` that doesnt exist yet
    def __init__(self, file: Union[Path, str]):
        self.file_path = Path(file)
        self.name = self.file_path.stem

        self._file_map = {}
        self._file_pointer = None
        self._mmap = None

        self._refreshed_once = False

        self._size = None

    def __repr__(self):
        return f"<Wad {self.name=}>"

    def __enter__(self):
        self._open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def size(self) -> int:
        """
        Total size of this wad
        """
        if not self._file_pointer:
            self._open()

        if self._size:
            return self._size

        self._size = sum(file.size for file in self._file_map.values())
        return self._size

    def name_list(self) -> List[str]:
        """
        List of all file names in this wad
        """
        if not self._file_pointer:
            self._open()

        return list(self._file_map.keys())

    def info_list(self) -> List[WadFileInfo]:
        """
        List of all KIWadFileInfo in this wad
        """
        if not self._file_pointer:
            self._open()

        return list(self._file_map.values())

    def _open(self):
        if self._file_pointer:
            raise RuntimeError("This Wad is already open")

        # noinspection PyTypeChecker
        self._file_pointer = open(self.file_path, "rb")
        self._mmap = mmap(self._file_pointer.fileno(), 0, access=ACCESS_READ)
        self._refresh_journal()

    def open(self, file_name: str) -> BytesIO:
        data = self.read(file_name)
        return BytesIO(data)

    def close(self):
        self._file_pointer.close()
        self._file_pointer = None

    # fmt: off
    def _read(self, start: int, size: int) -> bytes:
        return self._mmap[start: start + size]
    # fmt: on

    # fmt: off
    def _refresh_journal(self):
        if self._refreshed_once:
            return

        self._refreshed_once = True

        # WAD id string
        file_offset = 5

        version, file_num = struct.unpack(
            "<ll", self._mmap[file_offset: file_offset + 8]
        )

        file_offset += 8

        if version >= 2:
            file_offset += 1

        for _ in range(file_num):
            # no reason to use struct.calcsize
            offset, size, zipped_size, is_zip, crc, name_length = struct.unpack(
                "<lll?Ll", self._mmap[file_offset: file_offset + 21]
            )

            # 21 is the size of all the data we just read
            file_offset += 21

            name = self._mmap[file_offset: file_offset + name_length].decode()
            name = name.rstrip("\x00")

            file_offset += name_length

            self._file_map[name] = WadFileInfo(
                name, offset, size, zipped_size, is_zip, crc
            )
    # fmt: on

    def read(self, name: str) -> Optional[bytes]:
        """
        Get the data contents of the named file
        Args:
            name: name of the file to get
        Returns:
            Bytes of the file or None for "unpatched" dummy files
        """
        if not self._file_pointer:
            self._open()

        target_file = self.get_info(name)

        if target_file.is_zip:
            data = self._read(target_file.offset, target_file.zipped_size)

        else:
            data = self._read(target_file.offset, target_file.size)

        # unpatched file
        if data[:4] == b"\x00\x00\x00\x00":
            return None

        if target_file.is_zip:
            data = zlib.decompress(data)

        return data

    # # TODO: finish
    # def write(self, name: str, data: str | bytes):
    #     if isinstance(data, str):
    #         data = data.encode()

    def get_info(self, name: str) -> WadFileInfo:
        """
        Gets a KIWadFileInfo for a named file
        Args:
            name: name of the file to get info on
        """
        if not self._file_pointer:
            self._open()

        try:
            target_file = self._file_map[name]
        except KeyError:
            raise ValueError(f"File {name} not found.")

        return target_file

    def extract_all(self, path: Union[Path, str]):
        """
        Extract a wad file into a directory

        Args:
            path: source_path to the directory to unpack the wad
        """
        path = Path(path)

        if not self._file_pointer:
            self._open()

        self._extract_all(path)

    def _extract_all(self, path):
        with open(self.file_path, "rb") as fp:
            with mmap(fp.fileno(), 0, access=ACCESS_READ) as mm:
                for file in self._file_map.values():
                    file_path = path / file.name
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                    if file.is_zip:
                        data = mm[file.offset: file.offset + file.zipped_size]

                    else:
                        data = mm[file.offset: file.offset + file.size]

                    # unpatched file
                    if data[:4] == b"\x00\x00\x00\x00":
                        file_path.touch()
                        continue

                    if file.is_zip:
                        data = zlib.decompress(data)

                    file_path.write_bytes(data)

    @classmethod
    def from_full_add(
            cls,
            source_path: Path | str,
            new_wad_name: Path | str,
            *,
            overwrite: bool = False,
            wad_version: int = 1,
            workers: int = 10,
    ):
        if isinstance(source_path, str):
            source_path = Path(source_path)

        if not source_path.is_dir():
            if not source_path.exists():
                raise FileNotFoundError(source_path)

            raise ValueError(f"{source_path} is not a directory.")

        if isinstance(new_wad_name, str):
            new_wad_name = Path(new_wad_name)

        if not overwrite and new_wad_name.exists():
            raise FileExistsError(f"{new_wad_name} already exists.")

        cls._insert_all_fast(source_path, new_wad_name, wad_version, workers)
        return cls(new_wad_name)

    @staticmethod
    def _insert_all_fast(
        source_path: Path,
        output_path: Path,
        wad_version: int = 1,
        workers: int = 100,
    ):
        to_write = []
        source_path_string = str(source_path)
        for root, _, files in os.walk(source_path):
            if root == source_path_string:
                directory_prefix = ""
            else:
                directory_prefix = root[len(str(source_path)) + 1:] + "/"

            for file in files:
                to_write.append(Path(directory_prefix + file))

        # file names must be sorted
        to_write = sorted(to_write, key=lambda p: p.as_posix())

        file_num = len(to_write)

        all_names_len = sum(len(str(file)) for file in to_write)

        # KIWAD + version + file_num + version 2 0x01 + journal header * file number
        # + file num for the null terminator
        journal_size = 14 + (21 * file_num) + all_names_len + file_num

        if wad_version == 1:
            journal_size -= 1

        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            futures = []

            for chunk in more_itertools.divide(workers, to_write):
                futures.append(executor.submit(_calculate_chunk, chunk, 0, source_path))

            with open(output_path, "wb+") as fp:
                data_block = BytesIO()

                chunk_offset = journal_size

                # magic bytes
                fp.write(b"KIWAD")

                fp.write(struct.pack("<ll", wad_version, file_num))

                if wad_version >= 2:
                    # version 2 thing
                    fp.write(b"\x01")

                for future in futures:
                    end, buffer, infos = future.result()

                    for info in infos:
                        fp.write(
                            struct.pack(
                                "<lll?Ll",
                                info.offset + chunk_offset,  # 0 for first chunk
                                info.size,
                                info.zipped_size,
                                info.is_zip,
                                info.crc,
                                len(info.name) + 1,
                            )
                        )

                        # only / paths are allowed
                        fp.write(info.name.encode() + b"\x00")

                    chunk_offset += end

                    buffer.seek(0)
                    data_block.write(buffer.getvalue())

                data_block.seek(0)
                fp.write(data_block.getvalue())


# has to be defined here
def _calculate_chunk(
        files: list[Path],
        start: int,
        source: Path,
) -> tuple[int, BytesIO, list[WadFileInfo]]:
    """
    returns end offset, data block, and journal entries
    """
    current_offset = start
    data_buffer = BytesIO()
    journal_entries = []

    for file in files:
        is_zip = file.suffix not in _NO_COMPRESS
        data = (source / file).read_bytes()
        size = len(data)
        name = file.as_posix()

        if is_zip:
            # this is where 90% of processing time is spent
            compressed_data = zlib.compress(data, level=9)
            zipped_size = len(compressed_data)

            data = compressed_data
        else:
            zipped_size = -1

        # crc is of compressed data for some reason
        crc = zlib.crc32(data, 0xFFFF_FFFF) ^ 0xFFFF_FFFF

        journal_entries.append(
            WadFileInfo(name, current_offset, size, zipped_size, is_zip, crc)
        )

        current_offset += len(data)

        data_buffer.write(data)

    return current_offset, data_buffer, journal_entries
