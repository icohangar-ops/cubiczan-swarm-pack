# Cubiczan Orchestrator - Hybrid PARL + Stigmergy Coordination Engine

from .governance import (
    AuditKernel,
    EvidenceRequirement,
    PolicyAction,
    PolicyGate,
    ToolPolicy,
    TrustLevel,
    build_default_policy_gate,
    compute_heterogeneity_score,
)
from .task_dag import build_traceable_task_graph

__all__ = [
    "AuditKernel",
    "EvidenceRequirement",
    "PolicyAction",
    "PolicyGate",
    "ToolPolicy",
    "TrustLevel",
    "build_default_policy_gate",
    "build_traceable_task_graph",
    "compute_heterogeneity_score",
]
"""Cubiczan orchestration primitives."""

from .cross_harness_triangulation import (
    PROTOCOL_VERSION as CHTP_VERSION,
    TLP_COMPATIBILITY as CHTP_TLP_COMPATIBILITY,
    FoundationAttack,
    FoundationDisclosure,
    HarnessProfile,
    ModelDelta,
    Phase,
    TriangulationDossier,
    TriangulationSession,
    VCLAltitude,
    VCLDiagnosis,
    assess_model_parity,
    build_database_blueprint,
    build_origin_packet,
    classify_status,
    payload_echo_confirmed,
    validate_payload_envelope,
)

__all__ = [
    "CHTP_VERSION",
    "CHTP_TLP_COMPATIBILITY",
    "FoundationAttack",
    "FoundationDisclosure",
    "HarnessProfile",
    "ModelDelta",
    "Phase",
    "TriangulationDossier",
    "TriangulationSession",
    "VCLAltitude",
    "VCLDiagnosis",
    "assess_model_parity",
    "build_database_blueprint",
    "build_origin_packet",
    "classify_status",
    "payload_echo_confirmed",
    "validate_payload_envelope",
]
