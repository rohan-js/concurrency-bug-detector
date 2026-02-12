from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, Iterable, List, Set

from .model import OpType, Operation


class HappensBeforeGraph:
    def __init__(self, operations: List[Operation]):
        self.operations = operations
        self._adj: Dict[int, Set[int]] = defaultdict(set)
        self._reachable: Dict[int, Set[int]] = {}
        self._build_edges()

    def _build_edges(self) -> None:
        self._add_program_order_edges()
        self._add_lock_order_edges()
        self._add_write_read_edges()

    def _add_edge(self, from_ts: int, to_ts: int) -> None:
        if from_ts == to_ts:
            return
        self._adj[from_ts].add(to_ts)

    def _add_program_order_edges(self) -> None:
        by_thread: Dict[str, List[Operation]] = defaultdict(list)
        for op in self.operations:
            by_thread[op.thread_id].append(op)

        for thread_ops in by_thread.values():
            for left, right in zip(thread_ops, thread_ops[1:]):
                self._add_edge(left.timestamp, right.timestamp)

    def _add_lock_order_edges(self) -> None:
        total = len(self.operations)
        for idx, op in enumerate(self.operations):
            if op.op_type != OpType.UNLOCK:
                continue

            for j in range(idx + 1, total):
                candidate = self.operations[j]
                if (
                    candidate.op_type == OpType.LOCK
                    and candidate.variable == op.variable
                    and candidate.thread_id != op.thread_id
                ):
                    self._add_edge(op.timestamp, candidate.timestamp)
                    break

    def _add_write_read_edges(self) -> None:
        for idx, read_op in enumerate(self.operations):
            if read_op.op_type != OpType.READ or read_op.value is None:
                continue

            for j in range(idx - 1, -1, -1):
                write_op = self.operations[j]
                if (
                    write_op.op_type == OpType.WRITE
                    and write_op.variable == read_op.variable
                    and write_op.value == read_op.value
                ):
                    self._add_edge(write_op.timestamp, read_op.timestamp)
                    break

    def _compute_reachable(self, start: int) -> Set[int]:
        if start in self._reachable:
            return self._reachable[start]

        visited: Set[int] = set()
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nxt in self._adj.get(node, set()):
                if nxt in visited:
                    continue
                visited.add(nxt)
                queue.append(nxt)

        self._reachable[start] = visited
        return visited

    def happens_before(self, op_a: Operation, op_b: Operation) -> bool:
        return op_b.timestamp in self._compute_reachable(op_a.timestamp)

    def are_concurrent(self, op_a: Operation, op_b: Operation) -> bool:
        if op_a.timestamp == op_b.timestamp:
            return False
        return not self.happens_before(op_a, op_b) and not self.happens_before(op_b, op_a)

    def iter_edges(self) -> Iterable[tuple[int, int]]:
        for src, targets in self._adj.items():
            for dst in targets:
                yield src, dst
