"""Data models for memory allocation simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AllocationRecord:
    """Allocation details for a single process."""

    process_id: int
    process_size: int
    block_id: Optional[int] = None
    block_size: Optional[int] = None

    @property
    def internal_fragmentation(self) -> int:
        if self.block_size is None:
            return 0
        return self.block_size - self.process_size

    @property
    def is_allocated(self) -> bool:
        return self.block_id is not None


@dataclass
class BlockState:
    """Runtime state of a memory block during simulation."""

    block_id: int
    size: int
    is_used: bool = False
    process_id: Optional[int] = None


@dataclass
class SimulationResult:
    """Aggregated outcome of one allocation strategy."""

    strategy_name: str
    records: List[AllocationRecord]
    block_states: List[BlockState] = field(default_factory=list)
    used_memory: int = 0
    allocated_memory: int = 0
    internal_fragmentation: int = 0
    free_memory: int = 0
    total_memory: int = 0
    allocated_processes: int = 0
    unallocated_processes: List[int] = field(default_factory=list)

    @property
    def memory_utilization(self) -> float:
        if self.total_memory == 0:
            return 0.0
        return (self.used_memory / self.total_memory) * 100

    @property
    def allocation_efficiency(self) -> float:
        """Percentage of allocated block space actually used by processes."""
        if self.allocated_memory == 0:
            return 0.0
        return (self.used_memory / self.allocated_memory) * 100

    @property
    def total_wasted_memory(self) -> int:
        return self.internal_fragmentation + self.free_memory

    @property
    def waste_ratio(self) -> float:
        if self.total_memory == 0:
            return 0.0
        return (self.total_wasted_memory / self.total_memory) * 100
