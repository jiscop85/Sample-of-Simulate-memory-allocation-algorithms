"""Interactive CLI and simulation runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .console import configure_console_encoding
from .report import (
    build_report,
    print_comparison,
    print_result,
    save_report_to_file,
)
from .simulator import MemoryAllocationSimulator
from .utils import SAMPLE_DATASETS, list_sample_names, load_from_json, parse_int_list, read_int_list
from .visualization import render_comparison_chart, render_memory_map_chart


