import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))

from governance import (  # noqa: E402
    AuditKernel,
    EvidenceRequirement,
    PolicyAction,
    PolicyGate,
    ToolPolicy,
    TrustLevel,
    build_default_policy_gate,
    compute_heterogeneity_score,
)


def test_heterogeneity_score_penalizes_monoculture() -> None:
    report = compute_heterogeneity_score(["gpt-5", "gpt-5.1", "openai-o4"])

    assert report.dominant_family == "openai"
    assert report.score < 0.5


def test_heterogeneity_score_rewards_mixed_families() -> None:
    report = compute_heterogeneity_score(["gpt-5", "claude-sonnet", "qwen2.5", "deepseek-r1"])

    assert report.score > 0.9
    assert len(set(report.families)) == 4
    assert "Finance-Grade Assurance" in report.attribution


def test_audit_kernel_detects_tampering(tmp_path: Path) -> None:
    audit_path = tmp_path / "governance.jsonl"
    kernel = AuditKernel(audit_path, hmac_key="test-secret")

    kernel.record(actor="agent-a", action="read", resource="market-data")
    kernel.record(actor="agent-b", action="summarize", resource="report")

    assert kernel.verify_chain().valid

    text = audit_path.read_text(encoding="utf-8")
    audit_path.write_text(text.replace("summarize", "wire-money"), encoding="utf-8")

    report = kernel.verify_chain()
    assert not report.valid
    assert "hash mismatch" in report.error


def test_policy_gate_requires_human_approval_for_external_comms() -> None:
    gate = build_default_policy_gate()

    decision = gate.evaluate(
        tool="external.communication",
        actor="content-agent",
        action="publish_post",
        intent="Publish a LinkedIn update",
    )

    assert decision.action == PolicyAction.REQUIRE_APPROVAL
    assert decision.requires_approval
    assert decision.approval_id

    approved = gate.evaluate(
        tool="external.communication",
        actor="content-agent",
        action="publish_post",
        intent="Publish a LinkedIn update",
        approved_by_human=True,
        approval_id=decision.approval_id,
    )

    assert approved.allowed


def test_policy_gate_fails_closed_when_evidence_is_weak() -> None:
    gate = PolicyGate(
        policies={
            "financial.action": ToolPolicy(
                tool="financial.action",
                trust_level=TrustLevel.APPROVAL_REQUIRED,
                evidence_requirement=EvidenceRequirement(min_sources=2, min_coverage=0.75),
            )
        }
    )

    decision = gate.evaluate(
        tool="financial.action",
        actor="cfo-agent",
        action="send_money",
        evidence={"sources": ["ledger"], "coverage": 0.5},
        approved_by_human=True,
        approval_id="approval-123",
    )

    assert decision.action == PolicyAction.BLOCK
    assert "coverage" in " ".join(decision.evidence_failures)


def test_policy_gate_enforces_rate_budget() -> None:
    gate = PolicyGate(
        policies={
            "web.fetch": ToolPolicy(
                tool="web.fetch",
                trust_level=TrustLevel.AUTONOMOUS,
                max_calls=1,
                window_seconds=60,
            )
        }
    )

    assert gate.evaluate(tool="web.fetch", actor="researcher", action="read").allowed
    blocked = gate.evaluate(tool="web.fetch", actor="researcher", action="read")

    assert blocked.action == PolicyAction.BLOCK
    assert blocked.reason == "rate budget exhausted"
