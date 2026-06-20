"""Reusable GUI components."""

from __future__ import annotations

import tkinter as tk
from typing import Callable, List, Optional

import customtkinter as ctk

from memory_allocator.models import BlockState, SimulationResult
from memory_allocator.gui.theme import COLORS, FONTS, STRATEGY_COLORS


