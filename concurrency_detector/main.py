from __future__ import annotations

import argparse
import sys
from typing import List

from .deadlock import detect_deadlocks
from .happens_before import HappensBeforeGraph
from .model import AnalysisResult, OpType, Operation
from .parser import parse_log
from .race_detector import detect_data_races, detect_lost_updates
from .reporter import format_report
from .serializability import check_serializability


def _variables_analyzed(operations: List[Operation]) -> List[str]:
    variables = {
        op.variable
        for op in operations
        if op.op_type in {OpType.READ, OpType.WRITE}
    }
    return sorted(variables)


def run(filepath: str) -> AnalysisResult:
    operations = parse_log(filepath)

    hb_graph = HappensBeforeGraph(operations)
    data_races = detect_data_races(operations, hb_graph)
    lost_updates = detect_lost_updates(operations, hb_graph)
    serializability = check_serializability(operations)
    deadlock_cycles = detect_deadlocks(operations)

    return AnalysisResult(
        variables_analyzed=_variables_analyzed(operations),
        data_races=data_races,
        lost_updates=lost_updates,
        serializability=serializability,
        deadlock_cycles=deadlock_cycles,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="concurrency_detector",
        description="Analyze multithreaded execution logs for common concurrency bugs.",
    )
    parser.add_argument("logfile", help="Path to input execution log")
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = run(args.logfile)
    except Exception as exc:  # pragma: no cover - CLI surface
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(format_report(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
