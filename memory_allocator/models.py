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
