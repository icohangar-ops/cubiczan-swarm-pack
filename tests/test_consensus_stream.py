"""Tests for the streaming consensus debate (consensus.stream_consensus).

These mock the per-agent LLM call so no models or network are needed, and
verify (a) the streamed event sequence and (b) that run_consensus stays
equivalent to draining the stream.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))

from consensus import AgentVote, ConsensusEngine  # noqa: E402


def _make_engine(confidence: float, max_rounds: int = 3) -> ConsensusEngine:
    """Build an engine with stubbed models and a deterministic _query_agent."""
    engine = ConsensusEngine.__new__(ConsensusEngine)  # bypass _load_models/env
    from consensus import LMSRScorer

    engine.models = [
        {"client": None, "model": "model-a", "id": "agent-1"},
        {"client": None, "model": "model-b", "id": "agent-2"},
        {"client": None, "model": "model-c", "id": "agent-3"},
        {"client": None, "model": "model-d", "id": "agent-4"},
    ]
    engine.scorer = LMSRScorer()
    engine.threshold = 0.75
    engine.min_heterogeneity_score = 0.34
    engine.max_rounds = max_rounds

    def fake_query(model_cfg, task, context, is_contrarian):
        return AgentVote(
            agent_id=model_cfg["id"],
            model_name=model_cfg["model"],
            position=f"{model_cfg['id']} position",
            confidence=confidence,
            reasoning="because",
            is_contrarian=is_contrarian,
        )

    engine._query_agent = fake_query  # type: ignore[assignment]
    return engine


def test_stream_emits_expected_event_sequence() -> None:
    engine = _make_engine(confidence=0.9)  # high+uniform -> consensus round 1
    events = list(engine.stream_consensus("Should we proceed?", cluster_size=4))

    types = [e["type"] for e in events]
    assert types[0] == "debate_start"
    assert types[-1] == "debate_end"
    assert types.count("round_start") == types.count("round_end")
    # 4 agents vote in the (single) consensus round
    assert types.count("agent_vote") == 4
    assert types.count("round_start") == 1  # consensus reached immediately

    # Last agent in the cluster is the contrarian.
    votes = [e for e in events if e["type"] == "agent_vote"]
    assert votes[-1]["is_contrarian"] is True
    assert all(not v["is_contrarian"] for v in votes[:-1])


def test_debate_end_carries_serialized_result() -> None:
    engine = _make_engine(confidence=0.9)
    events = list(engine.stream_consensus("topic", cluster_size=4))
    end = events[-1]
    result = end["result"]
    assert result["final_position"]
    assert 0.0 <= result["consensus_score"] <= 1.0
    assert result["total_votes"] == 4
    assert isinstance(result["votes"], list)
    # Internal object is present for run_consensus but is a real ConsensusResult.
    assert end["_result_obj"].final_position == result["final_position"]


def test_run_consensus_matches_stream() -> None:
    engine = _make_engine(confidence=0.9)
    streamed = [e for e in engine.stream_consensus("topic", cluster_size=4)
                if e["type"] == "debate_end"][0]["_result_obj"]
    direct = _make_engine(confidence=0.9).run_consensus("topic", cluster_size=4)

    assert direct.final_position == streamed.final_position
    assert direct.consensus_score == streamed.consensus_score
    assert direct.debate_rounds == streamed.debate_rounds
    assert len(direct.votes) == len(streamed.votes)


def test_no_consensus_escalates() -> None:
    # Low confidence keeps score under threshold across all rounds.
    engine = _make_engine(confidence=0.2, max_rounds=2)
    events = list(engine.stream_consensus("topic", cluster_size=4))
    end = events[-1]
    assert end["type"] == "debate_end"
    assert end["result"]["escalate_to_human"] is True
    assert end["result"]["debate_rounds"] == 2
    # Both rounds ran since consensus never reached.
    assert [e["type"] for e in events].count("round_start") == 2
