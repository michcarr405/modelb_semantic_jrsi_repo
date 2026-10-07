"""Compatibility entry point for the current packaging validator."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("validate_packaged.py")), run_name="__main__")
