from __future__ import annotations

from itertools import permutations
from typing import Dict, List, Tuple

from .model import OpType, Operation, SerializabilityResult


def _final_state_from_sequence(operations: List[Operation]) -> Dict[str, str]:
    state: Dict[str, str] = {}
    for op in operations:
        if op.op_type == OpType.WRITE and op.value is not None:
            state[op.variable] = op.value
    return state


def check_serializability(operations: List[Operation]) -> SerializabilityResult:
    observed_final_state = _final_state_from_sequence(operations)

    by_thread: Dict[str, List[Operation]] = {}
    for op in operations:
        by_thread.setdefault(op.thread_id, []).append(op)

    thread_ids = sorted(by_thread.keys())

    serial_outcomes: Dict[Tuple[str, ...], Dict[str, str]] = {}
    matching_orders: List[Tuple[str, ...]] = []

    for thread_order in permutations(thread_ids):
        serial_ops: List[Operation] = []
        for tid in thread_order:
            serial_ops.extend(by_thread[tid])

        outcome = _final_state_from_sequence(serial_ops)
        serial_outcomes[thread_order] = outcome
        if outcome == observed_final_state:
            matching_orders.append(thread_order)

    return SerializabilityResult(
        serializable=len(matching_orders) > 0,
        matching_orders=matching_orders,
        observed_final_state=observed_final_state,
        serial_outcomes=serial_outcomes,
    )
