import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))

from governance import compute_heterogeneity_score  # noqa: E402


def test_heterogeneity_score_penalizes_monoculture() -> None:
    report = compute_heterogeneity_score(["gpt-5", "gpt-5.1", "openai-o4"])

    assert report.dominant_family == "openai"
    assert report.score < 0.5


def test_heterogeneity_score_rewards_mixed_families() -> None:
    report = compute_heterogeneity_score(["gpt-5", "claude-sonnet", "qwen2.5", "deepseek-r1"])

    assert report.score > 0.9
    assert len(set(report.families)) == 4
    assert "Finance-Grade Assurance" in report.attribution
