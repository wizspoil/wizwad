import logging

from .wad import Wad, WadFileInfo

logging.getLogger(__name__).addHandler(logging.NullHandler())

del logging

__all__ = ["Wad", "WadFileInfo"]
