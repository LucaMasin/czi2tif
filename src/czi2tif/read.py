from typing import Union, Tuple, List, Dict
from pathlib import Path
import xml.etree.ElementTree as ET

from aicspylibczi import CziFile
from czi2tif.logging import configure_module_logger

# Set up module logger
logger = configure_module_logger(__name__)

Pathlike = Union[str, Path]
CziShape = List[Dict[str, Tuple[int, ...]]]


def read_czi(czi_file: Pathlike) -> CziFile:
    """Read a CZI file and return CziFile object."""
    logger.debug(f"Reading CZI file: {czi_file}")
    try:
        czi_obj = CziFile(czi_file)
        logger.debug(f"Successfully loaded CZI file: {czi_file}")
        return czi_obj
    except Exception as e:
        logger.error(f"Failed to read CZI file {czi_file}: {e}")
        raise


def get_resolution(metadata: ET.Element) -> Tuple[float, float, float]:
    """Get the resolution from the czi metadata."""
    logger.debug("Extracting resolution from CZI metadata")

    root = ET.ElementTree(metadata).getroot()

    distance_element = root.find(".//Distance[@Id='X']/Value")
    if distance_element is None:
        logger.warning("No resolution found in metadata. Assuming 1 pixel per micron.")
        return (1, 1, 1)
    else:
        res_x = float(distance_element.text)  # type: ignore
        logger.debug(f"Found X resolution: {res_x}")
        # convert to pixels per micron
        res_x = 1 / (res_x * 1e6)

        distance_element = root.find(".//Distance[@Id='Y']/Value")
        res_y = float(distance_element.text)  # type: ignore
        logger.debug(f"Found Y resolution: {res_y}")

        try:
            distance_element = root.find(".//Distance[@Id='Z']/Value")
            res_z = float(distance_element.text) if distance_element is not None else 1
            logger.debug(f"Found Z resolution: {res_z}")
        except (AttributeError, TypeError):
            res_z = 1
            logger.debug("No Z resolution found, using default value of 1")

        # convert to pixels per micron
        res_y = 1 / (res_y * 1e6)
        res_z = 1 / (res_z * 1e6)

        final_resolution = (res_x, res_y, res_z)
        logger.info(
            f"Extracted resolution (pixels/micron): X={res_x:.6f}, Y={res_y:.6f}, Z={res_z:.6f}"
        )
        return final_resolution


def has_scenes(czi_shape: CziShape) -> bool:
    """Check if the CZI file has multiple scenes."""
    return "S" in czi_shape[0]


def has_mosaics(czi_shape: CziShape) -> bool:
    """Check if the CZI file has mosaics."""
    return any("M" in entry for entry in czi_shape)


def has_stacks(czi_shape: CziShape) -> bool:
    """Check if the CZI file has stacks."""
    return "Z" in czi_shape[0]


def process_file(czi_file: Pathlike) -> None:
    """Process a single CZI file and extract resolution information."""
    logger.info(f"Processing CZI file: {Path(czi_file).name}")

    try:
        czi = read_czi(czi_file)
        logger.debug("CZI file loaded successfully")

        resolution = get_resolution(czi.meta)
        logger.info(f"Resolution extracted: {resolution}")

        czi_shape: CziShape = czi.get_dims_shape()
        if len(czi_shape) == 1:
            logger.info(f"Dimensions of file: {czi_shape}")
        else:
            logger.info("Dimensions of file: ")
            for n, entry in enumerate(czi_shape):
                logger.info(f"Entry {n}: {entry}")

        is_homogenous = True
        if has_scenes(czi_shape):
            logger.debug("Detected multiple scenes")
            if len(czi_shape) > 1 and len(czi_shape) != czi_shape[0]["S"][-1]:
                logger.debug("Dimensions are not homogenous across scenes")
                is_homogenous = False
            elif len(czi_shape) == 1 and czi_shape[0]["S"][-1] > 1:
                logger.debug("Dimensions are homogenous across scenes")
            else:
                logger.debug("Single scene file")

        if has_mosaics(czi_shape):
            num_mosaics = sum(1 for entry in czi_shape if "M" in entry)
            logger.info(
                f"File contains mosaics ({num_mosaics} out of {len(czi_shape)} entries)"
            )
        else:
            logger.info("File does not contain mosaics")

        if has_stacks(czi_shape):
            logger.info("File contains stacks")
        else:
            logger.info("File does not contain stacks")

        # TODO: Add actual TIF conversion logic here
        logger.debug("File processing completed (conversion logic not yet implemented)")

    except Exception as e:
        logger.error(f"Error processing file {czi_file}: {e}")
        raise
