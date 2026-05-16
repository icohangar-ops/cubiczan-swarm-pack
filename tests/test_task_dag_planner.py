import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))

from task_dag import build_traceable_task_graph  # noqa: E402


def test_build_traceable_task_graph_computes_dependents_and_speedup() -> None:
    graph = build_traceable_task_graph(
        [
            {
                "task_id": "research",
                "description": "Collect evidence",
                "agent_type": "researcher",
                "tags": ["market-data"],
            },
            {
                "task_id": "analysis",
                "description": "Analyze evidence",
                "agent_type": "analyst",
                "depends_on": ["research"],
            },
            {
                "task_id": "risk",
                "description": "Review risk",
                "agent_type": "validator",
                "depends_on": ["research"],
            },
            {
                "task_id": "synthesis",
                "description": "Write final brief",
                "agent_type": "synthesizer",
                "depends_on": ["analysis", "risk"],
            },
        ],
        graph_id="demo",
    )

    assert graph.graph_id == "demo"
    assert graph.tasks["research"].dependents == ["analysis", "risk"]
    assert graph.critical_path_length == 3
    assert graph.theoretical_speedup == 1.3333


def test_build_traceable_task_graph_rejects_missing_dependency() -> None:
    with pytest.raises(ValueError, match="missing task"):
        build_traceable_task_graph(
            [{"task_id": "analysis", "description": "Analyze", "depends_on": ["research"]}]
        )


def test_build_traceable_task_graph_rejects_cycles() -> None:
    with pytest.raises(ValueError, match="cycle"):
        build_traceable_task_graph(
            [
                {"task_id": "a", "description": "A", "depends_on": ["b"]},
                {"task_id": "b", "description": "B", "depends_on": ["a"]},
            ]
        )
