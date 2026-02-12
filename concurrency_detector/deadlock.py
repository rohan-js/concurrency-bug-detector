from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set, Tuple

from .model import OpType, Operation


def _canonical_cycle(cycle: List[str]) -> Tuple[str, ...]:
    if not cycle:
        return tuple()

    rotations = [tuple(cycle[idx:] + cycle[:idx]) for idx in range(len(cycle))]
    reversed_cycle = list(reversed(cycle))
    rotations.extend(tuple(reversed_cycle[idx:] + reversed_cycle[:idx]) for idx in range(len(cycle)))
    return min(rotations)


def detect_deadlocks(operations: List[Operation]) -> List[List[str]]:
    lock_holder: Dict[str, str] = {}
    held_locks: Dict[str, Set[str]] = defaultdict(set)
    wait_for: Dict[str, Set[str]] = defaultdict(set)

    for op in operations:
        lock_name = op.variable
        if op.op_type == OpType.LOCK:
            holder = lock_holder.get(lock_name)
            if holder is None:
                lock_holder[lock_name] = op.thread_id
                held_locks[op.thread_id].add(lock_name)
            continue

        if op.op_type == OpType.UNLOCK:
            if lock_holder.get(lock_name) == op.thread_id:
                lock_holder.pop(lock_name, None)
                held_locks[op.thread_id].discard(lock_name)
            continue

        if op.op_type == OpType.WAIT:
            holder = lock_holder.get(lock_name)
            if holder is not None and holder != op.thread_id:
                wait_for[op.thread_id].add(holder)
            continue

    all_threads = set(wait_for.keys())
    for waiters in wait_for.values():
        all_threads.update(waiters)

    visited: Set[str] = set()
    in_stack: Set[str] = set()
    stack: List[str] = []
    cycle_keys: Set[Tuple[str, ...]] = set()

    def dfs(node: str) -> None:
        visited.add(node)
        in_stack.add(node)
        stack.append(node)

        for neighbor in wait_for.get(node, set()):
            if neighbor not in visited:
                dfs(neighbor)
                continue
            if neighbor in in_stack:
                start = stack.index(neighbor)
                cycle = stack[start:]
                cycle_keys.add(_canonical_cycle(cycle))

        stack.pop()
        in_stack.remove(node)

    for thread_id in sorted(all_threads):
        if thread_id not in visited:
            dfs(thread_id)

    return [list(cycle) for cycle in sorted(cycle_keys)]
