from typing import Union, Tuple, List, Dict
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from aicspylibczi import CziFile
from tifffile import imwrite, RESUNIT

from czi2tif.logging import configure_module_logger
from czi2tif.export import ExportParams
from readlif.reader import LifFile

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


def get_resolution(metadata: ET.Element) -> Tuple[float, ...]:
    """Get the resolution from the czi metadata."""
    logger.debug("Extracting resolution from CZI metadata")

    root = ET.ElementTree(metadata).getroot()

    distance_element = root.find(".//Distance[@Id='X']/Value")  # type: ignore
    if distance_element is None:
        logger.warning("No resolution found in metadata. Assuming 1 pixel per micron.")
        return (1, 1, 1)
    else:
        res_x = float(distance_element.text)  # type: ignore
        logger.debug(f"Found X resolution: {res_x}")
        # convert to pixels per micron
        res_x = 1 / (res_x * 1e6)

        distance_element = root.find(".//Distance[@Id='Y']/Value")  # type: ignore
        res_y = float(distance_element.text)  # type: ignore
        logger.debug(f"Found Y resolution: {res_y}")

        # convert to pixels per micron
        res_y = 1 / (res_y * 1e6)

        distance_element = root.find(".//Distance[@Id='Z']/Value")  # type: ignore
        if distance_element is not None and distance_element.text is not None:
            try:
                res_z = float(distance_element.text)
                logger.debug(f"Found Z resolution: {res_z}")
                # convert to pixels per micron
                res_z = 1 / (res_z * 1e6)
                final_resolution = (res_x, res_y, res_z)
                logger.info(
                    f"Extracted resolution (pixels/micron): X={res_x:.6f}, Y={res_y:.6f}, Z={res_z:.6f}"
                )
            except (AttributeError, TypeError, ValueError):
                final_resolution = (res_x, res_y)
                logger.debug("Error processing Z resolution, using 2D resolution")
                logger.info(
                    f"Extracted resolution (pixels/micron): X={res_x:.6f}, Y={res_y:.6f}"
                )
        else:
            final_resolution = (res_x, res_y)
            logger.debug("No Z resolution found, using 2D resolution")
            logger.info(
                f"Extracted resolution (pixels/micron): X={res_x:.6f}, Y={res_y:.6f}"
            )

        return final_resolution


def has_scenes(czi_dims: str) -> bool:
    """Check if the CZI file has multiple scenes."""
    return "S" in czi_dims


def has_mosaics(czi_dims: str) -> bool:
    """Check if the CZI file has mosaics."""
    return "M" in czi_dims


def has_stacks(czi_dims: str) -> bool:
    """Check if the CZI file has stacks."""
    return "Z" in czi_dims


def get_scene_data(czi: CziFile, entry_index: int) -> Tuple[np.ndarray, list]:
    """Get the image data from the CZI file."""
    image_data, dims = czi.read_image(S=entry_index)
    return image_data, dims


def get_stack_data(czi: CziFile, scene_index: int) -> Tuple[np.ndarray, list]:
    """Get the image data from the CZI file."""
    n_planes = czi.get_dims_shape()[0]["Z"][-1]
    n_channels = czi.get_dims_shape()[0]["C"][-1]
    full_image_data = []
    full_dims = []
    for plane_index in range(n_planes):
        channel_image_data = []
        channel_dims = []
        for channel_index in range(n_channels):
            image_data, dims = czi.read_image(
                S=scene_index, Z=plane_index, C=channel_index
            )
            channel_image_data.append(image_data)
            channel_dims.append(dims)
        full_image_data.append(channel_image_data)
        full_dims.append(channel_dims)

    return np.array(full_image_data), full_dims


def get_mosaic_data(
    czi: CziFile, entry_index: int, czi_dims: str, czi_shape: CziShape
) -> np.ndarray:
    """Get the mosaic image data from the CZI file."""
    bboxes = czi.get_all_mosaic_scene_bounding_boxes()
    channels = []
    for channel in range(czi_shape[entry_index]["C"][-1]):
        planes = []
        if has_stacks(czi_dims):
            for plane in range(czi_shape[entry_index]["Z"][-1]):
                mosaic_data = czi.read_mosaic(
                    region=tuple([bboxes[0].x, bboxes[0].y, bboxes[0].w, bboxes[0].h]),
                    scale_factor=1,
                    C=channel,
                    Z=plane,
                ).squeeze()
                planes.append(mosaic_data)
        else:
            mosaic_data = czi.read_mosaic(
                region=tuple([bboxes[0].x, bboxes[0].y, bboxes[0].w, bboxes[0].h]),
                scale_factor=1,
                C=channel,
            ).squeeze()
            planes.append(mosaic_data)
        channels.append(planes)
    img = np.array(channels)
    if not has_stacks(czi_dims):
        img = np.swapaxes(img, 0, 1)
    return img


# TODO: Clean this up later
def process_czi(czi_file: Path, export_params: ExportParams) -> None:
    try:
        czi = read_czi(czi_file)
        logger.debug("CZI file loaded successfully")

        resolution = get_resolution(czi.meta)
        logger.info(f"Resolution extracted: {resolution}")

        czi_dims = czi.dims

        czi_shape: CziShape = czi.get_dims_shape()
        if len(czi_shape) == 1:
            logger.info(f"Dimensions of file: {czi_shape}")
        else:
            logger.info("Dimensions of file: ")
            for n, entry in enumerate(czi_shape):
                logger.info(f"Entry {n}: {entry}")

        is_homogenous = True
        if has_scenes(czi_dims):
            logger.info("Detected multiple scenes")
            if len(czi_shape) > 1 and len(czi_shape) != czi_shape[0]["S"][-1]:
                logger.debug("Dimensions are not homogenous across scenes")
                is_homogenous = False
            elif len(czi_shape) == 1 and czi_shape[0]["S"][-1] > 1:
                logger.debug("Dimensions are homogenous across scenes")
            else:
                logger.debug("Single scene file")
        else:
            logger.info("File does not contain multiple scenes")

        if has_mosaics(czi_dims):
            num_mosaics = sum(1 for entry in czi_shape if "M" in entry)
            logger.info(
                f"File contains mosaics ({num_mosaics} out of {len(czi_shape)} entries)"
            )
        else:
            logger.info("File does not contain mosaics")

        if has_stacks(czi_dims):
            logger.info("File contains stacks")
        else:
            logger.info("File does not contain stacks")

        if has_scenes(czi_dims) and is_homogenous:
            entry_indexes = range(czi_shape[0]["S"][-1])
        else:
            entry_indexes = range(len(czi_shape))

        for entry_index in entry_indexes:
            if has_mosaics(czi_dims):
                is_mosaic = czi_shape[entry_index]["M"][-1] > 0
            else:
                is_mosaic = False

            if not is_mosaic:
                logger.info(f"Processing entry {entry_index}")
                if has_stacks(czi_dims):
                    img, dims = get_stack_data(czi, entry_index)
                else:
                    img, dims = get_scene_data(czi, entry_index)
                logger.info(f"Extracted image data shape: {img.shape}")
                logger.info(f"Extracted dimensions: {dims}")
                img = img.squeeze()
                logger.info(f"Squeezed image data shape: {img.shape}")
                if len(img.shape) > 3:
                    # logger.debug("Image has more than 3 dimensions, swapping channel and Z axes")
                    if not has_stacks(czi_dims):
                        img = np.swapaxes(img, 0, 1)
                    logger.info(f"Swapped axes image data shape: {img.shape}")
            else:
                logger.info(f"Processing mosaic entry {entry_index}")
                img = get_mosaic_data(czi, entry_index, czi_dims, czi_shape)
                logger.info(f"Mosaic image data shape: {img.shape}")

            export_params.output_dir.mkdir(parents=True, exist_ok=True)

            output_path = (
                export_params.output_dir / f"{Path(czi_file).stem}_{entry_index}.tif"
            )
            logger.info(f"Exporting to: {output_path}")

            imwrite(
                output_path,
                img,
                resolution=(resolution[0], resolution[1]),
                resolutionunit=RESUNIT.MICROMETER,
                imagej=True,
                metadata={"spacing": resolution, "unit": "micron"},
            )

    except Exception as e:
        logger.error(f"Error processing file {czi_file}: {e}")
        raise


def process_lif(lif_path: Path, export_params: ExportParams) -> None:
    """Process a single LIF file and extract resolution information."""
    logger.info(f"Processing LIF file: {Path(lif_path).name}")

    lif_file = LifFile(lif_path)

    for image in lif_file.get_iter_image():
        logger.info(f"Processing image: {image.name}")

        resolution = image.scale
        if resolution is None:
            logger.warning(
                "No resolution found in metadata. Assuming 1 pixel per micron."
            )
            resolution = (1, 1, 1)
        else:
            logger.info(f"Extracted resolution: {resolution}")

        # Get image data
        img_data = np.array(image.get_frame())
        logger.info(f"Image data shape: {img_data.shape}")

        # Export to TIF
        export_params.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = (
            export_params.output_dir / f"{Path(lif_path).stem}_{image.name}.tif"
        )
        logger.info(f"Exporting to: {output_path}")

        imwrite(
            output_path,
            img_data,
            resolution=(resolution[0], resolution[1]),
            resolutionunit=RESUNIT.MICROMETER,
            imagej=True,
            metadata={"spacing": resolution, "unit": "micron"},
        )


def process_file(czi_file: Pathlike, export_params: ExportParams) -> None:
    """Process a single CZI file and extract resolution information."""
    logger.info(f"Processing CZI file: {Path(czi_file).name}")

    if isinstance(czi_file, str):
        czi_file = Path(czi_file)

    file_extension = czi_file.suffix.lower()
    if file_extension == ".czi":
        process_czi(czi_file, export_params)
    elif file_extension == ".lif":
        process_lif(czi_file, export_params)
    else:
        logger.error(f"Unsupported file format: {file_extension}")
        raise ValueError(f"Unsupported file format: {file_extension}")
