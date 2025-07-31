# czi2tif

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A fast and reliable CLI tool to convert CZI and LIF microscopy files to TIF format while preserving scaling information for use in Fiji/ImageJ.

## Features

- 🔬 Convert CZI and LIF files to TIF format
- 📏 Preserve spatial scaling/resolution information for Fiji/ImageJ
- 📁 Batch processing with recursive directory support
- 🎛️ Configurable bit depth (8, 16, 32-bit)
- 🔍 Multi-scene and Z-stack support
- 📊 Comprehensive logging with customizable levels
- ⚡ Fast processing with efficient memory usage

## Installation

> **NOTE:** If you're on a managed/restricted system (e.g., Windows without admin access), see the [conda + uv section](#for-restricted-environments-using-conda--uv) below for an alternative installation method.

### Recommended: Using uv (fastest)

[uv](https://github.com/astral-sh/uv) is the recommended way to install and run `czi2tif`. It's significantly faster than pip and handles Python versions automatically.

#### Install uv first (if you haven't already):

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**

*Option 1: PowerShell (Recommended)*
```powershell
# Run this in PowerShell (run as Administrator if needed)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

*Option 2: Scoop*
```powershell
# Install Scoop first if you don't have it: https://scoop.sh/
scoop install main/uv
```

*Option 3: WinGet*
```cmd
# In Command Prompt or PowerShell
winget install --id=astral-sh.uv -e
```

*Option 4: pip (Universal)*
```cmd
pip install uv
```

**Windows Notes:**
- If you get execution policy errors, run PowerShell as Administrator
- After installation, restart your terminal or Command Prompt
- Add `%USERPROFILE%\.local\bin` to your PATH if uv commands aren't recognized

#### Install and run czi2tif:

**All platforms (Linux, macOS, Windows):**
```bash
# Option 1: Install globally with uv
uv tool install czi2tif

# Option 2: Run directly without installation (recommended for trying out)
uvx czi2tif --help

# Option 3: Run from this repository
git clone https://github.com/LucaMasin/czi2tif.git
cd czi2tif
uv run czi2tif --help
```

**Windows-specific considerations:**
- Use PowerShell, Command Prompt, or Windows Terminal
- File paths can use forward slashes (`/`) or backslashes (`\`)
- Use quotes around paths with spaces: `uvx czi2tif "C:\My Documents\image.czi"`

### Alternative: Using pip

```bash
pip install czi2tif
```

### For Restricted Environments: Using conda + uv

If you're on a managed system (like Windows with restricted admin access) where installing uv globally is problematic, you can use conda to create an isolated environment with both Python and uv:

#### First, install Miniconda (if you don't have conda already)

1. Download [Miniconda for Windows](https://www.anaconda.com/download/success)
2. Run the installer - it typically doesn't require admin rights when installing for current user only
3. During installation, choose "Add Miniconda3 to my PATH environment variable" if asked
4. Open a new Command Prompt or PowerShell window

#### Then, set up the czi2tif environment

```bash
# Clone or download the repository first
git clone https://github.com/LucaMasin/czi2tif.git
cd czi2tif

# Create and activate the conda environment
conda env create -f environment.yml
conda activate czi2tif

# Now use uv within the conda environment
uv sync
uv run czi2tif --help
```

**Alternative without git:**
```bash
# Download and extract the ZIP from GitHub, then:
cd czi2tif
conda env create -f environment.yml
conda activate czi2tif
uv sync
uv run czi2tif --help
```

This approach is ideal for:
- Corporate/managed Windows environments
- Systems where you don't have admin privileges
- Situations where the standard uv installation methods don't work

### Development Installation

**Linux/macOS:**
```bash
git clone https://github.com/LucaMasin/czi2tif.git
cd czi2tif
uv sync --dev
```

**Windows:**
```cmd
git clone https://github.com/LucaMasin/czi2tif.git
cd czi2tif
uv sync --dev

REM Alternative if you don't have git:
REM Download ZIP from GitHub and extract to a folder
REM Open Command Prompt in that folder and run:
uv sync --dev
```

## Usage

### Basic Usage

```bash
# Convert a single file
czi2tif input.czi

# Convert with custom output directory
czi2tif input.czi -o /path/to/output

# Convert all files in a directory
czi2tif /path/to/directory

# Recursive conversion of all files in subdirectories
czi2tif /path/to/directory -r
```

### Advanced Options

```bash
# Convert with specific bit depth
czi2tif input.czi --bit-depth 16

# Enable verbose logging
czi2tif input.czi -v

# Save logs to file
czi2tif input.czi --log-file conversion.log

# Quiet mode (no console output)
czi2tif input.czi -q --log-file conversion.log
```

### Command Line Options

```
Usage: czi2tif [OPTIONS] INPUT

  Convert CZI files to TIF format with scaling information.

Arguments:
  INPUT  Path to CZI/LIF file or directory containing files

Options:
  -o, --output PATH           Output directory (default: ./tif)
  -r, --recursive            Convert all files in subdirectories
  -v, --verbose              Enable verbose logging
  -q, --quiet                Disable console logging
  --log-file PATH            Save logs to file
  -bd, --bit-depth [8|16|32] Output bit depth (default: 16)
  --help                     Show this message and exit
```

## Examples

### Single File Conversion

**Linux/macOS:**
```bash
# Convert single CZI file to TIF
czi2tif experiment_001.czi
# Output: ./tif/experiment_001_0.tif

# Convert LIF file with custom output
czi2tif sample.lif -o ./converted_images
```

**Windows:**
```cmd
# Convert single CZI file to TIF
czi2tif experiment_001.czi
# Output: .\tif\experiment_001_0.tif

# Convert LIF file with custom output  
czi2tif sample.lif -o .\converted_images

# With full Windows paths
czi2tif "C:\Data\Microscopy\experiment_001.czi" -o "D:\Output\TIF_Files"

# Handle paths with spaces
czi2tif "C:\My Documents\Microscopy Data\sample.czi"
```

### Batch Processing

**Linux/macOS:**
```bash
# Convert all CZI files in current directory
czi2tif . 

# Convert all files recursively with verbose logging
czi2tif /microscopy_data -r -v

# Process directory with custom settings
czi2tif /data/images -o /data/tif_output --bit-depth 32 -r
```

**Windows:**
```cmd
# Convert all CZI files in current directory
czi2tif .

# Convert all files recursively with verbose logging
czi2tif "C:\Microscopy_Data" -r -v

# Process directory with custom settings
czi2tif "D:\Data\Images" -o "D:\Data\TIF_Output" --bit-depth 32 -r

# Using PowerShell with long paths
czi2tif "C:\Users\Username\Documents\Research\Microscopy Images" -r -o "C:\Users\Username\Desktop\Converted"
```

### Advanced Logging

```bash
# Detailed logging to file
czi2tif experiment.czi -v --log-file detailed.log

# Silent processing with log file only
czi2tif batch_data/ -r -q --log-file batch_conversion.log
```

## Supported File Formats

- **CZI**: Carl Zeiss Image files (multi-scene, multi-channel, Z-stacks)
- **LIF**: Leica Image Format files

## Output Format

- **TIF/TIFF**: Tagged Image File Format
- Preserves spatial scaling information as metadata
- Compatible with Fiji/ImageJ for accurate measurements
- Supports 8, 16, and 32-bit output

## Technical Details

### Resolution Handling

The tool automatically extracts and converts spatial resolution information from the source files:
- Reads pixel size from metadata (in meters)
- Converts to pixels per micron for TIF metadata
- Stores resolution in TIF file for Fiji/ImageJ compatibility

### Multi-dimensional Data

- **Scenes**: Multiple fields of view are saved as separate TIF files
- **Z-stacks**: Preserved as multi-page TIF files
- **Channels**: Handled appropriately based on file structure
- **Time series**: Supported where present in source files

### Memory Efficiency

- Processes images slice-by-slice for large datasets
- Optimized for minimal memory footprint
- Handles files larger than available RAM

## Requirements

- Python 3.11 or higher
- Dependencies automatically handled by uv/pip

## Troubleshooting

### Windows-Specific Issues

**"uv command not found" or "'uv' is not recognized":**
```cmd
# Option 1: Restart your terminal/Command Prompt after installation
# Option 2: Add uv to your PATH manually
set PATH=%PATH%;%USERPROFILE%\.local\bin

# Option 3: Use full path
%USERPROFILE%\.local\bin\uv --version
```

**PowerShell Execution Policy Error:**
```powershell
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run the installer with bypass (one-time):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Permission Denied Errors:**
- Run Command Prompt or PowerShell as Administrator
- Ensure you have write permissions to the output directory
- Use a different output directory: `-o "C:\Users\%USERNAME%\Desktop\output"`

**Long Path Issues (Windows 10/11):**
```cmd
# Enable long path support (requires Admin rights):
# Go to: Computer Configuration > Administrative Templates > System > Filesystem
# Enable "Enable Win32 long paths"

# Or use shorter paths and avoid deeply nested directories
```

### General Issues

**"No module named 'czi2tif'" after installation:**
```bash
# Ensure you're using the correct Python environment
uv tool list  # Check if czi2tif is installed
uv tool install --force czi2tif  # Force reinstall
```

**Out of memory errors with large files:**
```bash
# Process files individually instead of batch processing
czi2tif large_file.czi --verbose  # Monitor progress
```

## Development

### Running Tests

**All platforms:**
```bash
# With uv (recommended)
uv run pytest

# With pip
pip install -e ".[dev]"
pytest
```

**Windows Command Prompt:**
```cmd
REM With uv (recommended)
uv run pytest

REM With pip
pip install -e ".[dev]"
pytest
```

### Project Structure

```
czi2tif/
├── src/czi2tif/          # Main package
│   ├── czi2tif.py        # CLI interface
│   ├── read.py           # File reading and processing
│   ├── export.py         # Export configuration
│   └── logging.py        # Logging utilities
├── tests/                # Test suite
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install development dependencies: `uv sync --dev`
4. Make your changes and add tests
5. Run tests: `uv run pytest`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- **Luca Masin** - [luca.mas93@gmail.com](mailto:luca.mas93@gmail.com)

## Acknowledgments

- Built with [aicspylibczi](https://github.com/AllenCellModeling/aicspylibczi) for CZI file support
- Uses [readlif](https://github.com/nimne/readlif) for LIF file support
- Powered by [tifffile](https://github.com/cgohlke/tifffile) for TIF output

---

💡 **Tip**: Use `uvx czi2tif --help` to quickly try the tool without installation!