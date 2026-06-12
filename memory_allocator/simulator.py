"""Memory allocation algorithms: First Fit, Best Fit, Worst Fit."""

from __future__ import annotations

from typing import Callable, List, Optional

from .models import AllocationRecord, BlockState, SimulationResult


BlockChooser = Callable[[List[BlockState], int], Optional[int]]


class MemoryAllocationSimulator:
    """Simulates fixed-partition memory allocation strategies."""

    STRATEGIES = ("First Fit", "Best Fit", "Worst Fit")

    def __init__(self, blocks: List[int], processes: List[int]) -> None:
        self._validate_input(blocks, processes)
        self.blocks = list(blocks)
        self.processes = list(processes)

    @staticmethod
    def _validate_input(blocks: List[int], processes: List[int]) -> None:
        if not blocks:
            raise ValueError("لیست بلوک‌های حافظه نباید خالی باشد.")
        if not processes:
            raise ValueError("لیست پردازه‌ها نباید خالی باشد.")
        if any(not isinstance(b, int) or b <= 0 for b in blocks):
            raise ValueError("همه‌ی بلوک‌ها باید عدد صحیح مثبت باشند.")
        if any(not isinstance(p, int) or p <= 0 for p in processes):
            raise ValueError("همه‌ی پردازه‌ها باید عدد صحیح مثبت باشند.")

    def _simulate(self, strategy_name: str, chooser: BlockChooser) -> SimulationResult:
        block_states = [
            BlockState(block_id=i + 1, size=size)
            for i, size in enumerate(self.blocks)
        ]
        records: List[AllocationRecord] = []

        for pid, process_size in enumerate(self.processes, start=1):
            block_index = chooser(block_states, process_size)

            if block_index is None:
                records.append(AllocationRecord(process_id=pid, process_size=process_size))
            else:
                block = block_states[block_index]
                block.is_used = True
                block.process_id = pid
                records.append(
                    AllocationRecord(
                        process_id=pid,
                        process_size=process_size,
                        block_id=block.block_id,
                        block_size=block.size,
                    )
                )

        used_memory = sum(r.process_size for r in records if r.is_allocated)
        allocated_memory = sum(r.block_size for r in records if r.is_allocated)
        internal_fragmentation = allocated_memory - used_memory
        free_memory = sum(b.size for b in block_states if not b.is_used)
        allocated_processes = sum(1 for r in records if r.is_allocated)
        unallocated_processes = [r.process_id for r in records if not r.is_allocated]

        return SimulationResult(
            strategy_name=strategy_name,
            records=records,
            block_states=block_states,
            used_memory=used_memory,
            allocated_memory=allocated_memory,
            internal_fragmentation=internal_fragmentation,
            free_memory=free_memory,
            total_memory=sum(self.blocks),
            allocated_processes=allocated_processes,
            unallocated_processes=unallocated_processes,
        )

    @staticmethod
    def _first_fit_chooser(block_states: List[BlockState], process_size: int) -> Optional[int]:
        for i, block in enumerate(block_states):
            if not block.is_used and block.size >= process_size:
                return i
        return None

    @staticmethod
    def _best_fit_chooser(block_states: List[BlockState], process_size: int) -> Optional[int]:
        best_index: Optional[int] = None
        best_size: Optional[int] = None

        for i, block in enumerate(block_states):
            if not block.is_used and block.size >= process_size:
                if best_size is None or block.size < best_size:
                    best_size = block.size
                    best_index = i
        return best_index

    @staticmethod
    def _worst_fit_chooser(block_states: List[BlockState], process_size: int) -> Optional[int]:
        worst_index: Optional[int] = None
        worst_size: Optional[int] = None

        for i, block in enumerate(block_states):
            if not block.is_used and block.size >= process_size:
                if worst_size is None or block.size > worst_size:
                    worst_size = block.size
                    worst_index = i
        return worst_index

    def first_fit(self) -> SimulationResult:
        return self._simulate("First Fit", self._first_fit_chooser)

    def best_fit(self) -> SimulationResult:
        return self._simulate("Best Fit", self._best_fit_chooser)

    def worst_fit(self) -> SimulationResult:
        return self._simulate("Worst Fit", self._worst_fit_chooser)

    def run_all(self) -> List[SimulationResult]:
        return [self.first_fit(), self.best_fit(), self.worst_fit()]

    def run_strategy(self, strategy: str) -> SimulationResult:
        mapping = {
            "first fit": self.first_fit,
            "best fit": self.best_fit,
            "worst fit": self.worst_fit,
        }
        key = strategy.strip().lower()
        if key not in mapping:
            raise ValueError(
                f"الگوریتم نامعتبر: {strategy}. "
                f"گزینه‌های مجاز: {', '.join(self.STRATEGIES)}"
            )
        return mapping[key]()
