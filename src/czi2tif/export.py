from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExportParams:
    output_dir: Path
    bit_depth: int