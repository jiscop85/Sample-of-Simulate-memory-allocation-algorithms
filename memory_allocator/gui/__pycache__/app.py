"""Premium GUI for Memory Allocation Simulation."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Dict, List, Optional

import customtkinter as ctk

from memory_allocator.gui.charts import ComparisonChartPanel, StrategyDetailChart
from memory_allocator.gui.theme import APP_CONFIG, COLORS, FONTS, STRATEGY_COLORS
from memory_allocator.gui.widgets import (
    AllocationTable,
    MemoryMapCanvas,
    SidebarButton,
    StatCard,
    TagChip,
    Toast,
)
from memory_allocator.models import SimulationResult
from memory_allocator.report import build_report, save_report_to_file
from memory_allocator.simulator import MemoryAllocationSimulator
from memory_allocator.utils import SAMPLE_DATASETS, parse_int_list


class MemoryAllocatorApp(ctk.CTk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(APP_CONFIG["title"])
        self.geometry("1320x820")
        self.minsize(APP_CONFIG["min_width"], APP_CONFIG["min_height"])
        self.configure(fg_color=COLORS["bg_dark"])

        self._results: List[SimulationResult] = []
        self._blocks: List[int] = []
        self._processes: List[int] = []
        self._current_page = "input"
        self._nav_buttons: Dict[str, SidebarButton] = {}
        self._strategy_tabs: Dict[str, ctk.CTkFrame] = {}
        self._stat_cards: Dict[str, List[StatCard]] = {}
        self._memory_maps: Dict[str, MemoryMapCanvas] = {}
        self._detail_charts: Dict[str, StrategyDetailChart] = {}
        self._allocation_tables: Dict[str, AllocationTable] = {}

        self._build_layout()
        self._show_page("input")
        self._load_sample("classic", silent=True)

        self.bind("<Control-Return>", lambda _e: self._run_simulation())
        self.bind("<Control-s>", lambda _e: self._export_report())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # ── Layout ──────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(
            self,
            width=APP_CONFIG["sidebar_width"],
            fg_color=COLORS["bg_card"],
            corner_radius=0,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=16, pady=(24, 20))

        logo = ctk.CTkFrame(brand, width=44, height=44, fg_color=COLORS["primary"], corner_radius=12)
        logo.pack(side="left")
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="🧠", font=("Segoe UI Emoji", 22)).place(relx=0.5, rely=0.5, anchor="center")

        title_frame = ctk.CTkFrame(brand, fg_color="transparent")
        title_frame.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(
            title_frame,
            text="MemSim",
            font=FONTS["heading"],
            text_color=COLORS["text"],
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_frame,
            text="OS Simulator",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(anchor="w")

        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12, pady=8)

        nav_items = [
            ("input", "ورودی", "📝"),
            ("results", "نتایج", "📊"),
            ("compare", "مقایسه", "⚖️"),
            ("export", "خروجی", "💾"),
        ]
        for key, label, icon in nav_items:
            btn = SidebarButton(nav_frame, text=label, icon=icon, command=lambda k=key: self._show_page(k))
            btn.pack(fill="x", pady=3)
            self._nav_buttons[key] = btn

        ctk.CTkFrame(sidebar, fg_color=COLORS["border"], height=1).pack(fill="x", padx=16, pady=16)

        run_btn = ctk.CTkButton(
            sidebar,
            text="▶  اجرای شبیه‌سازی",
            height=48,
            corner_radius=12,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=FONTS["body_bold"],
            command=self._run_simulation,
        )
        run_btn.pack(fill="x", padx=16, pady=(0, 12))

        hint = ctk.CTkLabel(
            sidebar,
            text="Ctrl + Enter",
            font=FONTS["small"],
            text_color=COLORS["text_dim"],
        )
        hint.pack(padx=16, anchor="w")

        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=16, pady=20)
        ctk.CTkLabel(
            footer,
            text="First · Best · Worst Fit",
            font=FONTS["small"],
            text_color=COLORS["text_dim"],
        ).pack(anchor="w")

    def _build_main_area(self) -> None:
        self._main = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        self._main.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self._main.grid_columnconfigure(0, weight=1)
        self._main.grid_rowconfigure(1, weight=1)

        self._header = ctk.CTkFrame(self._main, fg_color="transparent", height=70)
        self._header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 0))
        self._header_title = ctk.CTkLabel(
            self._header,
            text="ورودی شبیه‌سازی",
            font=FONTS["title"],
            text_color=COLORS["text"],
            anchor="w",
        )
        self._header_title.pack(side="left")

        self._header_sub = ctk.CTkLabel(
            self._header,
            text=APP_CONFIG["subtitle"],
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        self._header_sub.pack(side="left", padx=(16, 0))

        self._status_badge = ctk.CTkLabel(
            self._header,
            text="● آماده",
            font=FONTS["small"],
            text_color=COLORS["success"],
            fg_color=COLORS["success_bg"],
            corner_radius=20,
            padx=12,
            pady=4,
        )
        self._status_badge.pack(side="right")

        self._content = ctk.CTkFrame(self._main, fg_color="transparent")
        self._content.grid(row=1, column=0, sticky="nsew", padx=28, pady=(12, 24))
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        self._pages: Dict[str, ctk.CTkFrame] = {}
        self._pages["input"] = self._build_input_page()
        self._pages["results"] = self._build_results_page()
        self._pages["compare"] = self._build_compare_page()
        self._pages["export"] = self._build_export_page()

    # ── Pages ───────────────────────────────────────────────────────────

    def _build_input_page(self) -> ctk.CTkFrame:
        page = ctk.CTkScrollableFrame(self._content, fg_color="transparent")
        page.grid_columnconfigure((0, 1), weight=1)

        left = ctk.CTkFrame(page, fg_color=COLORS["bg_card"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="📦  بلوک‌های حافظه (KB)", font=FONTS["subheading"], text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 8))
        ctk.CTkLabel(left, text="اعداد را با فاصله یا کاما جدا کنید", font=FONTS["small"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=20)

        self._blocks_entry = ctk.CTkTextbox(
            left, height=90, font=FONTS["mono"],
            fg_color=COLORS["bg_input"], border_color=COLORS["border"], border_width=1,
            corner_radius=10,
        )
        self._blocks_entry.pack(fill="x", padx=20, pady=(8, 12))
        self._blocks_entry.bind("<KeyRelease>", lambda _e: self._refresh_chips())

        self._blocks_chips = ctk.CTkFrame(left, fg_color="transparent")
        self._blocks_chips.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkFrame(left, fg_color=COLORS["border"], height=1).pack(fill="x", padx=20)

        ctk.CTkLabel(left, text="⚙️  پردازه‌ها (KB)", font=FONTS["subheading"], text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(16, 8))
        self._processes_entry = ctk.CTkTextbox(
            left, height=90, font=FONTS["mono"],
            fg_color=COLORS["bg_input"], border_color=COLORS["border"], border_width=1,
            corner_radius=10,
        )
        self._processes_entry.pack(fill="x", padx=20, pady=(8, 12))
        self._processes_entry.bind("<KeyRelease>", lambda _e: self._refresh_chips())

        self._processes_chips = ctk.CTkFrame(left, fg_color="transparent")
        self._processes_chips.pack(fill="x", padx=20, pady=(0, 20))

        right = ctk.CTkFrame(page, fg_color=COLORS["bg_card"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)

        ctk.CTkLabel(right, text="🎯  نمونه‌های آماده", font=FONTS["subheading"], text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(20, 12))

        self._sample_var = ctk.StringVar(value="classic")
        for key, data in SAMPLE_DATASETS.items():
            card = ctk.CTkFrame(right, fg_color=COLORS["bg_elevated"], corner_radius=10, border_width=1, border_color=COLORS["border"])
            card.pack(fill="x", padx=20, pady=4)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=10)

            rb = ctk.CTkRadioButton(
                row,
                text="",
                variable=self._sample_var,
                value=key,
                width=20,
                command=lambda k=key: self._load_sample(k),
            )
            rb.pack(side="left")

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=(4, 0))
            ctk.CTkLabel(info, text=key.upper(), font=FONTS["body_bold"], text_color=COLORS["text"], anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=data["description"], font=FONTS["small"], text_color=COLORS["text_muted"], anchor="w").pack(anchor="w")
            ctk.CTkLabel(
                info,
                text=f"B:{data['blocks']}  P:{data['processes']}",
                font=FONTS["mono"],
                text_color=COLORS["text_dim"],
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(right, fg_color=COLORS["border"], height=1).pack(fill="x", padx=20, pady=16)

        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(
            btn_row, text="📂  بارگذاری JSON", height=40, corner_radius=10,
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["border"],
            border_width=1, border_color=COLORS["border"],
            command=self._load_json,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="🗑  پاک کردن", height=40, corner_radius=10,
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["danger_bg"],
            border_width=1, border_color=COLORS["border"],
            command=self._clear_input,
        ).pack(side="left")

        summary = ctk.CTkFrame(page, fg_color=COLORS["bg_card"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        summary.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(16, 0))

        sum_inner = ctk.CTkFrame(summary, fg_color="transparent")
        sum_inner.pack(fill="x", padx=20, pady=16)

        self._summary_labels = {}
        for key, label, icon in [
            ("blocks", "تعداد بلوک‌ها", "📦"),
            ("processes", "تعداد پردازه‌ها", "⚙️"),
            ("total_mem", "کل حافظه", "💾"),
            ("total_proc", "کل اندازه پردازه‌ها", "📐"),
        ]:
            cell = ctk.CTkFrame(sum_inner, fg_color=COLORS["bg_elevated"], corner_radius=10)
            cell.pack(side="left", fill="x", expand=True, padx=6)
            ctk.CTkLabel(cell, text=f"{icon} {label}", font=FONTS["small"], text_color=COLORS["text_muted"]).pack(pady=(10, 0))
            lbl = ctk.CTkLabel(cell, text="—", font=FONTS["heading"], text_color=COLORS["primary"])
            lbl.pack(pady=(4, 12))
            self._summary_labels[key] = lbl

        return page

    def _build_results_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self._content, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        self._results_tabview = ctk.CTkTabview(
            page,
            fg_color=COLORS["bg_card"],
            segmented_button_fg_color=COLORS["bg_elevated"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_hover"],
            segmented_button_unselected_color=COLORS["bg_elevated"],
            segmented_button_unselected_hover_color=COLORS["border"],
            corner_radius=14,
        )
        self._results_tabview.grid(row=0, column=0, rowspan=2, sticky="nsew")

        for strategy in ("First Fit", "Best Fit", "Worst Fit"):
            tab = self._results_tabview.add(f"  {strategy}  ")
            tab.grid_columnconfigure(0, weight=1)
            self._strategy_tabs[strategy] = tab
            self._build_strategy_tab(tab, strategy)

        return page

    def _build_strategy_tab(self, tab: ctk.CTkFrame, strategy: str) -> None:
        color = STRATEGY_COLORS[strategy]

        cards_row = ctk.CTkFrame(tab, fg_color="transparent")
        cards_row.pack(fill="x", padx=12, pady=(12, 8))
        cards_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        card_defs = [
            ("used", "Used Memory", "💚", COLORS["success"]),
            ("frag", "Internal Frag.", "⚠️", COLORS["warning"]),
            ("free", "Free Memory", "🆓", COLORS["info"]),
            ("util", "Utilization", "📈", color),
        ]
        cards: List[StatCard] = []
        for i, (key, title, icon, accent) in enumerate(card_defs):
            card = StatCard(cards_row, title=title, icon=icon, accent=accent)
            card.grid(row=0, column=i, sticky="ew", padx=4)
            cards.append(card)
        self._stat_cards[strategy] = cards

        mid = ctk.CTkFrame(tab, fg_color="transparent")
        mid.pack(fill="both", expand=True, padx=12, pady=8)
        mid.grid_columnconfigure(0, weight=3)
        mid.grid_columnconfigure(1, weight=2)
        mid.grid_rowconfigure(0, weight=1)

        left_col = ctk.CTkFrame(mid, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        map_frame = ctk.CTkFrame(left_col, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        map_frame.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(map_frame, text="🗺  نقشه حافظه", font=FONTS["body_bold"], text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(12, 4))
        mem_map = MemoryMapCanvas(map_frame, height=110)
        mem_map.pack(fill="x", padx=12, pady=(0, 12))
        self._memory_maps[strategy] = mem_map

        table_frame = ctk.CTkFrame(left_col, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        table_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(table_frame, text="📋  جدول تخصیص", font=FONTS["body_bold"], text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(12, 4))
        table = AllocationTable(table_frame, height=200)
        table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._allocation_tables[strategy] = table

        right_col = ctk.CTkFrame(mid, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        chart_frame = ctk.CTkFrame(right_col, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        chart_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(chart_frame, text="📊  توزیع حافظه", font=FONTS["body_bold"], text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(12, 4))
        detail_chart = StrategyDetailChart(chart_frame)
        detail_chart.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self._detail_charts[strategy] = detail_chart

    def _build_compare_page(self) -> ctk.CTkFrame:
        page = ctk.CTkScrollableFrame(self._content, fg_color="transparent")

        self._winner_banner = ctk.CTkFrame(
            page, fg_color=COLORS["success_bg"], corner_radius=14,
            border_width=2, border_color=COLORS["success"],
        )
        self._winner_banner.pack(fill="x", pady=(0, 16))
        self._winner_label = ctk.CTkLabel(
            self._winner_banner,
            text="🏆  پس از اجرای شبیه‌سازی، بهترین الگوریتم اینجا نمایش داده می‌شود",
            font=FONTS["body_bold"],
            text_color=COLORS["success"],
        )
        self._winner_label.pack(padx=20, pady=16)

        self._compare_cards_row = ctk.CTkFrame(page, fg_color="transparent")
        self._compare_cards_row.pack(fill="x", pady=(0, 16))
        self._compare_cards: Dict[str, ctk.CTkFrame] = {}
        for strategy in ("First Fit", "Best Fit", "Worst Fit"):
            card = self._build_compare_card(self._compare_cards_row, strategy)
            card.pack(side="left", fill="both", expand=True, padx=6)
            self._compare_cards[strategy] = card

        chart_wrap = ctk.CTkFrame(page, fg_color=COLORS["bg_card"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        chart_wrap.pack(fill="both", expand=True)
        ctk.CTkLabel(chart_wrap, text="📊  نمودار مقایسه الگوریتم‌ها", font=FONTS["subheading"], text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 4))
        self._comparison_chart = ComparisonChartPanel(chart_wrap)
        self._comparison_chart.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        return page

 
