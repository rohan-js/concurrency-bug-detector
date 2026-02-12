from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Optional

from .happens_before import HappensBeforeGraph
from .model import DataRace, LostUpdate, OpType, Operation


@dataclass(frozen=True)
class _WriteContext:
    op: Operation
    read_value_before_write: Optional[str]


def detect_data_races(operations: List[Operation], hb_graph: HappensBeforeGraph) -> List[DataRace]:
    races: List[DataRace] = []
    data_ops = [op for op in operations if op.op_type in {OpType.READ, OpType.WRITE}]

    for op_a, op_b in combinations(data_ops, 2):
        if op_a.thread_id == op_b.thread_id:
            continue
        if op_a.variable != op_b.variable:
            continue
        if op_a.op_type != OpType.WRITE and op_b.op_type != OpType.WRITE:
            continue
        if not hb_graph.are_concurrent(op_a, op_b):
            continue

        race_type = "WRITE-WRITE" if op_a.op_type == op_b.op_type == OpType.WRITE else "READ-WRITE"
        races.append(DataRace(variable=op_a.variable, race_type=race_type, op_a=op_a, op_b=op_b))

    return races


def detect_lost_updates(operations: List[Operation], hb_graph: HappensBeforeGraph) -> List[LostUpdate]:
    writes_by_variable: Dict[str, List[_WriteContext]] = defaultdict(list)
    last_read_by_thread: Dict[tuple[str, str], str] = {}

    for op in operations:
        key = (op.thread_id, op.variable)
        if op.op_type == OpType.READ and op.value is not None:
            last_read_by_thread[key] = op.value
            continue

        if op.op_type == OpType.WRITE:
            writes_by_variable[op.variable].append(
                _WriteContext(op=op, read_value_before_write=last_read_by_thread.get(key))
            )

    lost_updates: List[LostUpdate] = []
    seen_pairs = set()
    for variable, write_contexts in writes_by_variable.items():
        for ctx_a, ctx_b in combinations(write_contexts, 2):
            if ctx_a.op.thread_id == ctx_b.op.thread_id:
                continue
            if ctx_a.read_value_before_write is None or ctx_b.read_value_before_write is None:
                continue
            if ctx_a.read_value_before_write != ctx_b.read_value_before_write:
                continue
            if not hb_graph.are_concurrent(ctx_a.op, ctx_b.op):
                continue

            pair_key = tuple(sorted((ctx_a.op.timestamp, ctx_b.op.timestamp)))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            lost_updates.append(
                LostUpdate(
                    variable=variable,
                    read_value=ctx_a.read_value_before_write,
                    write_a=ctx_a.op,
                    write_b=ctx_b.op,
                )
            )

    return lost_updates
