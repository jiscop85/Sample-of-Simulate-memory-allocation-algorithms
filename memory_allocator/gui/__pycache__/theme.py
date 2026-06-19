"""Visual design tokens for the GUI."""

from __future__ import annotations

# Palette — modern dark OS-inspired theme
COLORS = {
    "bg_dark": "#0b0f14",
    "bg_card": "#121820",
    "bg_elevated": "#1a2230",
    "bg_input": "#0f1520",
    "border": "#2a3548",
    "border_focus": "#6366f1",
    "primary": "#6366f1",
    "primary_hover": "#818cf8",
    "secondary": "#8b5cf6",
    "success": "#10b981",
    "success_bg": "#064e3b",
    "warning": "#f59e0b",
    "warning_bg": "#78350f",
    "danger": "#ef4444",
    "danger_bg": "#7f1d1d",
    "info": "#38bdf8",
    "text": "#f1f5f9",
    "text_muted": "#94a3b8",
    "text_dim": "#64748b",
    "first_fit": "#3b82f6",
    "best_fit": "#10b981",
    "worst_fit": "#f43f5e",
    "block_free": "#1e293b",
    "block_used": "#4f46e5",
    "block_frag": "#f59e0b",
    "gradient_start": "#6366f1",
    "gradient_end": "#8b5cf6",
}

STRATEGY_COLORS = {
    "First Fit": COLORS["first_fit"],
    "Best Fit": COLORS["best_fit"],
    "Worst Fit": COLORS["worst_fit"],
}

FONTS = {
    "title": ("Segoe UI", 22, "bold"),
    "heading": ("Segoe UI", 16, "bold"),
    "subheading": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 12),
    "body_bold": ("Segoe UI", 12, "bold"),
    "small": ("Segoe UI", 11),
    "mono": ("Consolas", 11),
    "stat_value": ("Segoe UI", 26, "bold"),
    "stat_label": ("Segoe UI", 11),
}

APP_CONFIG = {
    "title": "Memory Allocation Simulator",
    "subtitle": "شبیه‌سازی تخصیص حافظه — First Fit · Best Fit · Worst Fit",
    "min_width": 1180,
    "min_height": 720,
    "corner_radius": 14,
    "card_radius": 12,
    "button_height": 42,
    "sidebar_width": 220,
}
