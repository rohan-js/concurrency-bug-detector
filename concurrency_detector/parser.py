from __future__ import annotations

from pathlib import Path
from typing import List

from .model import OpType, Operation


def _parse_op_type(token: str, line_no: int) -> OpType:
    try:
        return OpType(token)
    except ValueError as exc:
        valid = ", ".join(op.value for op in OpType)
        raise ValueError(f"Line {line_no}: unsupported operation '{token}'. Expected one of: {valid}") from exc


def parse_log(filepath: str) -> List[Operation]:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input log not found: {filepath}")

    operations: List[Operation] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 3 or len(parts) > 4:
                raise ValueError(
                    f"Line {line_no}: expected format '<ThreadID> <OP> <Variable> [Value]', got: {raw_line.rstrip()}"
                )

            thread_id, op_token, variable = parts[0], parts[1], parts[2]
            value = parts[3] if len(parts) == 4 else None

            op_type = _parse_op_type(op_token, line_no)
            if op_type in {OpType.READ, OpType.WRITE} and value is None:
                raise ValueError(f"Line {line_no}: {op_type} requires a value")
            if op_type in {OpType.LOCK, OpType.UNLOCK, OpType.WAIT, OpType.SIGNAL} and value is not None:
                raise ValueError(f"Line {line_no}: {op_type} must not include a value")

            operations.append(
                Operation(
                    thread_id=thread_id,
                    op_type=op_type,
                    variable=variable,
                    value=value,
                    timestamp=len(operations),
                )
            )

    if not operations:
        raise ValueError("Input log contains no operations")

    return operations
