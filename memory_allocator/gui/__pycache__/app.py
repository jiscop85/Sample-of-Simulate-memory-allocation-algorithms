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

    def _build_compare_card(self, parent, strategy: str) -> ctk.CTkFrame:
        color = STRATEGY_COLORS[strategy]
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["bg_card"], corner_radius=12,
            border_width=2, border_color=COLORS["border"],
        )
        ctk.CTkLabel(card, text=strategy, font=FONTS["subheading"], text_color=color).pack(pady=(16, 8))
        metrics = ctk.CTkFrame(card, fg_color="transparent")
        metrics.pack(fill="x", padx=16, pady=(0, 16))
        card._metric_labels = {}
        for key, label in [
            ("alloc", "تخصیص موفق"),
            ("frag", "Fragmentation"),
            ("util", "Utilization"),
            ("eff", "Efficiency"),
        ]:
            row = ctk.CTkFrame(metrics, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label, font=FONTS["small"], text_color=COLORS["text_muted"]).pack(side="left")
            lbl = ctk.CTkLabel(row, text="—", font=FONTS["body_bold"], text_color=COLORS["text"])
            lbl.pack(side="right")
            card._metric_labels[key] = lbl
        return card

    def _build_export_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self._content, fg_color="transparent")

        hero = ctk.CTkFrame(page, fg_color=COLORS["bg_card"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        hero.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(hero, text="💾  ذخیره و خروجی", font=FONTS["title"], text_color=COLORS["text"]).pack(anchor="w", padx=24, pady=(24, 8))
        ctk.CTkLabel(
            hero,
            text="گزارش متنی، نمودار مقایسه و نقشه حافظه را ذخیره کنید",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=24, pady=(0, 20))

        grid = ctk.CTkFrame(page, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1), weight=1)

        exports = [
            ("📄  گزارش متنی (TXT)", "ذخیره گزارش کامل شامل جداول و تحلیل", self._export_report, COLORS["primary"]),
            ("📊  نمودار مقایسه (PNG)", "نمودار bar chart مقایسه سه الگوریتم", self._export_chart, COLORS["secondary"]),
            ("🗺  نقشه‌های حافظه (PNG)", "ذخیره نقشه هر الگوریتم در پوشه output", self._export_maps, COLORS["info"]),
            ("📋  کپی خلاصه", "کپی نتایج مقایسه به کلیپبورد", self._copy_summary, COLORS["success"]),
        ]

        for i, (title, desc, cmd, accent) in enumerate(exports):
            card = ctk.CTkFrame(
                grid, fg_color=COLORS["bg_card"], corner_radius=14,
                border_width=1, border_color=COLORS["border"],
            )
            card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=8, pady=8)

            accent_bar = ctk.CTkFrame(card, fg_color=accent, height=4, corner_radius=2)
            accent_bar.pack(fill="x", padx=16, pady=(16, 0))

            ctk.CTkLabel(card, text=title, font=FONTS["subheading"], text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(12, 4))
            ctk.CTkLabel(card, text=desc, font=FONTS["small"], text_color=COLORS["text_muted"]).pack(anchor="w", padx=20, pady=(0, 16))

            ctk.CTkButton(
                card, text="اجرا", height=40, corner_radius=10,
                fg_color=accent, hover_color=COLORS["primary_hover"],
                command=cmd,
            ).pack(anchor="w", padx=20, pady=(0, 20))

        return page

    # ── Navigation ──────────────────────────────────────────────────────

    def _show_page(self, page_key: str) -> None:
        self._current_page = page_key
        titles = {
            "input": "ورودی شبیه‌سازی",
            "results": "نتایج الگوریتم‌ها",
            "compare": "مقایسه و تحلیل",
            "export": "ذخیره خروجی",
        }
        self._header_title.configure(text=titles.get(page_key, ""))

        for key, btn in self._nav_buttons.items():
            btn.set_active(key == page_key)

        for key, frame in self._pages.items():
            if key == page_key:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()

    def _set_status(self, text: str, level: str = "ready") -> None:
        styles = {
            "ready": (COLORS["success"], COLORS["success_bg"], "● آماده"),
            "running": (COLORS["warning"], COLORS["warning_bg"], "◌ در حال اجرا..."),
            "done": (COLORS["success"], COLORS["success_bg"], "✓ انجام شد"),
            "error": (COLORS["danger"], COLORS["danger_bg"], "✕ خطا"),
        }
        color, bg, default = styles.get(level, styles["ready"])
        self._status_badge.configure(text=text or default, text_color=color, fg_color=bg)

    def _toast(self, message: str, level: str = "info") -> None:
        Toast(self, message, level=level)

    # ── Input helpers ───────────────────────────────────────────────────

    def _get_input_text(self, widget: ctk.CTkTextbox) -> str:
        return widget.get("1.0", "end").strip()

    def _set_input_text(self, widget: ctk.CTkTextbox, text: str) -> None:
        widget.delete("1.0", "end")
        widget.insert("1.0", text)

    def _refresh_chips(self) -> None:
        try:
            blocks = parse_int_list(self._get_input_text(self._blocks_entry))
            processes = parse_int_list(self._get_input_text(self._processes_entry))
        except ValueError:
            blocks, processes = [], []

        self._update_chip_row(self._blocks_chips, blocks, COLORS["primary"])
        self._update_chip_row(self._processes_chips, processes, COLORS["secondary"])
        self._update_summary(blocks, processes)

    def _update_chip_row(self, container: ctk.CTkFrame, values: List[int], color: str) -> None:
        for child in container.winfo_children():
            child.destroy()
        for v in values:
            TagChip(container, text=str(v), color=color).pack(side="left", padx=3, pady=4)

    def _update_summary(self, blocks: List[int], processes: List[int]) -> None:
        self._summary_labels["blocks"].configure(text=str(len(blocks)))
        self._summary_labels["processes"].configure(text=str(len(processes)))
        self._summary_labels["total_mem"].configure(text=f"{sum(blocks)} KB" if blocks else "—")
        self._summary_labels["total_proc"].configure(text=f"{sum(processes)} KB" if processes else "—")

    def _load_sample(self, key: str, silent: bool = False) -> None:
        data = SAMPLE_DATASETS.get(key)
        if not data:
            return
        self._sample_var.set(key)
        self._set_input_text(self._blocks_entry, " ".join(str(b) for b in data["blocks"]))
        self._set_input_text(self._processes_entry, " ".join(str(p) for p in data["processes"]))
        self._refresh_chips()
        if not silent:
            self._toast(f"نمونه «{key}» بارگذاری شد", "success")

    def _load_json(self) -> None:
        path = filedialog.askopenfilename(
            title="انتخاب فایل JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(Path(__file__).resolve().parents[2] / "samples"),
        )
        if not path:
            return
        try:
            from memory_allocator.utils import load_from_json
            blocks, processes = load_from_json(path)
            self._set_input_text(self._blocks_entry, " ".join(str(b) for b in blocks))
            self._set_input_text(self._processes_entry, " ".join(str(p) for p in processes))
            self._refresh_chips()
            self._toast("فایل JSON بارگذاری شد", "success")
        except Exception as exc:
            self._toast(str(exc), "error")

    def _clear_input(self) -> None:
        self._blocks_entry.delete("1.0", "end")
        self._processes_entry.delete("1.0", "end")
        self._refresh_chips()
        self._toast("ورودی پاک شد", "info")

    def _parse_input(self) -> tuple[List[int], List[int]]:
        blocks = parse_int_list(self._get_input_text(self._blocks_entry))
        processes = parse_int_list(self._get_input_text(self._processes_entry))
        if not blocks:
            raise ValueError("لیست بلوک‌های حافظه نباید خالی باشد.")
        if not processes:
            raise ValueError("لیست پردازه‌ها نباید خالی باشد.")
        return blocks, processes

    # ── Simulation ──────────────────────────────────────────────────────

    def _run_simulation(self) -> None:
        try:
            blocks, processes = self._parse_input()
        except ValueError as exc:
            self._toast(str(exc), "error")
            self._set_status("", "error")
            return

        self._set_status("", "running")
        self._show_progress(True)

        def worker() -> None:
            try:
                sim = MemoryAllocationSimulator(blocks, processes)
                results = sim.run_all()
                self.after(0, lambda: self._on_simulation_done(blocks, processes, results, None))
            except Exception as exc:
                self.after(0, lambda: self._on_simulation_done([], [], [], exc))

        threading.Thread(target=worker, daemon=True).start()

    def _show_progress(self, visible: bool) -> None:
        if visible:
            if not hasattr(self, "_progress"):
                self._progress = ctk.CTkProgressBar(
                    self._header, mode="indeterminate",
                    progress_color=COLORS["primary"],
                    width=120,
                )
            self._progress.pack(side="right", padx=(0, 12))
            self._progress.start()
        elif hasattr(self, "_progress"):
            self._progress.stop()
            self._progress.pack_forget()

    def _on_simulation_done(
        self,
        blocks: List[int],
        processes: List[int],
        results: List[SimulationResult],
        error: Optional[Exception],
    ) -> None:
        self._show_progress(False)

        if error:
            self._set_status("", "error")
            self._toast(str(error), "error")
            return

        self._blocks = blocks
        self._processes = processes
        self._results = results

        self._update_results_ui()
        self._update_compare_ui()
        self._set_status("", "done")
        self._toast("شبیه‌سازی با موفقیت انجام شد!", "success")
        self._show_page("results")

    def _update_results_ui(self) -> None:
        for result in self._results:
            strategy = result.strategy_name
            cards = self._stat_cards.get(strategy, [])
            if len(cards) >= 4:
                cards[0].set_value(f"{result.used_memory} KB")
                cards[1].set_value(f"{result.internal_fragmentation} KB")
                cards[2].set_value(f"{result.free_memory} KB")
                cards[3].set_value(f"{result.memory_utilization:.1f}%")

            if strategy in self._memory_maps:
                self._memory_maps[strategy].show_result(result)
            if strategy in self._allocation_tables:
                self._allocation_tables[strategy].update_records(result)
            if strategy in self._detail_charts:
                self._detail_charts[strategy].update_result(result)

    def _update_compare_ui(self) -> None:
        if not self._results:
            return

        best_frag = min(self._results, key=lambda x: (x.internal_fragmentation, -x.allocated_processes))
        best_util = max(self._results, key=lambda x: x.memory_utilization)
        most_alloc = max(self._results, key=lambda x: (x.allocated_processes, -x.internal_fragmentation))

        winner = best_util if best_util.allocated_processes >= most_alloc.allocated_processes else most_alloc
        self._winner_label.configure(
            text=(
                f"🏆  بهترین الگوریتم: {winner.strategy_name}  |  "
                f"Utilization: {winner.memory_utilization:.1f}%  |  "
                f"Frag: {winner.internal_fragmentation} KB  |  "
                f"تخصیص: {winner.allocated_processes}/{len(winner.records)}"
            )
        )

        for result in self._results:
            card = self._compare_cards.get(result.strategy_name)
            if not card:
                continue
            labels = card._metric_labels
            labels["alloc"].configure(
                text=f"{result.allocated_processes}/{len(result.records)}",
                text_color=COLORS["success"] if not result.unallocated_processes else COLORS["warning"],
            )
            labels["frag"].configure(text=f"{result.internal_fragmentation} KB")
            labels["util"].configure(text=f"{result.memory_utilization:.1f}%")
            labels["eff"].configure(text=f"{result.allocation_efficiency:.1f}%")

            is_best = result.strategy_name == winner.strategy_name
            card.configure(border_color=COLORS["success"] if is_best else COLORS["border"])

        self._comparison_chart.update_results(self._results)


    # ── Export ──────────────────────────────────────────────────────────

    def _ensure_results(self) -> bool:
        if not self._results:
            self._toast("ابتدا شبیه‌سازی را اجرا کنید", "warning")
            return False
        return True

    def _export_report(self) -> None:
        if not self._ensure_results():
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="memory_allocation_report.txt",
            initialdir=str(Path.cwd() / "output"),
        )
        if not path:
            return
        report = build_report(self._blocks, self._processes, self._results)
        saved = save_report_to_file(report, path)
        self._toast(f"گزارش ذخیره شد", "success")

    def _export_chart(self) -> None:
        if not self._ensure_results():
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG images", "*.png")],
            initialfile="comparison_chart.png",
            initialdir=str(Path.cwd() / "output"),
        )
        if not path:
            return
        self._comparison_chart.save_png(path)
        self._toast("نمودار ذخیره شد", "success")

    def _export_maps(self) -> None:
        if not self._ensure_results():
            return
        folder = filedialog.askdirectory(
            title="انتخاب پوشه ذخیره",
            initialdir=str(Path.cwd() / "output" / "memory_maps"),
        )
        if not folder:
            return
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            import matplotlib.patches as mpatches

            out = Path(folder)
            out.mkdir(parents=True, exist_ok=True)

            for result in self._results:
                fig = Figure(figsize=(10, 2.5), dpi=120)
                fig.patch.set_facecolor(COLORS["bg_dark"])
                ax = fig.add_subplot(111)
                ax.set_facecolor(COLORS["bg_card"])
                ax.set_xlim(0, result.total_memory)
                ax.set_ylim(0, 1)
                ax.axis("off")
                ax.set_title(f"Memory Map — {result.strategy_name}", color=COLORS["text"], fontsize=12)

                x = 0
                colors_list = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b"]
                for i, block in enumerate(result.block_states):
                    color = colors_list[i % len(colors_list)] if block.is_used else COLORS["block_free"]
                    rect = mpatches.FancyBboxPatch(
                        (x, 0.25), block.size, 0.5,
                        boxstyle="round,pad=0.01,rounding_size=1",
                        facecolor=color, edgecolor=COLORS["border"],
                    )
                    ax.add_patch(rect)
                    label = f"B{block.block_id}"
                    if block.is_used:
                        label += f"\nP{block.process_id}"
                    ax.text(x + block.size / 2, 0.5, label, ha="center", va="center", color="#fff", fontsize=8)
                    x += block.size

                canvas = FigureCanvasAgg(fig)
                fname = out / f"{result.strategy_name.lower().replace(' ', '_')}_map.png"
                canvas.print_png(str(fname))

            self._toast(f"نقشه‌ها در {folder} ذخیره شدند", "success")
        except Exception as exc:
            self._toast(str(exc), "error")

    def _copy_summary(self) -> None:
        if not self._ensure_results():
            return
        lines = ["مقایسه الگوریتم‌های تخصیص حافظه", ""]
        for r in self._results:
            lines.append(
                f"{r.strategy_name}: Alloc={r.allocated_processes}/{len(r.records)}, "
                f"Used={r.used_memory}KB, Frag={r.internal_fragmentation}KB, "
                f"Util={r.memory_utilization:.1f}%"
            )
        text = "\n".join(lines)
        self.clipboard_clear()
        self.clipboard_append(text)
        self._toast("خلاصه در کلیپبورد کپی شد", "success")


def launch_gui() -> None:
    """Start the GUI application."""
    app = MemoryAllocatorApp()
    app.mainloop()
