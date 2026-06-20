"""Reusable GUI components."""

from __future__ import annotations

import tkinter as tk
from typing import Callable, List, Optional

import customtkinter as ctk

from memory_allocator.models import BlockState, SimulationResult
from memory_allocator.gui.theme import COLORS, FONTS, STRATEGY_COLORS

class StatCard(ctk.CTkFrame):
    """KPI metric card with icon, value, and label."""

    def __init__(
        self,
        master,
        title: str,
        value: str = "—",
        icon: str = "●",
        accent: str = COLORS["primary"],
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self._accent = accent

        accent_bar = ctk.CTkFrame(self, fg_color=accent, height=3, corner_radius=2)
        accent_bar.pack(fill="x", padx=12, pady=(12, 0))

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(10, 0))

        ctk.CTkLabel(
            top,
            text=icon,
            font=("Segoe UI Emoji", 18),
            text_color=accent,
        ).pack(side="left")

        self._value_label = ctk.CTkLabel(
            self,
            text=value,
            font=FONTS["stat_value"],
            text_color=COLORS["text"],
        )
        self._value_label.pack(anchor="w", padx=16, pady=(4, 0))

        self._title_label = ctk.CTkLabel(
            self,
            text=title,
            font=FONTS["stat_label"],
            text_color=COLORS["text_muted"],
        )
        self._title_label.pack(anchor="w", padx=16, pady=(0, 14))

    def set_value(self, value: str, accent: Optional[str] = None) -> None:
        self._value_label.configure(text=value)
        if accent:
            self._accent = accent


class TagChip(ctk.CTkFrame):
    """Small pill tag for numeric values."""

    def __init__(self, master, text: str, color: str = COLORS["primary"], **kwargs) -> None:
        super().__init__(
            master,
            fg_color=COLORS["bg_elevated"],
            corner_radius=20,
            border_width=1,
            border_color=color,
            **kwargs,
        )
        ctk.CTkLabel(
            self,
            text=text,
            font=FONTS["small"],
            text_color=color,
        ).pack(padx=10, pady=4)


class SidebarButton(ctk.CTkButton):
    """Navigation button for sidebar."""

    def __init__(self, master, text: str, icon: str, command: Callable, **kwargs) -> None:
        super().__init__(
            master,
            text=f"  {icon}  {text}",
            command=command,
            anchor="w",
            height=44,
            corner_radius=10,
            fg_color="transparent",
            text_color=COLORS["text_muted"],
            hover_color=COLORS["bg_elevated"],
            font=FONTS["body_bold"],
            **kwargs,
        )
        self._active = False

  

