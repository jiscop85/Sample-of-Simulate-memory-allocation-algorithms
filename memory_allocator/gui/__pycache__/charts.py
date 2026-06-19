"""Matplotlib charts embedded in CustomTkinter."""

from __future__ import annotations

from typing import List, Optional

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from memory_allocator.models import SimulationResult
from memory_allocator.gui.theme import COLORS, STRATEGY_COLORS


def _style_figure(fig: Figure) -> None:
    fig.patch.set_facecolor(COLORS["bg_input"])
    for ax in fig.get_axes():
        ax.set_facecolor(COLORS["bg_card"])
        ax.tick_params(colors=COLORS["text_muted"], labelsize=9)
        ax.xaxis.label.set_color(COLORS["text_muted"])
        ax.yaxis.label.set_color(COLORS["text_muted"])
        ax.title.set_color(COLORS["text"])
        for spine in ax.spines.values():
            spine.set_color(COLORS["border"])


class ComparisonChartPanel(ctk.CTkFrame):
    """Side-by-side comparison bar chart."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color=COLORS["bg_card"], corner_radius=12, **kwargs)
        self._fig = Figure(figsize=(8, 3.5), dpi=100)
        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        self._placeholder()

    def _placeholder(self) -> None:
        self._fig.clear()
        ax = self._fig.add_subplot(111)
        _style_figure(self._fig)
        ax.text(
            0.5, 0.5,
            "نمودار مقایسه پس از اجرای شبیه‌سازی",
            ha="center", va="center",
            color=COLORS["text_dim"],
            fontsize=12,
            transform=ax.transAxes,
        )
        ax.set_xticks([])
        ax.set_yticks([])
        self._canvas.draw()

    def update_results(self, results: List[SimulationResult]) -> None:
        self._fig.clear()
        ax1 = self._fig.add_subplot(121)
        ax2 = self._fig.add_subplot(122)
        _style_figure(self._fig)

        names = [r.strategy_name for r in results]
        colors = [STRATEGY_COLORS.get(n, COLORS["primary"]) for n in names]
        x = range(len(names))

        used = [r.used_memory for r in results]
        frag = [r.internal_fragmentation for r in results]
        width = 0.35

        ax1.bar([i - width / 2 for i in x], used, width, label="Used", color=COLORS["success"], alpha=0.9)
        ax1.bar([i + width / 2 for i in x], frag, width, label="Frag.", color=COLORS["warning"], alpha=0.9)
        ax1.set_xticks(list(x))
        ax1.set_xticklabels([n.replace(" ", "\n") for n in names], fontsize=9)
        ax1.set_ylabel("KB", color=COLORS["text_muted"])
        ax1.set_title("Used vs Fragmentation", fontsize=11, pad=10)
        ax1.legend(facecolor=COLORS["bg_elevated"], edgecolor=COLORS["border"], labelcolor=COLORS["text"])

        util = [r.memory_utilization for r in results]
        bars = ax2.bar(names, util, color=colors, alpha=0.9)
        ax2.set_ylabel("%", color=COLORS["text_muted"])
        ax2.set_title("Memory Utilization", fontsize=11, pad=10)
        ax2.set_ylim(0, max(max(util) * 1.15, 15))
        for bar, val in zip(bars, util):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{val:.1f}%",
                ha="center", va="bottom",
                color=COLORS["text"],
                fontsize=9,
            )

        self._fig.tight_layout(pad=2.0)
        self._canvas.draw()

    def save_png(self, path: str) -> None:
        self._fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=COLORS["bg_dark"])

