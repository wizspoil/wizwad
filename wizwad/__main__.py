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


@main.command()
@click.argument("target_wad", type=click.Path(path_type=Path))
@click.argument("content_to_add", type=click.Path(path_type=Path, exists=True))
@click.option("--overwrite", is_flag=True, default=False, help="overwrite a wad if there already is one")
@click.option("--wad-version", type=int, default=1, help="the wad version to use")
@click.option("--workers", type=int, default=10, help="the number of workers to use; 100 is recommend if you can")
def pack(target_wad: Path, content_to_add: Path, overwrite: bool, wad_version: int, workers: int):
    """
    Pack a directory into <target_wad>
    """
    if wad_version == 1 and target_wad.name == "Root.wad":
        click.echo("You may wish to use --wad-version 2 for Root.wad")

    if workers < 100:
        click.echo("Using less than 100 workers may make packing slower")

    if workers <= 0:
        click.echo("workers must be greater than 0")
        exit(1)

    Wad.from_full_add(content_to_add, target_wad, overwrite=overwrite)


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
