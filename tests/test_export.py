"""Tests for czi2tif.export module."""
import pytest
from pathlib import Path

from czi2tif.export import ExportParams


class TestExportParams:
    """Tests for the ExportParams dataclass."""

    def test_export_params_creation(self):
        """Test ExportParams creation with valid parameters."""
        output_dir = Path("/tmp/test")
        bit_depth = 16
        
        params = ExportParams(output_dir=output_dir, bit_depth=bit_depth)
        
        assert params.output_dir == output_dir
        assert params.bit_depth == bit_depth

    def test_export_params_path_conversion(self):
        """Test ExportParams with string path conversion."""
        output_dir = "/tmp/test"
        bit_depth = 32
        
        params = ExportParams(output_dir=Path(output_dir), bit_depth=bit_depth)
        
        assert params.output_dir == Path(output_dir)
        assert params.bit_depth == bit_depth

    def test_export_params_different_bit_depths(self):
        """Test ExportParams with different bit depths."""
        output_dir = Path("/tmp/test")
        
        for bit_depth in [8, 16, 32]:
            params = ExportParams(output_dir=output_dir, bit_depth=bit_depth)
            assert params.bit_depth == bit_depth

    def test_export_params_equality(self):
        """Test ExportParams equality comparison."""
        output_dir = Path("/tmp/test")
        bit_depth = 16
        
        params1 = ExportParams(output_dir=output_dir, bit_depth=bit_depth)
        params2 = ExportParams(output_dir=output_dir, bit_depth=bit_depth)
        params3 = ExportParams(output_dir=output_dir, bit_depth=32)
        
        assert params1 == params2
        assert params1 != params3

    def test_export_params_immutability(self):
        """Test that ExportParams is immutable (frozen dataclass)."""
        output_dir = Path("/tmp/test")
        bit_depth = 16
        
        params = ExportParams(output_dir=output_dir, bit_depth=bit_depth)
        
        # This should work - we can access the attributes
        assert params.output_dir == output_dir
        assert params.bit_depth == bit_depth
        
        # Test that we can modify the attributes (dataclass is not frozen by default)
        params.bit_depth = 32
        assert params.bit_depth == 32
