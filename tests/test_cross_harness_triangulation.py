import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))

from cross_harness_triangulation import (  # noqa: E402
    FoundationAttack,
    FoundationDisclosure,
    HarnessProfile,
    ModelDelta,
    Status,
    TriangulationDossier,
    TriangulationSession,
    VCLAltitude,
    VCLDiagnosis,
    assess_model_parity,
    build_database_blueprint,
    build_origin_packet,
    classify_status,
    evaluate_r0_gate,
    payload_echo_confirmed,
    validate_payload_envelope,
)


def _session() -> TriangulationSession:
    return TriangulationSession(
        title="Validate cross-harness database architecture",
        origin=HarnessProfile(system="Codex", model="GPT-5.5", role="implementation_harness"),
        partner=HarnessProfile(system="Claude Code", model="Claude Opus 4.6", role="spec_adversary_harness"),
        human_bridge="Shyam",
        dossier=TriangulationDossier(
            core_problem="Validate whether a content-addressed event store supports scalable cross-harness code review.",
            goal_state=(">=90% agreement before implementation", "third-party validation before LOCKED"),
            current_state=("Cubiczan has governance, consensus, and anti-sycophancy primitives.",),
            constraints=("Max five rounds", "ASCII payloads", "No full transcript duplication in hot state"),
            scope=("Protocol module, docs, tests, and database blueprint",),
            origin_direction=("Use content-addressed payload bodies", "Keep state snapshots compact"),
        ),
        foundation=FoundationDisclosure(
            weakest_assumptions=(
                "Harnesses can preserve PAYLOAD markers through copy/paste.",
                "Compact state snapshots are enough to resume the loop.",
            ),
            invalidation_conditions=(
                "Partner omits PAYLOAD_ECHO.",
                "Implementation begins before Phase 1 spec lock.",
            ),
            key_vulnerability="False consensus caused by both systems optimizing for agreement.",
        ),
        vcl=(
            VCLDiagnosis(
                item="database_architecture",
                symptom_altitude=VCLAltitude.R2_TASK,
                constraint_altitude=VCLAltitude.R4_SYSTEM,
                diagnosis="Schema drift is a system constraint, not a task typo.",
            ),
        ),
    )


def test_model_parity_blocks_significant_asymmetry() -> None:
    parity = assess_model_parity("Claude Haiku", "GPT-5.5")

    assert parity.delta == ModelDelta.SIGNIFICANT
    assert not parity.can_proceed


def test_model_parity_allows_frontier_pair() -> None:
    parity = assess_model_parity("GPT-5.5", "Claude Opus 4.6")

    assert parity.delta == ModelDelta.NONE
    assert parity.can_proceed


def test_origin_packet_uses_three_sections_and_payload_echo() -> None:
    packet = build_origin_packet(_session(), payload_id="ABC123")

    assert packet.count("1. CORE_PROBLEM_STATEMENT") == 1
    assert packet.count("2. PARTNER_SYSTEM_PACKET") == 1
    assert packet.count("3. TRANSMISSION_CHECKLIST") == 1
    assert "VCL_DIAGNOSIS:" in packet
    assert "BEGIN_PAYLOAD [RX] [ABC123]" in packet
    assert "END_PAYLOAD [RX] [ABC123]" in packet
    assert packet.encode("ascii").decode("ascii") == packet

    payload = re.search(r"```\n(.*?)\n```", packet, re.DOTALL)
    assert payload
    assert validate_payload_envelope(payload.group(1))
    assert payload_echo_confirmed(payload.group(1), "[RX] [ABC123] CONFIRMED")


def test_r0_gate_halts_unknown_core_problem() -> None:
    gate = evaluate_r0_gate(core_problem="UNKNOWN", scope=("x",), current_state=("y",), worth_cost=True)

    assert gate.status == "HALT"
    assert "core problem is UNKNOWN" in gate.render()


def test_foundation_attack_requires_score_threshold() -> None:
    weak = FoundationAttack(
        assumption_attacks=("Marker discipline can fail.",),
        invalidation_exploitation=("Partner can omit echo.",),
        vulnerability_strike="False consensus.",
        foundation_score=64,
        attack_summary="Foundation is not strong enough yet.",
    )
    strong = FoundationAttack(
        assumption_attacks=("Marker discipline can fail but is detectable.",),
        invalidation_exploitation=("Omitted echo triggers resend.",),
        vulnerability_strike="False consensus is carried as a structural vulnerability.",
        foundation_score=82,
        attack_summary="Foundation can proceed with explicit gates.",
    )

    assert weak.verdict().value == "REFRAME"
    assert strong.verdict().value == "PASS"


def test_status_progression_requires_third_party_before_locked() -> None:
    assert classify_status(92, round_number=2) == Status.PROVISIONAL_LOCK
    assert classify_status(92, round_number=2, third_party_confirmed=True) == Status.LOCKED
    assert classify_status(86, round_number=5) == Status.UNRESOLVED


def test_database_blueprint_is_content_addressed() -> None:
    blueprint = build_database_blueprint()
    sql = blueprint["sql"]

    assert blueprint["strategy"] == "content_addressed_event_store"
    assert "triangulation_payload_blobs" in sql
    assert "content_hash text primary key" in sql
    assert "triangulation_round_events" in sql
    assert blueprint["token_efficiency"]["store_full_payload_once"] is True
