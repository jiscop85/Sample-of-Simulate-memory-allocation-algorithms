"""Unit tests for memory allocation simulator."""

import unittest

from memory_allocator.simulator import MemoryAllocationSimulator


class TestMemoryAllocationSimulator(unittest.TestCase):
    BLOCKS = [100, 500, 200, 300, 600]
    PROCESSES = [212, 417, 112, 426]

    def setUp(self) -> None:
        self.simulator = MemoryAllocationSimulator(self.BLOCKS, self.PROCESSES)

    def test_first_fit_allocations(self) -> None:
        result = self.simulator.first_fit()
        allocated = [(r.process_id, r.block_id) for r in result.records if r.is_allocated]
        self.assertEqual(allocated, [(1, 2), (2, 5), (3, 3)])
        self.assertEqual(result.unallocated_processes, [4])

    def test_best_fit_allocations(self) -> None:
        result = self.simulator.best_fit()
        allocated = [(r.process_id, r.block_id) for r in result.records if r.is_allocated]
        self.assertEqual(allocated, [(1, 4), (2, 2), (3, 3), (4, 5)])

    def test_worst_fit_allocations(self) -> None:
        result = self.simulator.worst_fit()
        allocated = [(r.process_id, r.block_id) for r in result.records if r.is_allocated]
        self.assertEqual(allocated, [(1, 5), (2, 2), (3, 4)])
        self.assertEqual(result.unallocated_processes, [4])

    def test_internal_fragmentation(self) -> None:
        self.assertEqual(self.simulator.first_fit().internal_fragmentation, 559)
        self.assertEqual(self.simulator.best_fit().internal_fragmentation, 433)
        self.assertEqual(self.simulator.worst_fit().internal_fragmentation, 659)

    def test_best_fit_allocates_all_processes(self) -> None:
        result = self.simulator.best_fit()
        self.assertEqual(result.allocated_processes, 4)
        self.assertEqual(result.unallocated_processes, [])

    def test_memory_utilization_best_fit(self) -> None:
        result = self.simulator.best_fit()
        expected = (1167 / 1700) * 100
        self.assertAlmostEqual(result.memory_utilization, expected, places=2)

    def test_partial_allocation(self) -> None:
        sim = MemoryAllocationSimulator([200, 300], [250, 400, 100])
        result = sim.first_fit()
        self.assertEqual(result.allocated_processes, 2)
        self.assertEqual(result.unallocated_processes, [2])

    def test_invalid_empty_blocks(self) -> None:
        with self.assertRaises(ValueError):
            MemoryAllocationSimulator([], [100])

    def test_invalid_negative_size(self) -> None:
        with self.assertRaises(ValueError):
            MemoryAllocationSimulator([100, -50], [80])


if __name__ == "__main__":
    unittest.main()
