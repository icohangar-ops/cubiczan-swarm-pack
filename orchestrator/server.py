"""
Orchestrator API Server — Exposes the hybrid coordinator via Flask REST API.
Port: 5002
"""

import os
import uuid
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("cubiczan.server")

app = Flask(__name__)
CORS(app)

# Lazy initialization to avoid import errors during Docker build
_coordinator = None
_policy_gate = None


def get_coordinator():
    global _coordinator
    if _coordinator is None:
        from hybrid_coordinator import HybridCoordinator
        _coordinator = HybridCoordinator(db_path="cubiczan_swarm.db")
    return _coordinator


def get_policy_gate():
    global _policy_gate
    if _policy_gate is None:
        try:
            from governance import build_default_policy_gate
        except ImportError:
            from .governance import build_default_policy_gate

        audit_path = os.getenv("GOVERNANCE_AUDIT_LOG", "audit/governance.jsonl")
        hmac_key = os.getenv("GOVERNANCE_HMAC_KEY") or None
        _policy_gate = build_default_policy_gate(audit_path=audit_path, hmac_key=hmac_key)
    return _policy_gate


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "cubiczan-orchestrator"})


@app.route("/api/swarm/governance/evaluate", methods=["POST"])
def evaluate_governance_policy():
    """Evaluate a proposed agent action before execution."""
    data = request.get_json() or {}
    tool = data.get("tool", "swarm.execute")
    action = data.get("action", "execute")
    actor = data.get("actor", "unknown-agent")

    decision = get_policy_gate().evaluate(
        tool=tool,
        actor=actor,
        action=action,
        intent=data.get("intent", ""),
        evidence=data.get("evidence") or {},
        approved_by_human=bool(data.get("approved_by_human", False)),
        approval_id=data.get("approval_id"),
    )
    status = 200 if decision.allowed else 202 if decision.requires_approval else 403
    return jsonify(decision.to_dict()), status


@app.route("/api/swarm/governance/audit/verify", methods=["GET"])
def verify_governance_audit():
    """Verify the tamper-evident governance audit chain."""
    gate = get_policy_gate()
    if not gate.audit_kernel:
        return jsonify({"valid": True, "event_count": 0, "last_hash": "", "error": ""})
    return jsonify(gate.audit_kernel.verify_chain().to_dict())


@app.route("/api/swarm/execute", methods=["POST"])
def execute_task():
    """
    Execute a task through the hybrid coordinator.

    POST body:
    {
        "task": "Analyze the cybersecurity risk of acquiring CompanyX",
        "task_id": "optional-custom-id"
    }

    Response: Full execution metrics including results, PARL reward,
    coordination tokens (always 0), and wall time.
    """
    data = request.get_json()
    task = data.get("task", "")
    task_id = data.get("task_id", f"task-{str(uuid.uuid4())[:8]}")

    if not task:
        return jsonify({"error": "Missing 'task' field"}), 400

    try:
        decision = get_policy_gate().evaluate(
            tool="swarm.execute",
            actor=data.get("actor", "api-client"),
            action="execute",
            intent=task,
            evidence=data.get("evidence") or {},
            approved_by_human=bool(data.get("approved_by_human", False)),
            approval_id=data.get("approval_id"),
        )
        if not decision.allowed:
            status = 202 if decision.requires_approval else 403
            return jsonify({"governance": decision.to_dict()}), status

        coordinator = get_coordinator()
        result = coordinator.execute(task=task, task_id=task_id)
        result["governance"] = decision.to_dict()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/swarm/domains", methods=["GET"])
def list_domains():
    """List active domains and their configurations."""
    import json
    domains_dir = os.path.join(os.path.dirname(__file__), "..", "domains")
    active = os.getenv("ACTIVE_DOMAINS", "financial,cybersecurity,business-intel")
    active_set = {d.strip() for d in active.split(",")}

    domain_configs = {}
    if os.path.isdir(domains_dir):
        for name in os.listdir(domains_dir):
            config_path = os.path.join(domains_dir, name, "swarm_config.json")
            if os.path.isfile(config_path):
                with open(config_path) as f:
                    config = json.load(f)
                    config["active"] = name in active_set or config.get("domain", name) in active_set
                    domain_configs[name] = config

    return jsonify(domain_configs)


@app.route("/api/swarm/scent/<task_id>", methods=["GET"])
def read_scent(task_id: str):
    """Read current scent field signals for a task (debugging/monitoring)."""
    coordinator = get_coordinator()
    signals = coordinator.scent_field.read_all_for_task(task_id)
    return jsonify({
        st.value: round(val, 4) for st, val in signals.items()
    })


@app.route("/api/swarm/stats", methods=["GET"])
def swarm_stats():
    """Get overall swarm statistics."""
    coordinator = get_coordinator()
    active_domains = os.getenv("ACTIVE_DOMAINS", "financial,cybersecurity,business-intel")
    return jsonify({
        "active_domains": active_domains.split(","),
        "worker_count": len(coordinator.workers),
        "worker_models": [w.config.model_name for w in coordinator.workers],
        "coordination_protocol": "stigmergy",
        "coordination_tokens_per_task": 0,
    })


def get_solana_cli():
    try:
        from solana_cli import SolanaCLI
    except ImportError:
        from .solana_cli import SolanaCLI
    return SolanaCLI()


@app.route("/api/swarm/solana/plan", methods=["POST"])
def solana_plan():
    """Plan a guarded Solana CLI command without executing it."""
    data = request.get_json() or {}
    args = data.get("args", [])
    if not isinstance(args, list):
        return jsonify({"error": "'args' must be a list of Solana CLI arguments"}), 400

    client = get_solana_cli()
    plan = client.plan(
        args=args,
        cluster=data.get("cluster", "devnet"),
        approved_by_human=bool(data.get("approved_by_human", False)),
        approval_id=data.get("approval_id"),
    )
    return jsonify(plan.to_dict())


@app.route("/api/swarm/solana/execute", methods=["POST"])
def solana_execute():
    """Execute a guarded Solana CLI command; dry_run defaults to true."""
    data = request.get_json() or {}
    args = data.get("args", [])
    if not isinstance(args, list):
        return jsonify({"error": "'args' must be a list of Solana CLI arguments"}), 400

    client = get_solana_cli()
    result = client.execute(
        args=args,
        cluster=data.get("cluster", "devnet"),
        approved_by_human=bool(data.get("approved_by_human", False)),
        approval_id=data.get("approval_id"),
        dry_run=bool(data.get("dry_run", True)),
    )
    status = 200 if result.plan.allowed else 403
    return jsonify(result.to_dict()), status


if __name__ == "__main__":
    port = int(os.getenv("ORCHESTRATOR_PORT", "5002"))
    app.run(host="0.0.0.0", port=port, debug=False)
