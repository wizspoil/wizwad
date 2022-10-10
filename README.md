# wizwad
A fast extractor and packer for wizard101/pirate101 wad files

## install
```shell
$ pip install wizwad
```

## cli usage
```shell
# extract a wad
$ wizwad extract path/to/Wad.wad directory/to/extract/to/
# list the files in a wad
$ wizwad list path/to/Wad.wad
# pack a directory into a wad
$ wizwad pack path/to/Wad.wad directory/to/pack
```

## library usage
```python
import wizwad

wad = wizwad.Wad("path/to/Wad.wad")

some_file = wad.read("name/of/file")
print(some_file)
```

## support
discord: https://discord.gg/yuCRZ7kPjM
