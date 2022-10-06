from pathlib import Path

import click

from .wad import Wad


@click.group()
def main():
    """
    wizwad
    """
    pass


@main.command()
@click.argument("input_wad", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("output_dir", type=click.Path(file_okay=False, path_type=Path), default=".")
def extract(input_wad: Path, output_dir: Path):
    """
    Extract the content of a wad to <output_dir> which defaults to the current directory
    """
    wad = Wad(input_wad)
    click.echo("Extracting")
    wad.extract_all(output_dir)


# @main.command()
# @click.argument("target_wad", type=click.Path(path_type=Path))
# @click.argument("content_to_add", type=click.Path(path_type=Path, exists=True))
# def add(target_wad: Path, content_to_add: Path):
#     """
#     Add a file to <target_wad>
#     """
#     print(f"{target_wad=} {content_to_add=}")


@main.command(name="list")
@click.argument("wad_to_list", type=click.Path(path_type=Path, exists=True, dir_okay=False))
def _list(wad_to_list: Path):
    """
    List the files in <wad_to_list>
    """
    wad = Wad(wad_to_list)
    # TODO: raise an error if it isn't a valid wad file
    click.echo("\n".join(wad.name_list()))


if __name__ == "__main__":
    main()
