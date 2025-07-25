"""Tests for czi2tif.read module."""
import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
import numpy as np
import xml.etree.ElementTree as ET

from czi2tif.read import (
    read_czi, get_resolution, has_scenes, has_mosaics, has_stacks,
    get_scene_data, get_stack_data, process_czi, process_lif, process_file
)
from czi2tif.export import ExportParams


class TestReadModule:
    """Tests for the read module functions."""

    def test_read_module_imports(self):
        """Test that the read module can be imported."""
        from czi2tif import read
        assert read is not None

    @patch('czi2tif.read.CziFile')
    def test_read_czi_success(self, mock_czi_file):
        """Test successful CZI file reading."""
        mock_czi_obj = Mock()
        mock_czi_file.return_value = mock_czi_obj
        
        result = read_czi("test.czi")
        
        mock_czi_file.assert_called_once_with("test.czi")
        assert result == mock_czi_obj

    @patch('czi2tif.read.CziFile')
    def test_read_czi_failure(self, mock_czi_file):
        """Test CZI file reading failure."""
        mock_czi_file.side_effect = Exception("File not found")
        
        with pytest.raises(Exception):
            read_czi("nonexistent.czi")

    def test_get_resolution_with_xyz(self):
        """Test resolution extraction with X, Y, Z coordinates."""
        xml_content = """
        <root>
            <Distance Id="X">
                <Value>1.0e-6</Value>
            </Distance>
            <Distance Id="Y">
                <Value>1.0e-6</Value>
            </Distance>
            <Distance Id="Z">
                <Value>2.0e-6</Value>
            </Distance>
        </root>
        """
        metadata = ET.fromstring(xml_content)
        
        resolution = get_resolution(metadata)
        
        assert len(resolution) == 3
        assert resolution[0] == 1.0  # 1 / (1.0e-6 * 1e6) = 1.0
        assert resolution[1] == 1.0
        assert resolution[2] == 0.5  # 1 / (2.0e-6 * 1e6) = 0.5

    def test_get_resolution_with_xy_only(self):
        """Test resolution extraction with X, Y coordinates only."""
        xml_content = """
        <root>
            <Distance Id="X">
                <Value>1.0e-6</Value>
            </Distance>
            <Distance Id="Y">
                <Value>1.0e-6</Value>
            </Distance>
        </root>
        """
        metadata = ET.fromstring(xml_content)
        
        resolution = get_resolution(metadata)
        
        assert len(resolution) == 2
        assert resolution[0] == 1.0
        assert resolution[1] == 1.0

    def test_get_resolution_no_metadata(self):
        """Test resolution extraction when no metadata is present."""
        xml_content = "<root></root>"
        metadata = ET.fromstring(xml_content)
        
        resolution = get_resolution(metadata)
        
        assert resolution == (1, 1, 1)

    def test_has_scenes(self):
        """Test scene detection in CZI dimensions."""
        assert has_scenes("STCZYX") is True
        assert has_scenes("TCZYX") is False

    def test_has_mosaics(self):
        """Test mosaic detection in CZI dimensions."""
        assert has_mosaics("MTCZYX") is True
        assert has_mosaics("TCZYX") is False

    def test_has_stacks(self):
        """Test stack detection in CZI dimensions."""
        assert has_stacks("TCZYX") is True
        assert has_stacks("TCYX") is False

    def test_get_scene_data(self):
        """Test scene data extraction."""
        mock_czi = Mock()
        mock_data = np.array([[[1, 2, 3]]])
        mock_dims = ['T', 'C', 'Y', 'X']
        mock_czi.read_image.return_value = (mock_data, mock_dims)
        
        data, dims = get_scene_data(mock_czi, 0)
        
        mock_czi.read_image.assert_called_once_with(S=0)
        assert np.array_equal(data, mock_data)
        assert dims == mock_dims

    def test_get_stack_data(self):
        """Test stack data extraction."""
        mock_czi = Mock()
        mock_czi.get_dims_shape.return_value = [{"Z": (0, 2), "C": (0, 2)}]
        mock_czi.read_image.return_value = (np.array([[[1, 2, 3]]]), ['T', 'C', 'Y', 'X'])
        
        data, dims = get_stack_data(mock_czi, 0)
        
        assert mock_czi.read_image.call_count == 4  # 2 Z planes * 2 channels
        assert data.shape == (2, 2, 1, 1, 3)  # Z, C, T, C, Y, X

    @patch('czi2tif.read.read_czi')
    @patch('czi2tif.read.get_resolution')
    @patch('czi2tif.read.imwrite')
    def test_process_czi_single_scene(self, mock_imwrite, mock_get_resolution, mock_read_czi):
        """Test processing a single scene CZI file."""
        mock_czi = Mock()
        mock_czi.dims = "TCYX"  # No Z dimension to avoid stack processing
        mock_czi.get_dims_shape.return_value = [{"S": (0, 1)}]
        mock_czi.read_image.return_value = (np.array([[[[1, 2, 3]]]]), ['T', 'C', 'Y', 'X'])
        mock_czi.meta = Mock()
        
        mock_read_czi.return_value = mock_czi
        mock_get_resolution.return_value = (1.0, 1.0, 1.0)
        
        export_params = ExportParams(output_dir=Path("/tmp/test"), bit_depth=16)
        
        process_czi(Path("test.czi"), export_params)
        
        mock_read_czi.assert_called_once()
        mock_get_resolution.assert_called_once()
        mock_imwrite.assert_called_once()

    @patch('czi2tif.read.LifFile')
    @patch('czi2tif.read.imwrite')
    def test_process_lif(self, mock_imwrite, mock_lif_file):
        """Test processing a LIF file."""
        mock_image = Mock()
        mock_image.name = "test_image"
        mock_image.scale = (1.0, 1.0, 1.0)
        mock_image.get_frame.return_value = np.array([[[1, 2, 3]]])
        
        mock_lif_obj = Mock()
        mock_lif_obj.get_iter_image.return_value = [mock_image]
        mock_lif_file.return_value = mock_lif_obj
        
        export_params = ExportParams(output_dir=Path("/tmp/test"), bit_depth=16)
        
        process_lif(Path("test.lif"), export_params)
        
        mock_lif_file.assert_called_once_with(Path("test.lif"))
        mock_imwrite.assert_called_once()

    @patch('czi2tif.read.LifFile')
    @patch('czi2tif.read.imwrite')
    def test_process_lif_no_resolution(self, mock_imwrite, mock_lif_file):
        """Test processing a LIF file without resolution metadata."""
        mock_image = Mock()
        mock_image.name = "test_image"
        mock_image.scale = None
        mock_image.get_frame.return_value = np.array([[[1, 2, 3]]])
        
        mock_lif_obj = Mock()
        mock_lif_obj.get_iter_image.return_value = [mock_image]
        mock_lif_file.return_value = mock_lif_obj
        
        export_params = ExportParams(output_dir=Path("/tmp/test"), bit_depth=16)
        
        process_lif(Path("test.lif"), export_params)
        
        mock_lif_file.assert_called_once_with(Path("test.lif"))
        mock_imwrite.assert_called_once()

    @patch('czi2tif.read.process_czi')
    def test_process_file_czi(self, mock_process_czi):
        """Test processing a CZI file through process_file."""
        export_params = ExportParams(output_dir=Path("/tmp/test"), bit_depth=16)
        
        process_file("test.czi", export_params)
        
        mock_process_czi.assert_called_once()

    @patch('czi2tif.read.process_lif')
    def test_process_file_lif(self, mock_process_lif):
        """Test processing a LIF file through process_file."""
        export_params = ExportParams(output_dir=Path("/tmp/test"), bit_depth=16)
        
        process_file("test.lif", export_params)
        
        mock_process_lif.assert_called_once()

    def test_process_file_unsupported_format(self):
        """Test processing an unsupported file format."""
        export_params = ExportParams(output_dir=Path("/tmp/test"), bit_depth=16)
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            process_file("test.txt", export_params) 