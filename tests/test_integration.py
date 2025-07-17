"""Integration tests for czi2tif functionality."""
import pytest
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
import numpy as np
import tempfile
import shutil

from czi2tif.read import process_file
from czi2tif.export import ExportParams


class TestIntegration:
    """Integration tests for the complete czi2tif pipeline."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.output_dir = self.test_dir / "output"
        self.export_params = ExportParams(
            output_dir=self.output_dir,
            bit_depth=16
        )

    def teardown_method(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @patch('czi2tif.read.CziFile')
    @patch('czi2tif.read.imwrite')
    def test_czi_processing_pipeline(self, mock_imwrite, mock_czi_file):
        """Test complete CZI processing pipeline."""
        # Mock CZI file
        mock_czi = Mock()
        mock_czi.dims = "TCZYX"
        mock_czi.get_dims_shape.return_value = [{"S": (0, 1), "Z": (0, 2), "C": (0, 1)}]
        mock_czi.read_image.return_value = (
            np.random.randint(0, 255, (1, 1, 1, 100, 100), dtype=np.uint8),
            ['T', 'C', 'Z', 'Y', 'X']
        )
        
        # Mock metadata for resolution extraction
        mock_metadata = Mock()
        mock_czi.meta = mock_metadata
        
        mock_czi_file.return_value = mock_czi
        
        # Create test file
        test_file = self.test_dir / "test.czi"
        test_file.touch()
        
        with patch('czi2tif.read.get_resolution', return_value=(1.0, 1.0, 1.0)):
            process_file(test_file, self.export_params)
        
        # Verify the pipeline executed
        mock_czi_file.assert_called_once()
        mock_imwrite.assert_called_once()
        
        # Check that output directory was created
        assert self.output_dir.exists()

    @patch('czi2tif.read.LifFile')
    @patch('czi2tif.read.imwrite')
    def test_lif_processing_pipeline(self, mock_imwrite, mock_lif_file):
        """Test complete LIF processing pipeline."""
        # Mock LIF file
        mock_image = Mock()
        mock_image.name = "test_image"
        mock_image.scale = (1.0, 1.0, 1.0)
        mock_image.get_frame.return_value = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        mock_lif = Mock()
        mock_lif.get_iter_image.return_value = [mock_image]
        mock_lif_file.return_value = mock_lif
        
        # Create test file
        test_file = self.test_dir / "test.lif"
        test_file.touch()
        
        process_file(test_file, self.export_params)
        
        # Verify the pipeline executed
        mock_lif_file.assert_called_once()
        mock_imwrite.assert_called_once()
        
        # Check that output directory was created
        assert self.output_dir.exists()

    @patch('czi2tif.read.LifFile')
    @patch('czi2tif.read.imwrite')
    def test_lif_multiple_images(self, mock_imwrite, mock_lif_file):
        """Test LIF processing with multiple images."""
        # Mock multiple images
        mock_images = []
        for i in range(3):
            mock_image = Mock()
            mock_image.name = f"image_{i}"
            mock_image.scale = (1.0, 1.0, 1.0)
            mock_image.get_frame.return_value = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            mock_images.append(mock_image)
        
        mock_lif = Mock()
        mock_lif.get_iter_image.return_value = mock_images
        mock_lif_file.return_value = mock_lif
        
        # Create test file
        test_file = self.test_dir / "test.lif"
        test_file.touch()
        
        process_file(test_file, self.export_params)
        
        # Verify the pipeline executed for all images
        mock_lif_file.assert_called_once()
        assert mock_imwrite.call_count == 3  # One call per image
        
        # Check that output directory was created
        assert self.output_dir.exists()

    @patch('czi2tif.read.CziFile')
    @patch('czi2tif.read.imwrite')
    def test_czi_with_scenes(self, mock_imwrite, mock_czi_file):
        """Test CZI processing with multiple scenes."""
        # Mock CZI file with scenes
        mock_czi = Mock()
        mock_czi.dims = "STCZYX"
        mock_czi.get_dims_shape.return_value = [{"S": (0, 3), "Z": (0, 2), "C": (0, 1)}]  # 3 scenes
        mock_czi.read_image.return_value = (
            np.random.randint(0, 255, (1, 1, 1, 100, 100), dtype=np.uint8),
            ['T', 'C', 'Z', 'Y', 'X']
        )
        
        mock_metadata = Mock()
        mock_czi.meta = mock_metadata
        
        mock_czi_file.return_value = mock_czi
        
        # Create test file
        test_file = self.test_dir / "test.czi"
        test_file.touch()
        
        with patch('czi2tif.read.get_resolution', return_value=(1.0, 1.0, 1.0)):
            process_file(test_file, self.export_params)
        
        # Verify the pipeline executed for all scenes
        mock_czi_file.assert_called_once()
        assert mock_imwrite.call_count == 3  # One call per scene

    def test_unsupported_format_error(self):
        """Test that unsupported formats raise appropriate errors."""
        test_file = self.test_dir / "test.txt"
        test_file.touch()
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            process_file(test_file, self.export_params)

    @patch('czi2tif.read.CziFile')
    def test_czi_file_read_error(self, mock_czi_file):
        """Test handling of CZI file read errors."""
        mock_czi_file.side_effect = Exception("Cannot read file")
        
        test_file = self.test_dir / "test.czi"
        test_file.touch()
        
        with pytest.raises(Exception):
            process_file(test_file, self.export_params)

    @patch('czi2tif.read.LifFile')
    def test_lif_file_read_error(self, mock_lif_file):
        """Test handling of LIF file read errors."""
        mock_lif_file.side_effect = Exception("Cannot read file")
        
        test_file = self.test_dir / "test.lif"
        test_file.touch()
        
        with pytest.raises(Exception):
            process_file(test_file, self.export_params)

    @patch('czi2tif.read.CziFile')
    @patch('czi2tif.read.imwrite')
    def test_output_directory_creation(self, mock_imwrite, mock_czi_file):
        """Test that output directory is created if it doesn't exist."""
        # Mock CZI file
        mock_czi = Mock()
        mock_czi.dims = "TCZYX"
        mock_czi.get_dims_shape.return_value = [{"S": (0, 1), "Z": (0, 2), "C": (0, 1)}]
        mock_czi.read_image.return_value = (
            np.random.randint(0, 255, (1, 1, 1, 100, 100), dtype=np.uint8),
            ['T', 'C', 'Z', 'Y', 'X']
        )
        mock_czi.meta = Mock()
        mock_czi_file.return_value = mock_czi
        
        # Use a nested output directory that doesn't exist
        nested_output = self.test_dir / "nested" / "output"
        export_params = ExportParams(output_dir=nested_output, bit_depth=16)
        
        # Create test file
        test_file = self.test_dir / "test.czi"
        test_file.touch()
        
        with patch('czi2tif.read.get_resolution', return_value=(1.0, 1.0, 1.0)):
            process_file(test_file, export_params)
        
        # Verify the output directory was created
        assert nested_output.exists()
        assert nested_output.is_dir()
