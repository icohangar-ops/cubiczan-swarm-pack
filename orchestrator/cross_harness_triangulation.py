"""Cross-Harness Triangulation Protocol.

CHTP adapts the local CHP/TLP governance pattern for code-building workflows
that deliberately combine different AI harnesses, such as Codex and Claude
Code. The module keeps packet contracts and persistence metadata compact so
teams can run cross-model validation without copying full transcripts every
round.
"""
from __future__ import annotations

import hashlib
import random
import re
import string
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


PROTOCOL_VERSION = "CHTP v1.0.0"
TLP_COMPATIBILITY = "TLP v2.2.4"


class Phase(int, Enum):
    FOUNDATION = 0
    SPEC = 1
    IMPLEMENTATION = 2


class Status(str, Enum):
    EXPLORING = "EXPLORING"
    PROVISIONAL = "PROVISIONAL"
    PROVISIONAL_LOCK = "PROVISIONAL_LOCK"
    LOCKED = "LOCKED"
    CONVERGED = "CONVERGED"
    UNRESOLVED = "UNRESOLVED"
    REFRAME_REQUIRED = "REFRAME_REQUIRED"
    HALT = "HALT"
    PHASE_GATE_FAIL = "PHASE_GATE_FAIL"


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    HALT = "HALT"
    REFRAME = "REFRAME"
    ITERATE = "ITERATE"
    CONVERGED = "CONVERGED"
    PHASE_GATE_FAIL = "PHASE_GATE_FAIL"


class ModelDelta(str, Enum):
    NONE = "NONE"
    MINOR = "MINOR"
    SIGNIFICANT = "SIGNIFICANT"


class ModelTier(int, Enum):
    SMALL = 1
    MID = 2
    HIGH = 3
    FRONTIER = 4
    UNKNOWN = 99


class VCLAltitude(str, Enum):
    R1_PHYSICAL = "R1 Physical"
    R2_TASK = "R2 Task"
    R3_HABIT = "R3 Habit"
    R4_SYSTEM = "R4 System"
    R5_IDENTITY = "R5 Identity"
    R6_RELATIONSHIP = "R6 Relationship"
    R7_VALUE = "R7 Value"
    R8_PHILOSOPHY = "R8 Philosophy"
    R9_NARRATIVE = "R9 Narrative"
    R10_ONTOLOGY = "R10 Ontology"


@dataclass(frozen=True)
class HarnessProfile:
    system: str
    model: str
    role: str
    strengths: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContextCheck:
    memory_tools: str = "UNAVAILABLE"
    prior_triangulations: int = 0
    prior_lock_versions: tuple[str, ...] = ()
    legacy_warning: bool = False
    related_locks: tuple[str, ...] = ()
    assessment: str = "SPARSE"
    action: str = "PROCEED"

    def render(self) -> str:
        return "\n".join(
            [
                "CONTEXT_CHECK:",
                f"- Memory/Tools: {self.memory_tools}",
                f"- Prior Triangulations: {self.prior_triangulations} found",
                f"- Prior Lock Versions: {list(self.prior_lock_versions) or 'NONE'}",
                f"- Legacy Warning: {'YES' if self.legacy_warning else 'NO'}",
                f"- Related Locks: {list(self.related_locks) or 'NONE'}",
                f"- Assessment: {self.assessment}",
                f"- Action: {self.action}",
            ]
        )


@dataclass(frozen=True)
class ModelParityCheck:
    origin: str
    partner: str
    delta: ModelDelta
    advisory: str = ""

    @property
    def can_proceed(self) -> bool:
        return self.delta != ModelDelta.SIGNIFICANT

    def render(self) -> str:
        lines = [
            "MODEL_PARITY_CHECK:",
            f"- Origin: {self.origin}",
            f"- Partner: {self.partner}",
            f"- Delta: {self.delta.value}",
        ]
        if self.advisory:
            lines.append(f"- Advisory: {self.advisory}")
        return "\n".join(lines)


@dataclass(frozen=True)
class R0Gate:
    solvable: tuple[str, str]
    scoped: tuple[str, str]
    valid: tuple[str, str]
    worth_it: tuple[str, str]

    @property
    def status(self) -> str:
        return "HALT" if any(item[0] == "FATAL" for item in self._items()) else "PROCEED"

    def _items(self) -> tuple[tuple[str, str], ...]:
        return (self.solvable, self.scoped, self.valid, self.worth_it)

    def render(self) -> str:
        return "\n".join(
            [
                "R0_GATE:",
                f"- Solvable: {self.solvable[0]} - {self.solvable[1]}",
                f"- Scoped: {self.scoped[0]} - {self.scoped[1]}",
                f"- Valid: {self.valid[0]} - {self.valid[1]}",
                f"- Worth_it: {self.worth_it[0]} - {self.worth_it[1]}",
                f"GATE_STATUS: {self.status}",
            ]
        )


@dataclass(frozen=True)
class FoundationDisclosure:
    weakest_assumptions: tuple[str, ...]
    invalidation_conditions: tuple[str, ...]
    key_vulnerability: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not 1 <= len(self.weakest_assumptions) <= 3:
            errors.append("weakest_assumptions must include 1-3 items")
        if not 1 <= len(self.invalidation_conditions) <= 2:
            errors.append("invalidation_conditions must include 1-2 items")
        if not self.key_vulnerability:
            errors.append("key_vulnerability is required")
        return errors

    def render(self) -> str:
        lines = ["FOUNDATION_DISCLOSURE:", "", "WEAKEST_ASSUMPTIONS:"]
        lines.extend(f"{idx}. {item}" for idx, item in enumerate(self.weakest_assumptions, 1))
        lines.extend(["", "WHAT_COULD_INVALIDATE:"])
        lines.extend(f"{idx}. {item}" for idx, item in enumerate(self.invalidation_conditions, 1))
        lines.extend(["", "KEY_VULNERABILITY:", f"- IF attacking this: {self.key_vulnerability}"])
        return "\n".join(lines)


@dataclass(frozen=True)
class FoundationAttack:
    assumption_attacks: tuple[str, ...]
    invalidation_exploitation: tuple[str, ...]
    vulnerability_strike: str
    foundation_score: int
    attack_summary: str

    def verdict(self) -> Verdict:
        return Verdict.PASS if self.foundation_score >= 70 else Verdict.REFRAME


@dataclass(frozen=True)
class VCLDiagnosis:
    item: str
    symptom_altitude: VCLAltitude
    constraint_altitude: VCLAltitude
    diagnosis: str

    def render(self) -> str:
        return (
            f"- {self.item}: symptom={self.symptom_altitude.value}; "
            f"constraint={self.constraint_altitude.value}; diagnosis={self.diagnosis}"
        )


@dataclass(frozen=True)
class TriangulationDossier:
    core_problem: str
    goal_state: tuple[str, ...]
    current_state: tuple[str, ...]
    prior_decisions: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    scope: tuple[str, ...] = ()
    origin_direction: tuple[str, ...] = ()
    prior_round_summary: tuple[str, ...] = ()
    unknowns_carried: tuple[str, ...] = ()
    foundation_score: int | None = None
    structural_vulnerabilities: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.core_problem or self.core_problem == "UNKNOWN":
            errors.append("CORE PROBLEM is required")
        populated = sum(bool(value) for value in (self.goal_state, self.current_state, self.constraints, self.scope))
        if populated < 3:
            errors.append("dossier must include at least three populated context sections")
        return errors

    def render(self) -> str:
        return "\n".join(
            [
                "DOSSIER:",
                f"CORE PROBLEM: {self.core_problem or 'UNKNOWN'}",
                f"GOAL STATE: {list(self.goal_state) or 'UNKNOWN'}",
                f"CURRENT STATE: {list(self.current_state) or 'UNKNOWN'}",
                f"PRIOR DECISIONS: {list(self.prior_decisions) or 'NONE'}",
                f"CONSTRAINTS: {list(self.constraints) or 'UNKNOWN'}",
                f"UNKNOWNS: {list(self.unknowns) or 'NONE'}",
                f"SCOPE: {list(self.scope) or 'UNKNOWN'}",
                f"ORIGIN DIRECTION: {list(self.origin_direction) or 'UNKNOWN'}",
                f"PRIOR_ROUND_SUMMARY: {list(self.prior_round_summary) or 'NONE'}",
                f"UNKNOWNS_CARRIED: {list(self.unknowns_carried) or 'NONE'}",
                f"FOUNDATION_SCORE: {self.foundation_score if self.foundation_score is not None else 'UNKNOWN'}",
                f"STRUCTURAL_VULNERABILITIES: {list(self.structural_vulnerabilities) or 'NONE'}",
            ]
        )


@dataclass(frozen=True)
class PayloadEnvelope:
    body: str
    route: str = "RX"
    payload_id: str = ""

    def __post_init__(self) -> None:
        if not self.payload_id:
            object.__setattr__(self, "payload_id", make_payload_id())

    def render(self) -> str:
        return (
            f"BEGIN_PAYLOAD [{self.route}] [{self.payload_id}]\n"
            f"{ascii_only(self.body)}\n"
            f"END_PAYLOAD [{self.route}] [{self.payload_id}]"
        )

    @property
    def echo(self) -> str:
        return f"[{self.route}] [{self.payload_id}] CONFIRMED"


@dataclass(frozen=True)
class TriangulationSession:
    title: str
    origin: HarnessProfile
    partner: HarnessProfile
    human_bridge: str
    dossier: TriangulationDossier
    context_check: ContextCheck = ContextCheck()
    parity: ModelParityCheck | None = None
    r0_gate: R0Gate | None = None
    foundation: FoundationDisclosure | None = None
    vcl: tuple[VCLDiagnosis, ...] = ()
    phase: Phase = Phase.FOUNDATION
    round_number: int = 0
    status: Status = Status.EXPLORING
    blind_spots: tuple[str, ...] = ()
    structural_vulnerabilities: tuple[str, ...] = ()


TRIGGER_PHRASES = (
    "triangulation",
    "tlp",
    "cross-ai validation",
    "claude-to-claude",
    "multi-model consensus",
    "convergence loop",
    "partner system packet",
    "foundation attack",
    "spec validation",
    "devil's advocate",
    "council spawn",
    "payload markers",
    "vcl altitude diagnosis",
)


HARNESS_ARCHETYPES = {
    "codex": HarnessProfile(
        system="Codex",
        model="UNKNOWN",
        role="implementation_harness",
        strengths=(
            "repo-local execution",
            "tests and build verification",
            "patch discipline",
            "database migration scaffolding",
        ),
        constraints=("bounded context", "must protect user worktree", "tool availability varies by sandbox"),
    ),
    "claude_code": HarnessProfile(
        system="Claude Code",
        model="UNKNOWN",
        role="spec_adversary_harness",
        strengths=(
            "long-form architecture review",
            "spec critique",
            "alternate implementation framing",
            "blind spot enumeration",
        ),
        constraints=("cannot be treated as ground truth", "must echo payload markers", "must preserve phase gates"),
    ),
}


DATABASE_BLUEPRINT_SQL = """
-- Cross-Harness Triangulation Protocol persistence blueprint.
-- Token-efficient design: session state is normalized; large packet bodies are
-- content-addressed once and referenced by hash from round events.

create table if not exists triangulation_sessions (
  session_id text primary key,
  protocol_version text not null,
  title text not null,
  origin_system text not null,
  origin_model text not null,
  partner_system text not null,
  partner_model text not null,
  human_bridge text not null,
  phase integer not null default 0,
  round_number integer not null default 0,
  status text not null default 'EXPLORING',
  foundation_score integer,
  created_at text not null,
  updated_at text not null
);

create table if not exists triangulation_items (
  item_id text primary key,
  session_id text not null references triangulation_sessions(session_id),
  label text not null,
  status text not null,
  agreement integer not null default 0,
  flip_criteria text not null default '',
  vcl_symptom_altitude text not null,
  vcl_constraint_altitude text not null,
  third_party_status text not null default 'PENDING'
);

create table if not exists triangulation_payload_blobs (
  content_hash text primary key,
  body text not null,
  token_estimate integer not null,
  created_at text not null
);

create table if not exists triangulation_round_events (
  event_id text primary key,
  session_id text not null references triangulation_sessions(session_id),
  phase integer not null,
  round_number integer not null,
  route text not null,
  payload_id text not null,
  content_hash text not null references triangulation_payload_blobs(content_hash),
  payload_echo text not null,
  status_snapshot text not null,
  created_at text not null
);

create table if not exists triangulation_validations (
  validation_id text primary key,
  session_id text not null references triangulation_sessions(session_id),
  item_id text not null references triangulation_items(item_id),
  validator text not null,
  challenge text not null,
  result text not null,
  rationale text not null,
  created_at text not null
);

create index if not exists triangulation_round_lookup
  on triangulation_round_events(session_id, phase, round_number);

create index if not exists triangulation_item_state_lookup
  on triangulation_items(session_id, status, third_party_status);
""".strip()


def make_payload_id() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(6))


def ascii_only(text: str) -> str:
    return text.encode("ascii", "ignore").decode("ascii")


def content_hash(text: str) -> str:
    return hashlib.sha256(ascii_only(text).encode("ascii")).hexdigest()


def estimate_tokens(text: str) -> int:
    # Cheap planning estimate; actual tokenizer is deliberately not required.
    return max(1, round(len(text.split()) * 1.35))


def validate_payload_envelope(rendered: str) -> bool:
    lines = [line.rstrip() for line in rendered.strip().splitlines()]
    if len(lines) < 3:
        return False
    first, last = lines[0], lines[-1]
    if not first.startswith("BEGIN_PAYLOAD [") or not last.startswith("END_PAYLOAD ["):
        return False
    return first.replace("BEGIN_PAYLOAD", "", 1).strip() == last.replace("END_PAYLOAD", "", 1).strip()


def extract_payload_marker(rendered: str) -> tuple[str, str] | None:
    first = rendered.strip().splitlines()[0] if rendered.strip() else ""
    match = re.match(r"BEGIN_PAYLOAD \[([A-Z0-9]+)\] \[([A-Z0-9]{6})\]", first)
    if not match:
        return None
    return match.group(1), match.group(2)


def payload_echo_confirmed(rendered: str, echo: str) -> bool:
    marker = extract_payload_marker(rendered)
    if not marker:
        return False
    route, payload_id = marker
    return echo.strip() == f"[{route}] [{payload_id}] CONFIRMED"


def infer_model_tier(model_name: str) -> ModelTier:
    name = (model_name or "").lower()
    if any(token in name for token in ("gpt-5.5", "opus", "frontier", "max")):
        return ModelTier.FRONTIER
    if any(token in name for token in ("gpt-5", "claude 4", "claude-4", "high")):
        return ModelTier.HIGH
    if any(token in name for token in ("sonnet", "gpt-4", "4o", "medium", "mid")):
        return ModelTier.MID
    if any(token in name for token in ("mini", "haiku", "small", "low")):
        return ModelTier.SMALL
    return ModelTier.UNKNOWN


def assess_model_parity(origin_model: str, partner_model: str) -> ModelParityCheck:
    origin_tier = infer_model_tier(origin_model)
    partner_tier = infer_model_tier(partner_model)
    if ModelTier.UNKNOWN in (origin_tier, partner_tier):
        return ModelParityCheck(
            origin=origin_model,
            partner=partner_model,
            delta=ModelDelta.MINOR,
            advisory="One or both model tiers are unknown. Treat parity as advisory and monitor dominance bias.",
        )
    gap = abs(origin_tier.value - partner_tier.value)
    if gap == 0:
        return ModelParityCheck(origin=origin_model, partner=partner_model, delta=ModelDelta.NONE)
    if gap == 1:
        return ModelParityCheck(
            origin=origin_model,
            partner=partner_model,
            delta=ModelDelta.MINOR,
            advisory="Slight analytical weight difference. Monitor for dominance bias.",
        )
    return ModelParityCheck(origin=origin_model, partner=partner_model, delta=ModelDelta.SIGNIFICANT)


def model_parity_halt_message(parity: ModelParityCheck) -> str:
    return "\n".join(
        [
            "MODEL PARITY GATE - HALT",
            "",
            "TLP CANNOT PROCEED",
            "",
            "Model mismatch detected:",
            f"Origin: {parity.origin}",
            f"Partner: {parity.partner}",
            "Status: ASYMMETRIC",
            "Running this session would bias convergence, not test it.",
            "",
            "USER ACTION REQUIRED:",
            "-> Upgrade Origin to a comparable tier, OR",
            "-> Switch Partner to a comparable model, OR",
            "-> Accept asymmetry and log it as a structural constraint.",
            "",
            "SESSION PAUSED",
        ]
    )


def evaluate_r0_gate(*, core_problem: str, scope: tuple[str, ...], current_state: tuple[str, ...], worth_cost: bool) -> R0Gate:
    return R0Gate(
        solvable=("PASS", "AI negotiation can compare spec, evidence, and implementation constraints")
        if core_problem and core_problem != "UNKNOWN"
        else ("FATAL", "core problem is UNKNOWN"),
        scoped=("PASS", "scope is bounded for five rounds") if scope else ("FATAL", "scope is empty"),
        valid=("PASS", "current state provides external reality anchor") if current_state else ("FATAL", "current state is empty"),
        worth_it=("PASS", "cross-harness validation is worth the coordination cost")
        if worth_cost
        else ("FATAL", "decision does not justify triangulation overhead"),
    )


def classify_status(agreement: int, *, round_number: int, third_party_confirmed: bool = False) -> Status:
    if round_number >= 5 and agreement < 90:
        return Status.UNRESOLVED
    if agreement >= 90 and third_party_confirmed:
        return Status.LOCKED
    if agreement >= 90:
        return Status.PROVISIONAL_LOCK
    if agreement >= 80:
        return Status.PROVISIONAL
    return Status.EXPLORING


def build_session_declaration(session: TriangulationSession) -> str:
    return "\n".join(
        [
            "TRIANGULATION LOOP INITIATED",
            f"Protocol: {TLP_COMPATIBILITY} + {PROTOCOL_VERSION}",
            f"Origin System: {session.origin.system}",
            f"Origin Model: {session.origin.model}",
            f"Partner System: {session.partner.system}",
            f"Partner Model: {session.partner.model}",
            f"Human Bridge: {session.human_bridge}",
            f"Phase: {session.phase.value} (Foundation)",
            f"Round: {session.round_number} of 5",
        ]
    )


def build_partner_shape_lock(phase: Phase = Phase.SPEC) -> str:
    if phase == Phase.FOUNDATION:
        body_contract = "Return exactly 2 sections: FOUNDATION_ATTACK and STATE_SNAPSHOT."
    else:
        body_contract = (
            "Return exactly 7 sections: ITEM_AGREEMENTS, WINNER_FRAMING, "
            "SCORING_TABLE, OBJECTIONS, FRAMEWORKS, CONVERGENCE_PLAN, STATE_SNAPSHOT."
        )
    return "\n".join(
        [
            "SHAPE_LOCK:",
            "- Reply as one code block with From:, To:, Subject: headers.",
            "- Wrap the entire response in BEGIN_PAYLOAD [RX] [6-alnum] and matching END_PAYLOAD.",
            f"- {body_contract}",
            "- Include PAYLOAD_ECHO in STATE_SNAPSHOT.",
            "- Pick one winner; no ties.",
            "- Include FLIP_CRITERIA for every PROVISIONAL item.",
            "- ASCII only.",
        ]
    )


def build_origin_packet(session: TriangulationSession, *, payload_id: str | None = None) -> str:
    errors = session.dossier.validate()
    if errors:
        raise ValueError("; ".join(errors))
    foundation_errors = session.foundation.validate() if session.foundation else ["foundation disclosure is required"]
    if foundation_errors:
        raise ValueError("; ".join(foundation_errors))

    parity = session.parity or assess_model_parity(session.origin.model, session.partner.model)
    if not parity.can_proceed:
        raise ValueError(model_parity_halt_message(parity))
    r0_gate = session.r0_gate or evaluate_r0_gate(
        core_problem=session.dossier.core_problem,
        scope=session.dossier.scope,
        current_state=session.dossier.current_state,
        worth_cost=True,
    )
    if r0_gate.status == "HALT":
        raise ValueError(r0_gate.render())

    body = "\n\n".join(
        [
            f"From: {session.origin.system}",
            f"To: {session.partner.system}",
            "Subject: CHTP - Phase 0 Round 0",
            "STYLE_GUIDE:\n- Tone: Calm, spec-like.\n- Framing: does not X unless Y.\n- Question: max 1; else UNKNOWN.\n- ASCII only.",
            session.context_check.render(),
            parity.render(),
            build_session_declaration(session),
            r0_gate.render(),
            session.foundation.render(),
            session.dossier.render(),
            "VCL_DIAGNOSIS:\n" + "\n".join(item.render() for item in session.vcl),
            build_partner_shape_lock(Phase.FOUNDATION),
        ]
    )
    envelope = PayloadEnvelope(body=body, payload_id=payload_id or "")

    return "\n\n".join(
        [
            "1. CORE_PROBLEM_STATEMENT",
            session.dossier.core_problem,
            "",
            "2. PARTNER_SYSTEM_PACKET",
            "```",
            envelope.render(),
            "```",
            "",
            "3. TRANSMISSION_CHECKLIST",
            "[ ] R0 Gate passed",
            "[ ] Foundation >=70% (Phase 0)",
            "[ ] Prior received",
            "[ ] Objections addressed",
            "[ ] No skips",
            "[ ] Dossier updated",
            "[ ] Unknowns carried",
            "[ ] Blind spots acknowledged",
            "[ ] Structural vulnerabilities carried",
            "VERDICT: ITERATE (Phase 0 Round 0 of 5)",
        ]
    )


def build_database_blueprint() -> dict[str, Any]:
    return {
        "sql": DATABASE_BLUEPRINT_SQL,
        "strategy": "content_addressed_event_store",
        "token_efficiency": {
            "store_full_payload_once": True,
            "round_events_reference_content_hash": True,
            "state_snapshots_are_compact": True,
            "recommended_summary_budget_tokens": 900,
        },
        "scaling_notes": [
            "Use SQLite for local harness runs and Postgres for shared team deployment.",
            "Move payload_blobs.body to object storage when packets exceed repository audit budget.",
            "Index session_id, phase, round_number, status, and third_party_status.",
            "Keep full transcript out of hot state; store hashes and compressed snapshots in round events.",
        ],
    }
