# Governed Swarm Controls

Cubiczan now includes a small governance kernel around the swarm runtime. The
goal is to keep autonomous coordination fast while making external actions,
high-risk actions, and weak-evidence decisions fail closed.

## Components

### Audit Kernel

`orchestrator/governance.py` provides `AuditKernel`, an append-only JSONL audit
chain.

- Every event records `previous_hash`.
- Every event receives a SHA-256 hash over a canonical JSON body.
- If `GOVERNANCE_HMAC_KEY` is set, the event hash uses HMAC-SHA256 and records
  only a short `key_id`.
- `/api/swarm/governance/audit/verify` validates the full chain.

This is inspired by audit-first agent frameworks such as
[open-agentic](https://github.com/PAXECT-Interface/open-agentic), but the
implementation is local and intentionally small.

### Policy Gate

`PolicyGate` evaluates proposed actions before execution.

It checks:

- Trust level: autonomous, supervised, or approval required.
- Explicit blocked actions.
- Approval-required actions.
- Evidence thresholds.
- Per-tool rate budgets.
- Kill switches for paused tools.

Default protected action categories:

- External communications: `publish_post`, `send_email`,
  `send_client_message`.
- Financial actions: `send_money`, `external_purchase`.
- Legal actions: `sign_contract`.
- Irreversible actions: `delete_data`, `deploy_mainnet`, and related variants.

### Evidence Gate

`EvidenceRequirement` makes the gate fail closed when an action does not provide
enough sources, coverage, or required evidence fields.

Example:

```python
EvidenceRequirement(min_sources=2, min_coverage=0.75)
```

This blocks even human-approved requests if the evidence payload is too weak.
That is deliberate: approval should review a complete decision package, not
rubber-stamp an empty one.

### Traceable DAG Builder

`build_traceable_task_graph` turns deterministic task specs into a validated
`TaskGraph`.

It verifies:

- All dependencies exist.
- The graph has no cycles.
- Dependents are populated.
- Critical path and theoretical speedup are computed before worker execution.

This supports task planners, department templates, or future self-spawning
modules that produce DAGs without relying on a new LLM call.

## API

Evaluate a proposed action:

```bash
curl -X POST http://localhost:5002/api/swarm/governance/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "external.communication",
    "actor": "content-agent",
    "action": "publish_post",
    "intent": "Publish a LinkedIn update"
  }'
```

Expected outcome: `require_approval`.

Approve and rerun:

```bash
curl -X POST http://localhost:5002/api/swarm/governance/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "external.communication",
    "actor": "content-agent",
    "action": "publish_post",
    "intent": "Publish a LinkedIn update",
    "approved_by_human": true,
    "approval_id": "approval-123"
  }'
```

Verify the audit chain:

```bash
curl http://localhost:5002/api/swarm/governance/audit/verify
```

## Environment

```env
GOVERNANCE_AUDIT_LOG=audit/governance.jsonl
GOVERNANCE_HMAC_KEY=
```

In production, load `GOVERNANCE_HMAC_KEY` from a vault or operator-managed
secret store. Do not commit it to Git.

## Test Coverage

The governance tests cover:

- Heterogeneity scoring.
- Audit-chain tamper detection.
- Approval-required external communications.
- Evidence-threshold fail-closed behavior.
- Rate budget enforcement.
- Deterministic DAG validation and cycle detection.
