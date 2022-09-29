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
def extract(input_wad, output_dir):
    wad = Wad(input_wad)
    click.echo("Extracting")
    wad.extract_all(output_dir)


if __name__ == "__main__":
    main()
