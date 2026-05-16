# Cross-Harness Scaffolder

Cross-Harness Scaffolder v1.0.0 is a software-engineering layer that leverages the strengths of different AI harnesses to build efficient code. It adapts Cubiczan's canonical Consensus Hardening Protocol and TLP pattern for structured AI-to-AI validation across coding systems.

Canonical CHP source: [codeberg.org/cubiczan/consensus-hardening-protocol](https://codeberg.org/cubiczan/consensus-hardening-protocol)

It is designed for cases where one harness is strongest at implementation and local verification, while another is strongest at spec critique, long-form reasoning, or adversarial review. The goal is not model theater; it is less rework, lower token waste, stronger specs, and code that survives tests. A common pairing is:

- Codex as implementation harness: repo-local edits, tests, builds, migrations, packaging, and push discipline.
- Claude Code as spec/adversary harness: architecture critique, blind-spot attack, alternate framing, and partner-system review.

The protocol is origin-agnostic. Either harness can be Origin or Partner.

## Trigger Phrases

Use this protocol when the user mentions:

- triangulation
- TLP
- cross-AI validation
- Claude-to-Claude
- multi-model consensus
- convergence loop
- partner system packet
- foundation attack
- spec validation
- devil's advocate
- council spawn
- PAYLOAD markers
- VCL altitude diagnosis

## Why This Belongs In Cubiczan

Cubiczan already optimizes for token-efficient swarm work:

- zero-token stigmergic coordination for worker agents,
- adversarial consensus and anti-sycophancy checks,
- governance gates and audit evidence,
- heterogeneous model pools to reduce correlated failure.

Cross-Harness Scaffolder adds a higher-level harness scaffold so two coding systems can negotiate the spec before implementation, then verify the implementation against the locked spec. It turns harness differences into an engineering advantage: one system attacks the plan, one system patches the repo, and both leave a compact audit trail.

## Phase Architecture

```text
PHASE 0: R0 Gate + Foundation Attack
    |
    v
PHASE 1: Spec Convergence (Rounds 1-2)
    |
    v
PHASE 2: Implementation QA (Rounds 3-5)
```

Phase 1 must lock before implementation QA begins. Round 5 cannot remain provisional.

## Hard Gates

- Context check first: duplicate, related, or sparse.
- Model parity gate before session declaration.
- R0 gate: solvable, scoped, valid, worth it.
- Foundation score must be at least 70 percent.
- Partner payload must echo the payload marker.
- Standard partner response has exactly 7 sections.
- Origin response has exactly 3 sections.
- Third-party validation is required before LOCKED.
- VCL diagnosis is required for each decision item.
- Single winner; no ties.
- ASCII only.

## Model Parity

The module infers model tiers from model names and classifies deltas:

- NONE: same tier, proceed.
- MINOR: one-tier gap or unknown tier, proceed with advisory.
- SIGNIFICANT: two-tier or greater gap, halt unless the human explicitly accepts asymmetry as a structural constraint.

Use `assess_model_parity(origin_model, partner_model)`.

## Payload Integrity

Every packet is wrapped:

```text
BEGIN_PAYLOAD [RX] [6ALNUM]
...
END_PAYLOAD [RX] [6ALNUM]
```

Partner must return:

```text
PAYLOAD_ECHO: [RX] [6ALNUM] CONFIRMED
```

Use `validate_payload_envelope()` and `payload_echo_confirmed()`.

## Token-Efficient Database Architecture

Cross-Harness Scaffolder uses a normalized event store:

- `cross_harness_sessions`: one hot session row.
- `cross_harness_items`: compact per-decision state, agreement, VCL, flip criteria, third-party status.
- `cross_harness_payload_blobs`: content-addressed full packet body, stored once by hash.
- `cross_harness_round_events`: references payload hash plus compact state snapshot.
- `cross_harness_validations`: third-party lock validation trail.

This avoids copying long transcripts into every round. The hot path stores only state, hashes, status, and summaries. Large payload bodies can later move to object storage while the database keeps the content hash.

Use `build_database_blueprint()` to export the schema and scaling notes.

## Minimal Python Usage

```python
from orchestrator.cross_harness_scaffolder import (
    FoundationDisclosure,
    HarnessProfile,
    TriangulationDossier,
    TriangulationSession,
    VCLAltitude,
    VCLDiagnosis,
    build_origin_packet,
)

session = TriangulationSession(
    title="Validate token-efficient database architecture",
    origin=HarnessProfile(system="Codex", model="GPT-5.5", role="implementation_harness"),
    partner=HarnessProfile(system="Claude Code", model="Claude Opus 4.6", role="spec_adversary_harness"),
    human_bridge="Shyam",
    dossier=TriangulationDossier(
        core_problem="Validate whether the proposed event-store schema supports scalable cross-harness code review.",
        goal_state=(">=90% spec agreement", "third-party validation before LOCKED"),
        current_state=("Cubiczan has governance, anti-sycophancy, and CHP-adjacent modules.",),
        constraints=("Max five rounds", "ASCII payloads", "No full transcript duplication in hot state"),
        scope=("Protocol and schema only",),
        origin_direction=("Use content-addressed payload bodies", "Keep state snapshots compact"),
    ),
    foundation=FoundationDisclosure(
        weakest_assumptions=(
            "Two harnesses can maintain marker discipline across copy/paste.",
            "A compact state snapshot is enough to resume a session.",
        ),
        invalidation_conditions=(
            "Partner responses omit payload echo.",
            "Implementation begins before spec convergence.",
        ),
        key_vulnerability="False consensus caused by both models optimizing for agreement.",
    ),
    vcl=(
        VCLDiagnosis(
            item="database_architecture",
            symptom_altitude=VCLAltitude.R2_TASK,
            constraint_altitude=VCLAltitude.R4_SYSTEM,
            diagnosis="Schema mistakes are system-level; task-level fixes will not prevent replay drift.",
        ),
    ),
)

packet = build_origin_packet(session, payload_id="ABC123")
print(packet)
```

## Operating Split: Codex Versus Claude Code

Use Codex when the next step is:

- patching files,
- running tests,
- validating migrations,
- building artifacts,
- packaging and pushing changes.

Use Claude Code or another partner harness when the next step is:

- attacking assumptions,
- reviewing spec ambiguity,
- finding blind spots,
- comparing implementation options,
- acting as a third-party validator.

Do not let either system self-certify a lock. LOCKED requires third-party confirmation.

## Attribution

This protocol adapts Cubiczan's canonical Consensus Hardening Protocol from [codeberg.org/cubiczan/consensus-hardening-protocol](https://codeberg.org/cubiczan/consensus-hardening-protocol), including the `src/cme/chp/*` primitives for parity, R0/foundation gates, payload integrity, VCL diagnosis, lock progression, and third-party validation.

It also incorporates the user's TLP v2.2.4 / origin-agnostic AI convergence protocol for cross-model triangulation with adversarial foundation validation.

It also aligns with the repository's existing governance and anti-sycophancy layers:

- `orchestrator/governance.py`
- `orchestrator/anti_sycophancy.py`
- `orchestrator/consensus.py`

No external source code is vendored.
