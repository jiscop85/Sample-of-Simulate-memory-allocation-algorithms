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
