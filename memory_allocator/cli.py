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

def run_simulation(
    blocks: List[int],
    processes: List[int],
    *,
    auto_save_report: Optional[str] = None,
    auto_save_chart: Optional[str] = None,
    show_chart: bool = False,
    show_memory_maps: bool = False,
    interactive: bool = True,
) -> List:
    simulator = MemoryAllocationSimulator(blocks, processes)
    results = simulator.run_all()

    print("\n" + "=" * 80)
    print("ورودی شبیه‌سازی")
    print("=" * 80)
    print(f"Memory Blocks : {blocks}")
    print(f"Processes     : {processes}")
    print(f"Total Memory  : {sum(blocks)} KB")

    for result in results:
        print_result(result)

    print_comparison(results)

    report_text = build_report(blocks, processes, results)

    report_path = auto_save_report
    if interactive and report_path is None:
        choice = input("\nگزارش در فایل ذخیره شود؟ (y/n): ").strip().lower()
        if choice == "y":
            filename = input("نام فایل را وارد کن (پیش‌فرض: memory_allocation_report.txt): ").strip()
            report_path = filename or "memory_allocation_report.txt"

    if report_path:
        saved = save_report_to_file(report_text, report_path)
        print(f"\nگزارش با موفقیت ذخیره شد:\n{saved}")

    chart_path = auto_save_chart
    show = show_chart

    if interactive and chart_path is None and not show:
        choice = input("\nنمودار مقایسه نمایش داده شود؟ (y/n): ").strip().lower()
        if choice == "y":
            show = True
            save_choice = input("نمودار در فایل هم ذخیره شود؟ (y/n): ").strip().lower()
            if save_choice == "y":
                chart_path = "output/comparison_chart.png"

    if show or chart_path:
        saved_chart = render_comparison_chart(results, save_path=chart_path, show=show)
        if saved_chart:
            print(f"نمودار مقایسه ذخیره شد:\n{saved_chart}")

    if show_memory_maps or (interactive and _ask_yes_no("\nنقشه حافظه هر الگوریتم نمایش داده شود؟ (y/n): ")):
        output_dir = Path("output/memory_maps")
        for result in results:
            map_path = output_dir / f"{result.strategy_name.lower().replace(' ', '_')}_map.png"
            saved_map = render_memory_map_chart(
                result,
                save_path=str(map_path),
                show=show_chart or interactive,
            )
            if saved_map:
                print(f"نقشه حافظه {result.strategy_name}: {saved_map}")

    return results


def _ask_yes_no(prompt: str) -> bool:
    return input(prompt).strip().lower() == "y"


def show_menu() -> str:
    print("\n" + "=" * 80)
    print("Memory Allocation Simulation")
    print("شبیه‌سازی الگوریتم‌های تخصیص حافظه")
    print("=" * 80)
    print("1) ورود دستی داده‌ها")
    print("2) اجرای نمونه آماده")
    print("3) بارگذاری از فایل JSON")
    print("4) رابط گرافیکی (GUI)")
    print("5) خروج")
    return input("انتخاب کن: ").strip()


def _choose_sample() -> tuple[List[int], List[int]]:
    names = list_sample_names()
    print("\nنمونه‌های آماده:")
    for i, name in enumerate(names, start=1):
        info = SAMPLE_DATASETS[name]
        print(f"  {i}) {name} - {info['description']}")

    while True:
        choice = input("شماره نمونه را انتخاب کن: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            key = names[int(choice) - 1]
            data = SAMPLE_DATASETS[key]
            print(f"\nنمونه '{key}' انتخاب شد.")
            print(f"Blocks    = {data['blocks']}")
            print(f"Processes = {data['processes']}")
            return data["blocks"], data["processes"]
        print("گزینه نامعتبر است.")


def interactive_main() -> None:
    while True:
        choice = show_menu()

        if choice == "1":
            print("\nاعداد را با فاصله وارد کن. مثال:")
            print("100 500 200 300 600")
            blocks = read_int_list("اندازه بلوک‌ها (KB): ")
            processes = read_int_list("اندازه پردازه‌ها (KB): ")
            try:
                run_simulation(blocks, processes)
            except ValueError as exc:
                print(f"\nخطا: {exc}")

        elif choice == "2":
            try:
                blocks, processes = _choose_sample()
                run_simulation(blocks, processes)
            except ValueError as exc:
                print(f"\nخطا: {exc}")

        elif choice == "3":
            path = input("مسیر فایل JSON: ").strip()
            try:
                blocks, processes = load_from_json(path)
                print(f"Blocks    = {blocks}")
                print(f"Processes = {processes}")
                run_simulation(blocks, processes)
            except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
                print(f"\nخطا: {exc}")

        elif choice == "4":
            from memory_allocator.gui import launch_gui
            launch_gui()
            break

        elif choice == "5":
            print("خروج از برنامه.")
            break

        else:
            print("گزینه نامعتبر است. دوباره تلاش کن.")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="شبیه‌سازی الگوریتم‌های First Fit, Best Fit, Worst Fit",
    )
    parser.add_argument(
        "--blocks",
        type=str,
        help="اندازه بلوک‌های حافظه (با فاصله یا کاما جدا شده)",
    )
    parser.add_argument(
        "--processes",
        type=str,
        help="اندازه پردازه‌ها (با فاصله یا کاما جدا شده)",
    )
    parser.add_argument(
        "--sample",
        choices=list_sample_names(),
        help="اجرای یک نمونه آماده",
    )
    parser.add_argument(
        "--json",
        type=str,
        help="بارگذاری ورودی از فایل JSON",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="مسیر ذخیره گزارش متنی",
    )
    parser.add_argument(
        "--chart",
        type=str,
        default=None,
        help="مسیر ذخیره نمودار مقایسه (PNG)",
    )
    parser.add_argument(
        "--show-chart",
        action="store_true",
        help="نمایش نمودار مقایسه",
    )
    parser.add_argument(
        "--memory-maps",
        action="store_true",
        help="ذخیره نقشه حافظه برای هر الگوریتم",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="اجرای غیرتعاملی (بدون prompt)",
    )
    parser.add_argument(
        "--gui", "-g",
        action="store_true",
        help="اجرای رابط گرافیکی (GUI)",
    )
    return parser


def cli_main(argv: Optional[List[str]] = None) -> int:
    configure_console_encoding()
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.gui:
        from memory_allocator.gui import launch_gui
        launch_gui()
        return 0

    has_cli_input = args.blocks or args.processes or args.sample or args.json

    if not has_cli_input:
        try:
            interactive_main()
        except KeyboardInterrupt:
            print("\nبرنامه متوقف شد.")
            return 0
        return 0

    try:
        if args.json:
            blocks, processes = load_from_json(args.json)
        elif args.sample:
            data = SAMPLE_DATASETS[args.sample]
            blocks, processes = data["blocks"], data["processes"]
        else:
            if not args.blocks or not args.processes:
                parser.error("هر دو --blocks و --processes لازم هستند.")
            blocks = parse_int_list(args.blocks)
            processes = parse_int_list(args.processes)

        run_simulation(
            blocks,
            processes,
            auto_save_report=args.report or "memory_allocation_report.txt",
            auto_save_chart=args.chart or "output/comparison_chart.png",
            show_chart=args.show_chart,
            show_memory_maps=args.memory_maps,
            interactive=not args.no_interactive,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"خطا: {exc}", file=sys.stderr)
        return 1

    return 0


