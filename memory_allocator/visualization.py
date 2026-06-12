"""Chart generation for algorithm comparison."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .models import SimulationResult


def render_comparison_chart(
    results: List[SimulationResult],
    *,
    save_path: Optional[str] = None,
    show: bool = True,
) -> Optional[str]:
    try:
        import matplotlib.pyplot as plt
        import matplotlib
    except ImportError:
        print("\nmatplotlib نصب نیست. برای رسم نمودار این دستور را اجرا کن:")
        print("  pip install matplotlib")
        return None

    matplotlib.rcParams["font.family"] = "DejaVu Sans"

    strategies = [r.strategy_name for r in results]
    frag = [r.internal_fragmentation for r in results]
    free = [r.free_memory for r in results]
    util = [r.memory_utilization for r in results]
    used = [r.used_memory for r in results]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Memory Allocation Algorithm Comparison", fontsize=14, fontweight="bold")

    x = range(len(strategies))
    width = 0.35

    ax1 = axes[0]
    bars1 = ax1.bar([i - width / 2 for i in x], used, width, label="Used Memory", color="#2ecc71")
    bars2 = ax1.bar([i + width / 2 for i in x], frag, width, label="Internal Frag.", color="#e74c3c")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(strategies)
    ax1.set_ylabel("Memory (KB)")
    ax1.set_title("Used Memory vs Internal Fragmentation")
    ax1.legend()
    ax1.bar_label(bars1, padding=2, fontsize=8)
    ax1.bar_label(bars2, padding=2, fontsize=8)

    ax2 = axes[1]
    color_util = "#3498db"
    color_free = "#95a5a6"
    ax2.bar(strategies, util, color=color_util, alpha=0.85, label="Utilization (%)")
    ax2.set_ylabel("Utilization (%)", color=color_util)
    ax2.tick_params(axis="y", labelcolor=color_util)
    ax2.set_ylim(0, max(max(util) * 1.2, 10))

    ax2_twin = ax2.twinx()
    ax2_twin.plot(strategies, free, color=color_free, marker="o", linewidth=2, label="Free Memory")
    ax2_twin.set_ylabel("Free Memory (KB)", color=color_free)
    ax2_twin.tick_params(axis="y", labelcolor=color_free)
    ax2.set_title("Utilization & Free Memory")

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    plt.tight_layout()

    saved: Optional[str] = None
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150, bbox_inches="tight")
        saved = str(path.resolve())

    if show:
        plt.show()
    else:
        plt.close(fig)

    return saved


def render_memory_map_chart(
    result: SimulationResult,
    *,
    save_path: Optional[str] = None,
    show: bool = True,
) -> Optional[str]:
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        return None

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.set_title(f"Memory Map - {result.strategy_name}", fontweight="bold")
    ax.set_xlim(0, result.total_memory)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xlabel("Memory (KB)")

    colors_used = ["#3498db", "#2ecc71", "#9b59b6", "#e67e22", "#1abc9c", "#f39c12"]
    x_offset = 0

    for i, block in enumerate(result.block_states):
        color = colors_used[i % len(colors_used)] if block.is_used else "#ecf0f1"
        rect = mpatches.FancyBboxPatch(
            (x_offset, 0.2),
            block.size,
            0.6,
            boxstyle="round,pad=0.02,rounding_size=2",
            facecolor=color,
            edgecolor="#2c3e50",
            linewidth=1.2,
        )
        ax.add_patch(rect)

        label = f"B{block.block_id}\n{block.size}KB"
        if block.is_used:
            record = next(r for r in result.records if r.block_id == block.block_id)
            label += f"\nP{block.process_id} ({record.process_size}KB)"
        ax.text(
            x_offset + block.size / 2,
            0.5,
            label,
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold" if block.is_used else "normal",
        )
        x_offset += block.size

    legend_used = mpatches.Patch(color="#3498db", label="Allocated Block")
    legend_free = mpatches.Patch(color="#ecf0f1", label="Free Block")
    ax.legend(handles=[legend_used, legend_free], loc="upper right")

    plt.tight_layout()

    saved: Optional[str] = None
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150, bbox_inches="tight")
        saved = str(path.resolve())

    if show:
        plt.show()
    else:
        plt.close(fig)

    return saved
