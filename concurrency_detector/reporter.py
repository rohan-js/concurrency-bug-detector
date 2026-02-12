from __future__ import annotations

from typing import List

from .model import AnalysisResult


def _render_data_races(result: AnalysisResult) -> List[str]:
    if not result.data_races:
        return ["[+] No data races detected."]

    lines: List[str] = []
    for race in result.data_races:
        lines.append(
            "[!] DATA RACE DETECTED - "
            f"{race.race_type} on '{race.variable}' between {race.op_a.thread_id}@{race.op_a.timestamp} "
            f"and {race.op_b.thread_id}@{race.op_b.timestamp}"
        )
    return lines


def _render_lost_updates(result: AnalysisResult) -> List[str]:
    if not result.lost_updates:
        return ["[+] No lost updates detected."]

    lines: List[str] = []
    for lost in result.lost_updates:
        lines.append(
            "[!] LOST UPDATE - "
            f"'{lost.variable}' written by {lost.write_a.thread_id}@{lost.write_a.timestamp} and "
            f"{lost.write_b.thread_id}@{lost.write_b.timestamp} after reading base value {lost.read_value}"
        )
    return lines


def _render_serializability(result: AnalysisResult) -> List[str]:
    serial = result.serializability
    if serial is None:
        return ["[-] Serializability was not evaluated."]

    if serial.serializable:
        orders = [" -> ".join(order) for order in serial.matching_orders]
        return [
            "[+] SERIALIZABLE EXECUTION - matching serial thread orders: " + "; ".join(orders),
            "    Observed final state: " + str(serial.observed_final_state),
        ]

    return [
        "[!] NON-SERIALIZABLE EXECUTION - observed final state does not match any serial thread ordering",
        "    Observed final state: " + str(serial.observed_final_state),
    ]


def _render_deadlocks(result: AnalysisResult) -> List[str]:
    if not result.deadlock_cycles:
        return ["[+] No deadlocks detected."]

    lines: List[str] = []
    for cycle in result.deadlock_cycles:
        path = " -> ".join(cycle + [cycle[0]])
        lines.append(f"[!] DEADLOCK DETECTED - cycle: {path}")
    return lines


def format_report(result: AnalysisResult) -> str:
    lines: List[str] = ["======== ANALYSIS REPORT ========"]

    variables = ", ".join(result.variables_analyzed) if result.variables_analyzed else "(none)"
    lines.append(f"Variables analyzed: {variables}")
    lines.append("")

    lines.extend(_render_data_races(result))
    lines.append("")
    lines.extend(_render_lost_updates(result))
    lines.append("")
    lines.extend(_render_serializability(result))
    lines.append("")
    lines.extend(_render_deadlocks(result))

    lines.append("=================================")
    return "\n".join(lines)
