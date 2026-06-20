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
  def set_active(self, active: bool) -> None:
        self._active = active
        if active:
            self.configure(
                fg_color=COLORS["primary"],
                text_color="#ffffff",
                hover_color=COLORS["primary_hover"],
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=COLORS["text_muted"],
                hover_color=COLORS["bg_elevated"],
            )


class MemoryMapCanvas(tk.Canvas):
    """Interactive memory block visualization."""

    BLOCK_COLORS = [
        "#6366f1", "#8b5cf6", "#06b6d4", "#10b981",
        "#f59e0b", "#ec4899", "#14b8a6", "#a855f7",
    ]

    def __init__(self, master, height: int = 120, **kwargs) -> None:
        super().__init__(
            master,
            height=height,
            bg=COLORS["bg_input"],
            highlightthickness=0,
            **kwargs,
        )
        self._result: Optional[SimulationResult] = None
        self.bind("<Configure>", self._on_resize)

    def show_result(self, result: SimulationResult) -> None:
        self._result = result
        self._draw()

    def clear(self) -> None:
        self._result = None
        self.delete("all")
        self._draw_empty()

    def _on_resize(self, _event=None) -> None:
        if self._result:
            self._draw()
        else:
            self._draw_empty()

    def _draw_empty(self) -> None:
        self.delete("all")
        w = max(self.winfo_width(), 200)
        h = max(self.winfo_height(), 80)
        self.create_text(
            w // 2, h // 2,
            text="نقشه حافظه پس از اجرای شبیه‌سازی نمایش داده می‌شود",
            fill=COLORS["text_dim"],
            font=("Segoe UI", 11),
        )

    def _draw(self) -> None:
        if not self._result:
            return

        self.delete("all")
        w = max(self.winfo_width(), 200)
        h = max(self.winfo_height(), 80)
        total = self._result.total_memory or 1
        margin = 16
        bar_h = 48
        y = (h - bar_h) // 2
        x = margin
        usable_w = w - 2 * margin

        for i, block in enumerate(self._result.block_states):
            block_w = max((block.size / total) * usable_w, 28)
            color = self.BLOCK_COLORS[i % len(self.BLOCK_COLORS)] if block.is_used else COLORS["block_free"]
            outline = COLORS["border"] if not block.is_used else color

            self.create_rectangle(
                x, y, x + block_w, y + bar_h,
                fill=color if block.is_used else COLORS["block_free"],
                outline=outline,
                width=2,
            )

            label = f"B{block.block_id}"
            if block.is_used:
                record = next(
                    (r for r in self._result.records if r.block_id == block.block_id),
                    None,
                )
                proc_size = record.process_size if record else "?"
                label = f"B{block.block_id} | P{block.process_id}\n{proc_size}/{block.size} KB"
                frag = block.size - (record.process_size if record else 0)
                if frag > 0 and block_w > 50:
                    frag_w = (frag / block.size) * block_w
                    self.create_rectangle(
                        x + block_w - frag_w, y + bar_h - 8,
                        x + block_w, y + bar_h,
                        fill=COLORS["block_frag"],
                        outline="",
                    )
            else:
                label = f"B{block.block_id}\n{block.size} KB FREE"

            self.create_text(
                x + block_w / 2, y + bar_h / 2,
                text=label,
                fill="#ffffff" if block.is_used else COLORS["text_muted"],
                font=("Segoe UI", 9, "bold"),
                justify="center",
            )
            x += block_w + 4

        legend_y = h - 14
        self.create_rectangle(margin, legend_y - 8, margin + 12, legend_y, fill=COLORS["block_used"], outline="")
        self.create_text(margin + 60, legend_y - 4, text="تخصیص‌یافته", fill=COLORS["text_muted"], anchor="w", font=("Segoe UI", 9))
        self.create_rectangle(margin + 130, legend_y - 8, margin + 142, legend_y, fill=COLORS["block_free"], outline=COLORS["border"])
        self.create_text(margin + 190, legend_y - 4, text="آزاد", fill=COLORS["text_muted"], anchor="w", font=("Segoe UI", 9))
        self.create_rectangle(margin + 230, legend_y - 8, margin + 242, legend_y, fill=COLORS["block_frag"], outline="")
        self.create_text(margin + 290, legend_y - 4, text="Fragmentation", fill=COLORS["text_muted"], anchor="w", font=("Segoe UI", 9))


  

