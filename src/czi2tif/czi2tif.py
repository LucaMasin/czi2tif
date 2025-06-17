import click
from pathlib import Path
from czi2tif.read import process_file
from czi2tif.logging import setup_logging, configure_module_logger
from czi2tif.export import ExportParams

# Set up module logger
logger = configure_module_logger(__name__)

@click.command()
@click.argument("czi_input", type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--recursive", "-r", is_flag=True, help="Convert all czi files in the input directory")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging", default=False)
@click.option("--quiet", "-q", is_flag=True, help="Disable all logging output", default=False)
@click.option("--log-file", type=click.Path(), help="Path to log file (enables file logging)")
@click.option("--bit-depth", type=click.Choice(["8", "16", "32"]), help="Bit depth for the output TIF files", default="16")
def main(czi_input, output, recursive, verbose, quiet, log_file, bit_depth):
    """Convert CZI files to TIF format with scaling information."""
    
    # Validate mutually exclusive options
    if verbose and quiet:
        click.echo("--verbose and --quiet options cannot be used together. Overriding --quiet.")
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
            quiet=False
        )
    
    logger.info("Starting czi2tif conversion")
    logger.debug(f"Input: {czi_input}, Output: {output}, Recursive: {recursive}")

    is_input_dir = Path(czi_input).is_dir()
    is_input_file = Path(czi_input).is_file()

    if is_input_dir:
        if output is None:
            output = Path(czi_input) / "tif"
        logger.info(f"Processing directory: {czi_input}")
    elif is_input_file:
        if output is None:
            output = Path(czi_input).parent / "tif"
        logger.info(f"Processing file: {czi_input}")

    # if not output.exists():
    #     output.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output directory: {output}")

    export_params = ExportParams(output_dir=Path(output), bit_depth=int(bit_depth))

    if is_input_dir:
        glob_pattern = "**/*.czi" if recursive else "*.czi"
        logger.debug(f"Using glob pattern: {glob_pattern}")

        czi_files = list(Path(czi_input).glob(glob_pattern))
        logger.info(f"Found {len(czi_files)} CZI files to process")

        for i, czi_file in enumerate(czi_files, 1):
            logger.info(f"Converting {i}/{len(czi_files)}: {czi_file.name}")
            logger.debug(f"Processing file: {czi_file} -> {output}")
            try:
                process_file(czi_file, export_params)
                logger.debug(f"Successfully processed: {czi_file.name}")
            except Exception as e:
                logger.error(f"Failed to process {czi_file.name}: {e}")
                if verbose:
                    logger.exception("Full traceback:")

    elif is_input_file:
        logger.info(f"Converting single file: {Path(czi_input).name}")
        try:
            process_file(czi_input, export_params)
            logger.info("Conversion completed successfully")
        except Exception as e:
            logger.error(f"Failed to process {Path(czi_input).name}: {e}")
            if verbose:
                logger.exception("Full traceback:")
    
    logger.info("czi2tif conversion completed")