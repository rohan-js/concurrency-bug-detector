from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple


class OpType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    LOCK = "LOCK"
    UNLOCK = "UNLOCK"
    WAIT = "WAIT"
    SIGNAL = "SIGNAL"


@dataclass(frozen=True)
class Operation:
    thread_id: str
    op_type: OpType
    variable: str
    value: Optional[str]
    timestamp: int

    @property
    def is_data_op(self) -> bool:
        return self.op_type in {OpType.READ, OpType.WRITE}

    def short(self) -> str:
        value_part = f", {self.value}" if self.value is not None else ""
        return f"{self.thread_id}:{self.op_type}({self.variable}{value_part})@{self.timestamp}"


@dataclass(frozen=True)
class DataRace:
    variable: str
    race_type: str
    op_a: Operation
    op_b: Operation


@dataclass(frozen=True)
class LostUpdate:
    variable: str
    read_value: str
    write_a: Operation
    write_b: Operation


@dataclass(frozen=True)
class SerializabilityResult:
    serializable: bool
    matching_orders: Sequence[Tuple[str, ...]]
    observed_final_state: Dict[str, str]
    serial_outcomes: Dict[Tuple[str, ...], Dict[str, str]]


@dataclass
class AnalysisResult:
    variables_analyzed: List[str] = field(default_factory=list)
    data_races: List[DataRace] = field(default_factory=list)
    lost_updates: List[LostUpdate] = field(default_factory=list)
    serializability: Optional[SerializabilityResult] = None
    deadlock_cycles: List[List[str]] = field(default_factory=list)
