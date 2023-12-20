"""
# for out_path take a PathLike or a callable that takes the old path and returns the new one

with WadEditor(wad, out_path="abc.wad") as editor:
    editor.edit("filename", content=b"\x00\x00")
    editor.add("filename2", from=SomeReadable)

# this can only be called after the context manager
wad = editor.get_wad()
"""


class WadEditor:
    def __init__(self):
        ...

    def edit(self):
        ...
    
    def add(self):
        ...

