"""Text report generation and console output."""

from __future__ import annotations

from typing import List

from .models import SimulationResult


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    def make_row(row_vals: List[str]) -> str:
        return " | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row_vals))

    line = "-+-".join("-" * w for w in widths)
    output = [make_row(headers), line]
    for row in rows:
        output.append(make_row(row))
    return "\n".join(output)


def _allocation_rows(result: SimulationResult) -> List[List[str]]:
    rows: List[List[str]] = []
    for record in result.records:
        if not record.is_allocated:
            rows.append([
                f"P{record.process_id}",
                str(record.process_size),
                "Not Allocated",
                "-",
                "-",
            ])
        else:
            rows.append([
                f"P{record.process_id}",
                str(record.process_size),
                f"B{record.block_id}",
                str(record.block_size),
                str(record.internal_fragmentation),
            ])
    return rows


def _memory_map(result: SimulationResult) -> str:
    lines = ["Memory Map:"]
    for block in result.block_states:
        if block.is_used:
            lines.append(
                f"  B{block.block_id} [{block.size:>4} KB] -> P{block.process_id} (USED)"
            )
        else:
            lines.append(f"  B{block.block_id} [{block.size:>4} KB] -> FREE")
    return "\n".join(lines)


def print_result(result: SimulationResult) -> None:
    print("\n" + "=" * 80)
    print(f"نتایج الگوریتم: {result.strategy_name}")
    print("=" * 80)

    headers = ["Process", "Size", "Allocated Block", "Block Size", "Frag."]
    print(format_table(headers, _allocation_rows(result)))

    print(f"\n{_memory_map(result)}")

    print("\nخلاصه:")
    print(f"Used Memory            : {result.used_memory} KB")
    print(f"Allocated Memory       : {result.allocated_memory} KB")
    print(f"Internal Fragmentation : {result.internal_fragmentation} KB")
    print(f"Free Memory            : {result.free_memory} KB")
    print(f"Total Wasted Memory    : {result.total_wasted_memory} KB")
    print(f"Memory Utilization     : {result.memory_utilization:.2f}%")
    print(f"Allocation Efficiency  : {result.allocation_efficiency:.2f}%")
    print(f"Waste Ratio            : {result.waste_ratio:.2f}%")
    print(f"Allocated Processes    : {result.allocated_processes}/{len(result.records)}")

    if result.unallocated_processes:
        failed = ", ".join(f"P{p}" for p in result.unallocated_processes)
        print(f"Unallocated Processes  : {failed}")
    else:
        print("Unallocated Processes  : None")


def print_comparison(results: List[SimulationResult]) -> None:
    print("\n" + "=" * 80)
    print("مقایسه الگوریتم‌ها")
    print("=" * 80)

    headers = [
        "Strategy",
        "Allocated",
        "Used",
        "Frag.",
        "Free",
        "Utilization",
        "Efficiency",
    ]
    rows = [
        [
            r.strategy_name,
            str(r.allocated_processes),
            str(r.used_memory),
            str(r.internal_fragmentation),
            str(r.free_memory),
            f"{r.memory_utilization:.2f}%",
            f"{r.allocation_efficiency:.2f}%",
        ]
        for r in results
    ]
    print(format_table(headers, rows))

    best_by_frag = min(
        results,
        key=lambda x: (x.internal_fragmentation, -x.allocated_processes),
    )
    best_by_util = max(results, key=lambda x: x.memory_utilization)
    most_allocated = max(results, key=lambda x: (x.allocated_processes, -x.internal_fragmentation))

    print("\nتحلیل نهایی:")
    print(f"کمترین fragmentation در این نمونه     : {best_by_frag.strategy_name}")
    print(f"بیشترین استفاده از حافظه در این نمونه : {best_by_util.strategy_name}")
    print(f"بیشترین تعداد تخصیص موفق              : {most_allocated.strategy_name}")


def build_report(
    blocks: List[int],
    processes: List[int],
    results: List[SimulationResult],
) -> str:
    lines = [
        "MEMORY ALLOCATION SIMULATION REPORT",
        "=" * 80,
        "",
        f"Memory Blocks : {blocks}",
        f"Processes     : {processes}",
        f"Total Memory  : {sum(blocks)} KB",
        "",
    ]

    for result in results:
        lines.extend([
            "=" * 80,
            f"Strategy: {result.strategy_name}",
            "=" * 80,
            "",
            format_table(
                ["Process", "Size", "Allocated Block", "Block Size", "Frag."],
                _allocation_rows(result),
            ),
            "",
            _memory_map(result),
            "",
            "Summary:",
            f"Used Memory            : {result.used_memory} KB",
            f"Allocated Memory       : {result.allocated_memory} KB",
            f"Internal Fragmentation : {result.internal_fragmentation} KB",
            f"Free Memory            : {result.free_memory} KB",
            f"Total Wasted Memory    : {result.total_wasted_memory} KB",
            f"Memory Utilization     : {result.memory_utilization:.2f}%",
            f"Allocation Efficiency  : {result.allocation_efficiency:.2f}%",
            f"Waste Ratio            : {result.waste_ratio:.2f}%",
            f"Allocated Processes    : {result.allocated_processes}/{len(result.records)}",
        ])

        if result.unallocated_processes:
            lines.append(
                "Unallocated Processes  : "
                + ", ".join(f"P{p}" for p in result.unallocated_processes)
            )
        else:
            lines.append("Unallocated Processes  : None")
        lines.append("")

    lines.extend([
        "=" * 80,
        "Comparison",
        "=" * 80,
        format_table(
            [
                "Strategy",
                "Allocated",
                "Used",
                "Frag.",
                "Free",
                "Utilization",
                "Efficiency",
            ],
            [
                [
                    r.strategy_name,
                    str(r.allocated_processes),
                    str(r.used_memory),
                    str(r.internal_fragmentation),
                    str(r.free_memory),
                    f"{r.memory_utilization:.2f}%",
                    f"{r.allocation_efficiency:.2f}%",
                ]
                for r in results
            ],
        ),
        "",
    ])

    best_frag = min(results, key=lambda x: (x.internal_fragmentation, -x.allocated_processes))
    best_util = max(results, key=lambda x: x.memory_utilization)

    lines.extend([
        "Analysis:",
        f"- Lowest internal fragmentation : {best_frag.strategy_name}",
        f"- Highest memory utilization    : {best_util.strategy_name}",
        "",
        "Note: In fixed-partition allocation, internal fragmentation occurs when",
        "a process is smaller than its assigned block. Free memory represents",
        "unused blocks (external fragmentation in this model).",
        "",
    ])

    return "\n".join(lines)


def save_report_to_file(report_text: str, filename: str) -> str:
    from pathlib import Path

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)
    return str(path.resolve())

