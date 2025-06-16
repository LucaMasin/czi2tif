from typing import Union, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET

from aicspylibczi import CziFile


Pathlike = Union[str, Path]


def read_czi(czi_file: Pathlike) -> CziFile:
    return CziFile(czi_file)


def get_resolution(metadata: ET.Element) -> Tuple[float, float, float]:
    """Get the resolution from the czi metadata."""
    root = ET.ElementTree(metadata).getroot()

    distance_element = root.find(".//Distance[@Id='X']/Value")
    if distance_element is None:
        print("No resolution found in metadata. Assuming 1 pixel per micron.")
        return (1, 1, 1)
    else:
        res_x = float(distance_element.text)  # type: ignore
        # convert to pixels per micron
        res_x = 1 / (res_x * 1e6)
        distance_element = root.find(".//Distance[@Id='Y']/Value")
        res_y = float(distance_element.text)  # type: ignore
        try:
            distance_element = root.find(".//Distance[@Id='Z']/Value")
            res_z = float(distance_element.text)
        except AttributeError:
            res_z = 1
        # convert to pixels per micron
        res_y = 1 / (res_y * 1e6)
        res_z = 1 / (res_z * 1e6)

        return (res_x, res_y, res_z)


def process_file(czi_file: Pathlike) -> None:
    czi = read_czi(czi_file)
    resolution = get_resolution(czi.meta)
    print(resolution)
