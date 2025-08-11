import click
from pathlib import Path
from czi2tif.read import process_file
from czi2tif.logging import setup_logging, configure_module_logger
from czi2tif.export import ExportParams

general_config = {
    "bit_depth": 16,
    "verbose": False,
    "quiet": False,
    "log_file": None,
    "output": None,
}

# Set up module logger
logger = configure_module_logger(__name__)


@click.command()
@click.argument("input", type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output directory",
    default=general_config["output"],
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Convert all czi files in the input directory",
)
@click.option(
    "--match",
    "-m",
    type=str,
    help="Only convert files whose name contains this substring",
    default=None,
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
    default=general_config["verbose"],
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Disable all logging output",
    default=general_config["quiet"],
)
@click.option(
    "--log-file", type=click.Path(), help="Path to log file (enables file logging)"
)
@click.option(
    "--bit-depth",
    "-bd",
    type=click.Choice(["8", "16", "32"]),
    help=f"Bit depth for the output TIF files (default: {general_config['bit_depth']})",
    default=str(general_config["bit_depth"]),
)
def main(input, output, recursive, match, verbose, quiet, log_file, bit_depth):
    """Convert CZI files to TIF format with scaling information."""

    allowed_extensions = (".czi", ".lif")

    # Validate mutually exclusive options
    if verbose and quiet:
        click.echo(
            "--verbose and --quiet options cannot be used together. Overriding --quiet."
        )
        quiet = False

    # Initialize logging
    if quiet:
        setup_logging(quiet=True)
    else:
        log_level = "DEBUG" if verbose else "INFO"
        file_output = log_file is not None
        setup_logging(
            log_level=log_level,
            log_file=Path(log_file) if log_file else None,
            console_output=True,
            file_output=file_output,
            quiet=False,
        )

    logger.info("Starting czi2tif conversion")
    logger.debug(
        f"Input: {input}, Output: {output}, Recursive: {recursive}, Match: {match}"
    )

    is_input_dir = Path(input).is_dir()
    is_input_file = Path(input).is_file()

    if is_input_dir:
        if output is None:
            output = Path(input) / "tif"
        logger.info(f"Processing directory: {input}")
    elif is_input_file:
        if not is_input_file or Path(input).suffix.lower() not in allowed_extensions:
            logger.error(f"Input file must be a CZI or LIF file: {input}")
            raise ValueError(f"Input file must be a CZI or LIF file: {input}")
        if output is None:
            output = Path(input).parent / "tif"
        logger.info(f"Processing file: {input}")

    # if not output.exists():
    #     output.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output directory: {output}")

    export_params = ExportParams(output_dir=Path(output), bit_depth=int(bit_depth))

    if is_input_dir:
        files = []
        for ext in allowed_extensions:
            files.extend(Path(input).glob(f"**/*{ext}" if recursive else f"*{ext}"))
        logger.info(f"Found {len(files)} files to process")

        # TODO: extend this it matches proper regexes
        if match:
            files = [f for f in files if match in f.name]
            logger.info(f"Filtered files: {files}")

        for i, file in enumerate(files, 1):
            logger.info(f"Converting {i}/{len(files)}: {file.name}")
            logger.debug(f"Processing file: {file} -> {output}")
            try:
                process_file(file, export_params)
                logger.debug(f"Successfully processed: {file.name}")
            except Exception as e:
                logger.error(f"Failed to process {file.name}: {e}")
                if verbose:
                    logger.exception("Full traceback:")

    elif is_input_file:
        logger.info(f"Converting single file: {Path(input).name}")
        try:
            process_file(input, export_params)
            logger.info("Conversion completed successfully")
        except Exception as e:
            logger.error(f"Failed to process {Path(input).name}: {e}")
            if verbose:
                logger.exception("Full traceback:")

    logger.info("czi2tif conversion completed")
