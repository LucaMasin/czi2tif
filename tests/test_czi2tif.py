"""Tests for czi2tif main functionality."""

from unittest.mock import patch
from pathlib import Path
from click.testing import CliRunner

from czi2tif.czi2tif import main


class TestMainFunctionality:
    """Tests for the main czi2tif functionality."""

    def test_main_function_exists(self):
        """Test that the main function can be imported."""
        from czi2tif import main

        assert main is not None

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_single_czi_file(self, mock_setup_logging, mock_process_file):
        """Test CLI with a single CZI file."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test CZI file
            test_file = Path("test.czi")
            test_file.touch()

            result = runner.invoke(main, [str(test_file)])

            assert result.exit_code == 0
            mock_process_file.assert_called_once()
            mock_setup_logging.assert_called_once()

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_single_lif_file(self, mock_setup_logging, mock_process_file):
        """Test CLI with a single LIF file."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test LIF file
            test_file = Path("test.lif")
            test_file.touch()

            result = runner.invoke(main, [str(test_file)])

            assert result.exit_code == 0
            mock_process_file.assert_called_once()
            mock_setup_logging.assert_called_once()

    def test_cli_unsupported_file_format(self):
        """Test CLI with an unsupported file format."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test file with unsupported extension
            test_file = Path("test.txt")
            test_file.touch()

            result = runner.invoke(main, [str(test_file)])

            assert result.exit_code != 0

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_directory_processing(self, mock_setup_logging, mock_process_file):
        """Test CLI with directory containing multiple files."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create test directory with files
            test_dir = Path("test_dir")
            test_dir.mkdir()

            czi_file = test_dir / "test1.czi"
            lif_file = test_dir / "test2.lif"
            txt_file = test_dir / "test3.txt"  # Should be ignored

            czi_file.touch()
            lif_file.touch()
            txt_file.touch()

            result = runner.invoke(main, [str(test_dir)])

            assert result.exit_code == 0
            # Should be called twice (once for each supported file)
            assert mock_process_file.call_count == 2
            mock_setup_logging.assert_called_once()

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_recursive_processing(self, mock_setup_logging, mock_process_file):
        """Test CLI with recursive directory processing."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create nested directory structure
            test_dir = Path("test_dir")
            sub_dir = test_dir / "subdir"
            sub_dir.mkdir(parents=True)

            czi_file1 = test_dir / "test1.czi"
            czi_file2 = sub_dir / "test2.czi"

            czi_file1.touch()
            czi_file2.touch()

            result = runner.invoke(main, [str(test_dir), "--recursive"])

            assert result.exit_code == 0
            # Should be called twice (both files found recursively)
            assert mock_process_file.call_count == 2
            mock_setup_logging.assert_called_once()

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_custom_output_directory(self, mock_setup_logging, mock_process_file):
        """Test CLI with custom output directory."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            test_file = Path("test.czi")
            test_file.touch()

            result = runner.invoke(main, [str(test_file), "--output", "custom_output"])

            assert result.exit_code == 0
            mock_process_file.assert_called_once()

            # Check that ExportParams was created with custom output directory
            call_args = mock_process_file.call_args
            export_params = call_args[0][1]
            assert export_params.output_dir == Path("custom_output")

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_bit_depth_option(self, mock_setup_logging, mock_process_file):
        """Test CLI with custom bit depth."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            test_file = Path("test.czi")
            test_file.touch()

            result = runner.invoke(main, [str(test_file), "--bit-depth", "32"])

            assert result.exit_code == 0
            mock_process_file.assert_called_once()

            # Check that ExportParams was created with custom bit depth
            call_args = mock_process_file.call_args
            export_params = call_args[0][1]
            assert export_params.bit_depth == 32

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_verbose_logging(self, mock_setup_logging, mock_process_file):
        """Test CLI with verbose logging enabled."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            test_file = Path("test.czi")
            test_file.touch()

            result = runner.invoke(main, [str(test_file), "--verbose"])

            assert result.exit_code == 0
            mock_setup_logging.assert_called_once()

            # Check that setup_logging was called with DEBUG level
            call_args = mock_setup_logging.call_args
            assert call_args[1]["log_level"] == "DEBUG"

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_quiet_logging(self, mock_setup_logging, mock_process_file):
        """Test CLI with quiet logging enabled."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            test_file = Path("test.czi")
            test_file.touch()

            result = runner.invoke(main, [str(test_file), "--quiet"])

            assert result.exit_code == 0
            mock_setup_logging.assert_called_once()

            # Check that setup_logging was called with quiet=True
            call_args = mock_setup_logging.call_args
            assert call_args[1]["quiet"] is True

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_log_file_option(self, mock_setup_logging, mock_process_file):
        """Test CLI with log file option."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            test_file = Path("test.czi")
            test_file.touch()

            result = runner.invoke(main, [str(test_file), "--log-file", "test.log"])

            assert result.exit_code == 0
            mock_setup_logging.assert_called_once()

            # Check that setup_logging was called with log file
            call_args = mock_setup_logging.call_args
            assert call_args[1]["log_file"] == Path("test.log")
            assert call_args[1]["file_output"] is True

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_verbose_and_quiet_conflict(
        self, mock_setup_logging, mock_process_file
    ):
        """Test CLI with both verbose and quiet flags (should prioritize verbose)."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            test_file = Path("test.czi")
            test_file.touch()

            result = runner.invoke(main, [str(test_file), "--verbose", "--quiet"])

            assert result.exit_code == 0
            mock_setup_logging.assert_called_once()

            # Check that setup_logging was called with verbose settings (quiet overridden)
            call_args = mock_setup_logging.call_args
            assert call_args[1]["log_level"] == "DEBUG"
            assert call_args[1]["quiet"] is False

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_file_processing_error(self, mock_setup_logging, mock_process_file):
        """Test CLI behavior when file processing fails."""
        runner = CliRunner()

        mock_process_file.side_effect = Exception("Processing failed")

        with runner.isolated_filesystem():
            test_file = Path("test.czi")
            test_file.touch()

            result = runner.invoke(main, [str(test_file)])

            assert result.exit_code == 0  # Should not crash, just log error
            mock_process_file.assert_called_once()
            mock_setup_logging.assert_called_once()

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_directory_processing_with_match(
        self, mock_setup_logging, mock_process_file
    ):
        """Test CLI directory processing with --match filters only matching files."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            test_dir = Path("test_dir")
            test_dir.mkdir()

            # Files: only those containing 'match' should be processed
            (test_dir / "a_match_1.czi").touch()
            (test_dir / "a_unrelated_2.czi").touch()
            (test_dir / "b_match_3.lif").touch()
            (test_dir / "ignore.txt").touch()  # unsupported

            result = runner.invoke(main, [str(test_dir), "--match", "match"])

            assert result.exit_code == 0
            # Expect only 2 matching files (czi + lif)
            assert mock_process_file.call_count == 2
            processed = sorted(
                call.args[0].name for call in mock_process_file.call_args_list
            )
            assert processed == ["a_match_1.czi", "b_match_3.lif"]
            mock_setup_logging.assert_called_once()

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_recursive_processing_with_match(
        self, mock_setup_logging, mock_process_file
    ):
        """Test CLI recursive processing with --match filters across subdirectories."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            base = Path("base_dir")
            (base / "sub1").mkdir(parents=True)
            (base / "sub2").mkdir(parents=True)

            # Create files across subdirs
            (base / "sub1" / "match_file1.czi").touch()
            (base / "sub1" / "nope1.czi").touch()
            (base / "sub2" / "match_file2.lif").touch()
            (base / "sub2" / "nope2.lif").touch()

            result = runner.invoke(main, [str(base), "--recursive", "--match", "match"])

            assert result.exit_code == 0
            assert mock_process_file.call_count == 2
            processed = sorted(
                call.args[0].name for call in mock_process_file.call_args_list
            )
            assert processed == ["match_file1.czi", "match_file2.lif"]
            mock_setup_logging.assert_called_once()

    @patch("czi2tif.czi2tif.process_file")
    @patch("czi2tif.czi2tif.setup_logging")
    def test_cli_match_no_results(self, mock_setup_logging, mock_process_file):
        """Test CLI with --match that yields no files; should not process any files."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            test_dir = Path("empty_match")
            test_dir.mkdir()
            # Create some files that do not match
            (test_dir / "abc.czi").touch()
            (test_dir / "def.lif").touch()

            result = runner.invoke(main, [str(test_dir), "--match", "zzz"])

            assert result.exit_code == 0
            mock_process_file.assert_not_called()
            mock_setup_logging.assert_called_once()
