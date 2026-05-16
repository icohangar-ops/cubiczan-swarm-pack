"""Governance controls for swarm risk management.

Attribution: Heterogeneity Score concept adapted from Georgios Fradelos, PhD,
"Finance-Grade Assurance for Agentic AI", Geneva, January 11, 2026, local
source AI Governance papers/ssrn-6306980.pdf.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import uuid
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HeterogeneityReport:
    score: float
    families: list[str]
    dominant_family: str
    dominant_share: float
    attribution: str = (
        "Adapted from Georgios Fradelos, PhD, Finance-Grade Assurance for "
        "Agentic AI, Geneva, January 11, 2026, local source "
        "AI Governance papers/ssrn-6306980.pdf."
    )


def compute_heterogeneity_score(model_names: list[str]) -> HeterogeneityReport:
    if not model_names:
        return HeterogeneityReport(0.0, [], "none", 1.0)
    families = [_model_family(name) for name in model_names]
    counts = Counter(families)
    dominant_family, dominant_count = counts.most_common(1)[0]
    dominant_share = dominant_count / len(families)
    unique_ratio = len(counts) / len(families)
    anti_monoculture = 1.0 - dominant_share
    score = round((0.65 * unique_ratio) + (0.35 * anti_monoculture), 3)
    return HeterogeneityReport(score, families, dominant_family, round(dominant_share, 3))


def _model_family(model_name: str) -> str:
    name = (model_name or "unknown").lower()
    if any(marker in name for marker in ["gpt", "openai", "o3", "o4"]):
        return "openai"
    if any(marker in name for marker in ["claude", "anthropic"]):
        return "anthropic"
    if "qwen" in name:
        return "qwen"
    if "deepseek" in name:
        return "deepseek"
    if "llama" in name or "meta" in name:
        return "llama"
    if "gemini" in name or "google" in name:
        return "google"
    if "mistral" in name or "mixtral" in name:
        return "mistral"
    return name.split(":", 1)[0].split("-", 1)[0] or "unknown"


class TrustLevel(str, Enum):
    """Execution trust level for tools, skills, agents, or departments."""

    AUTONOMOUS = "autonomous"
    SUPERVISED = "supervised"
    APPROVAL_REQUIRED = "approval_required"


class PolicyAction(str, Enum):
    """Policy gate outcome."""

    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    BLOCK = "block"


@dataclass(frozen=True)
class EvidenceRequirement:
    """Minimum evidence needed before an autonomous action can proceed."""

    min_sources: int = 0
    min_coverage: float = 0.0
    required_fields: tuple[str, ...] = ()

    def evaluate(self, evidence: dict[str, Any] | None) -> tuple[bool, list[str]]:
        evidence = evidence or {}
        failures: list[str] = []
        sources = evidence.get("sources") or []
        coverage = float(evidence.get("coverage") or 0.0)

        if len(sources) < self.min_sources:
            failures.append(f"requires at least {self.min_sources} sources")
        if coverage < self.min_coverage:
            failures.append(f"requires coverage >= {self.min_coverage}")
        for field_name in self.required_fields:
            if not evidence.get(field_name):
                failures.append(f"missing evidence field: {field_name}")

        return not failures, failures


@dataclass(frozen=True)
class ToolPolicy:
    """Runtime policy for one tool/action namespace."""

    tool: str
    trust_level: TrustLevel = TrustLevel.SUPERVISED
    max_calls: int = 20
    window_seconds: int = 3600
    approval_required_actions: tuple[str, ...] = ()
    blocked_actions: tuple[str, ...] = ()
    evidence_requirement: EvidenceRequirement = EvidenceRequirement()
    policy_id: str = "default"


@dataclass(frozen=True)
class PolicyDecision:
    """Structured response from the governance policy gate."""

    action: PolicyAction
    reason: str
    tool: str
    actor: str
    requested_action: str
    policy_id: str
    requires_approval: bool = False
    approval_id: str | None = None
    budget_remaining: int | None = None
    evidence_failures: tuple[str, ...] = ()

    @property
    def allowed(self) -> bool:
        return self.action == PolicyAction.ALLOW

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "allowed": self.allowed,
            "reason": self.reason,
            "tool": self.tool,
            "actor": self.actor,
            "requested_action": self.requested_action,
            "policy_id": self.policy_id,
            "requires_approval": self.requires_approval,
            "approval_id": self.approval_id,
            "budget_remaining": self.budget_remaining,
            "evidence_failures": list(self.evidence_failures),
        }


@dataclass(frozen=True)
class AuditVerificationReport:
    """Result of validating a governance audit chain."""

    valid: bool
    event_count: int
    last_hash: str
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "event_count": self.event_count,
            "last_hash": self.last_hash,
            "error": self.error,
        }


class AuditKernel:
    """
    Append-only JSONL audit chain.

    Each event stores the previous hash and a hash over the canonical event body.
    If `hmac_key` is provided, the chain uses HMAC-SHA256 and records a short
    key identifier without exposing the key itself.
    """

    def __init__(self, audit_path: str | Path, hmac_key: str | bytes | None = None):
        self.audit_path = Path(audit_path)
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(hmac_key, str):
            self.hmac_key = hmac_key.encode("utf-8")
        else:
            self.hmac_key = hmac_key
        self.key_id = self._key_id(self.hmac_key) if self.hmac_key else None

    def record(
        self,
        *,
        actor: str,
        action: str,
        resource: str = "",
        payload: dict[str, Any] | None = None,
        decision: PolicyDecision | None = None,
        evidence: dict[str, Any] | None = None,
        policy_id: str | None = None,
    ) -> dict[str, Any]:
        previous_hash = self._last_hash()
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": round(time.time(), 6),
            "actor": actor,
            "action": action,
            "resource": resource,
            "payload": payload or {},
            "decision": decision.to_dict() if decision else None,
            "evidence": evidence or {},
            "policy_id": policy_id or (decision.policy_id if decision else None),
            "previous_hash": previous_hash,
            "key_id": self.key_id,
        }
        event["hash"] = self._digest(event)
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event

    def verify_chain(self) -> AuditVerificationReport:
        if not self.audit_path.exists():
            return AuditVerificationReport(True, 0, "")

        previous_hash = ""
        count = 0
        with self.audit_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    return AuditVerificationReport(False, count, previous_hash, f"line {line_number}: {exc}")

                if event.get("previous_hash") != previous_hash:
                    return AuditVerificationReport(
                        False,
                        count,
                        previous_hash,
                        f"line {line_number}: previous_hash mismatch",
                    )
                expected_hash = self._digest(event)
                if event.get("hash") != expected_hash:
                    return AuditVerificationReport(
                        False,
                        count,
                        previous_hash,
                        f"line {line_number}: hash mismatch",
                    )
                previous_hash = expected_hash
                count += 1

        return AuditVerificationReport(True, count, previous_hash)

    def _last_hash(self) -> str:
        if not self.audit_path.exists():
            return ""
        last_hash = ""
        with self.audit_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    last_hash = json.loads(line).get("hash", "")
        return last_hash

    def _digest(self, event: dict[str, Any]) -> str:
        body = dict(event)
        body.pop("hash", None)
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if self.hmac_key:
            return hmac.new(self.hmac_key, encoded, hashlib.sha256).hexdigest()
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _key_id(hmac_key: bytes) -> str:
        return hashlib.sha256(hmac_key).hexdigest()[:12]


class PolicyGate:
    """
    Fail-closed policy engine for autonomous swarm actions.

    It handles trust tiers, explicit approval gates, blocked actions, evidence
    thresholds, rate budgets, and kill switches. Decisions can be recorded to
    an AuditKernel for replay and incident review.
    """

    def __init__(
        self,
        policies: dict[str, ToolPolicy] | None = None,
        audit_kernel: AuditKernel | None = None,
    ):
        self.policies = policies or {}
        self.audit_kernel = audit_kernel
        self.kill_switches: set[str] = set()
        self._call_history: dict[str, list[float]] = {}

    def pause_tool(self, tool: str) -> None:
        self.kill_switches.add(tool)

    def resume_tool(self, tool: str) -> None:
        self.kill_switches.discard(tool)

    def evaluate(
        self,
        *,
        tool: str,
        actor: str,
        action: str,
        intent: str = "",
        evidence: dict[str, Any] | None = None,
        approved_by_human: bool = False,
        approval_id: str | None = None,
    ) -> PolicyDecision:
        policy = self.policies.get(tool, ToolPolicy(tool=tool))
        decision = self._evaluate_policy(
            policy=policy,
            actor=actor,
            action=action,
            intent=intent,
            evidence=evidence,
            approved_by_human=approved_by_human,
            approval_id=approval_id,
        )
        if decision.allowed:
            self._remember_call(tool)

        if self.audit_kernel:
            self.audit_kernel.record(
                actor=actor,
                action=action,
                resource=tool,
                payload={"intent": intent},
                decision=decision,
                evidence=evidence,
                policy_id=policy.policy_id,
            )

        return decision

    def _evaluate_policy(
        self,
        *,
        policy: ToolPolicy,
        actor: str,
        action: str,
        intent: str,
        evidence: dict[str, Any] | None,
        approved_by_human: bool,
        approval_id: str | None,
    ) -> PolicyDecision:
        del intent
        remaining = self._remaining_budget(policy)

        if policy.tool in self.kill_switches:
            return self._decision(PolicyAction.BLOCK, "tool is paused by kill switch", policy, actor, action, remaining)

        if action in policy.blocked_actions:
            return self._decision(PolicyAction.BLOCK, "action is explicitly blocked", policy, actor, action, remaining)

        if remaining <= 0:
            return self._decision(PolicyAction.BLOCK, "rate budget exhausted", policy, actor, action, 0)

        evidence_ok, failures = policy.evidence_requirement.evaluate(evidence)
        if not evidence_ok:
            return self._decision(
                PolicyAction.BLOCK,
                "evidence threshold not met",
                policy,
                actor,
                action,
                remaining,
                evidence_failures=tuple(failures),
            )

        needs_approval = (
            policy.trust_level == TrustLevel.APPROVAL_REQUIRED
            or action in policy.approval_required_actions
        )
        if needs_approval and not (approved_by_human and approval_id):
            return self._decision(
                PolicyAction.REQUIRE_APPROVAL,
                "human approval required",
                policy,
                actor,
                action,
                remaining,
                requires_approval=True,
                approval_id=approval_id or f"approval-{uuid.uuid4().hex[:10]}",
            )

        return self._decision(PolicyAction.ALLOW, "policy checks passed", policy, actor, action, remaining - 1)

    def _remaining_budget(self, policy: ToolPolicy) -> int:
        now = time.time()
        history = [
            ts for ts in self._call_history.get(policy.tool, [])
            if now - ts <= policy.window_seconds
        ]
        self._call_history[policy.tool] = history
        return max(policy.max_calls - len(history), 0)

    def _remember_call(self, tool: str) -> None:
        self._call_history.setdefault(tool, []).append(time.time())

    @staticmethod
    def _decision(
        action: PolicyAction,
        reason: str,
        policy: ToolPolicy,
        actor: str,
        requested_action: str,
        budget_remaining: int | None,
        *,
        requires_approval: bool = False,
        approval_id: str | None = None,
        evidence_failures: tuple[str, ...] = (),
    ) -> PolicyDecision:
        return PolicyDecision(
            action=action,
            reason=reason,
            tool=policy.tool,
            actor=actor,
            requested_action=requested_action,
            policy_id=policy.policy_id,
            requires_approval=requires_approval,
            approval_id=approval_id,
            budget_remaining=budget_remaining,
            evidence_failures=evidence_failures,
        )


def build_default_policy_gate(audit_path: str | Path | None = None, hmac_key: str | bytes | None = None) -> PolicyGate:
    """Create Cubiczan's default production-safety policy set."""

    audit_kernel = AuditKernel(audit_path, hmac_key=hmac_key) if audit_path else None
    irreversible_actions = (
        "send_money",
        "sign_contract",
        "publish_post",
        "send_email",
        "send_client_message",
        "delete_data",
        "deploy_mainnet",
        "external_purchase",
    )
    policies = {
        "swarm.execute": ToolPolicy(
            tool="swarm.execute",
            trust_level=TrustLevel.SUPERVISED,
            max_calls=100,
            window_seconds=3600,
            evidence_requirement=EvidenceRequirement(min_sources=0, min_coverage=0.0),
            policy_id="swarm-execute-v1",
        ),
        "external.communication": ToolPolicy(
            tool="external.communication",
            trust_level=TrustLevel.APPROVAL_REQUIRED,
            max_calls=50,
            window_seconds=3600,
            approval_required_actions=("publish_post", "send_email", "send_client_message"),
            policy_id="external-comms-v1",
        ),
        "financial.action": ToolPolicy(
            tool="financial.action",
            trust_level=TrustLevel.APPROVAL_REQUIRED,
            max_calls=10,
            window_seconds=3600,
            approval_required_actions=("send_money", "external_purchase"),
            blocked_actions=("sign_contract",),
            evidence_requirement=EvidenceRequirement(min_sources=2, min_coverage=0.75),
            policy_id="financial-action-v1",
        ),
        "legal.action": ToolPolicy(
            tool="legal.action",
            trust_level=TrustLevel.APPROVAL_REQUIRED,
            max_calls=10,
            window_seconds=3600,
            approval_required_actions=("sign_contract",),
            policy_id="legal-action-v1",
        ),
    }

    for action in irreversible_actions:
        policies[f"irreversible.{action}"] = ToolPolicy(
            tool=f"irreversible.{action}",
            trust_level=TrustLevel.APPROVAL_REQUIRED,
            max_calls=5,
            window_seconds=3600,
            approval_required_actions=(action,),
            policy_id=f"irreversible-{action}-v1",
        )

    return PolicyGate(policies=policies, audit_kernel=audit_kernel)
