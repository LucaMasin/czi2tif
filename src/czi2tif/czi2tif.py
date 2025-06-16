import click
from pathlib import Path
from czi2tif.read import process_file

@click.command()
@click.argument("czi_input", type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--recursive", "-r", is_flag=True, help="Convert all czi files in the input directory")
def main(czi_input, output, recursive):

    is_input_dir = Path(czi_input).is_dir()
    is_input_file = Path(czi_input).is_file()

    if is_input_dir:
        if output is None:
            output = Path(czi_input) / "tif"
    elif is_input_file:
        if output is None:
            output = Path(czi_input).parent / "tif"

    # if not output.exists():
    #     output.mkdir(parents=True, exist_ok=True)

    click.echo(f"Output directory: {output}")

    if is_input_dir:
        glob_pattern = "**/*.czi" if recursive else "*.czi"

        czi_files = Path(czi_input).glob(glob_pattern)

        for czi_file in czi_files:
            click.echo(f"Converting {czi_file} to {output}")
            process_file(czi_file)

    elif is_input_file:
        click.echo(f"Converting {czi_input} to {output}")
        process_file(czi_input)