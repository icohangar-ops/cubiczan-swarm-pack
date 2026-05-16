# Attributions And Open Source Research

This repository uses third-party research and open-source projects as design
references. Unless a file says otherwise, no source code from the projects below
has been copied into Cubiczan Swarm Pack. If future work vendors code, preserve
the upstream license, copyright notices, and commit SHA in this file.

## Implemented Design References

- [PAXECT-Interface/open-agentic](https://github.com/PAXECT-Interface/open-agentic)
  - Referenced for audit-first agent execution, fail-closed orchestration,
    evidence thresholds, and tamper-evident action chains.
  - Current Cubiczan use: `orchestrator/governance.py` implements a lightweight
    append-only audit chain and evidence-aware policy gate.
- [cordum-io/cordum](https://github.com/cordum-io/cordum)
  - Referenced for agent control-plane concepts: pre-execution policy checks,
    approval gates, audit trails, and framework-neutral governance.
  - Current Cubiczan use: policy decisions are exposed through
    `/api/swarm/governance/evaluate`.
- [pegasi-ai/reins](https://github.com/pegasi-ai/reins)
  - Referenced for intervention, AI monitoring, agent security, and
    human-in-the-loop safeguards.
  - Current Cubiczan use: policy gates include kill switches, approval-required
    actions, and rate budgets.
- [humanlayer/agentcontrolplane](https://github.com/humanlayer/agentcontrolplane)
  - Referenced for outer-loop agent scheduling and asynchronous approval
    control-plane ideas.
  - Current Cubiczan use: approval IDs can unlock supervised actions without
    giving autonomous agents unconditional permission.
- [open-multi-agent/open-multi-agent](https://github.com/open-multi-agent/open-multi-agent)
  - Referenced for goal-to-DAG orchestration, dependency-aware execution, and
    traceable synthesis.
  - Current Cubiczan use: `build_traceable_task_graph` validates external or
    template-generated task DAGs before execution.
- [EvoMap/awesome-agent-swarm](https://github.com/EvoMap/awesome-agent-swarm)
  - Referenced as an ecosystem map for positioning Cubiczan around governed,
    auditable swarm coordination.

## Existing Project Attributions

- [MiroFish](https://github.com/666ghj/MiroFish), AGPL-3.0: swarm simulation
  and OASIS-style multi-agent simulation reference.
- [TEMM1E](https://github.com/nagisanzenin/temm1e), MIT: stigmergic
  coordination and atomic task-claiming inspiration.
- Kimi K2.5 PARL research: parallel agent reward-shaping inspiration.
- Georgios Fradelos, PhD, "Finance-Grade Assurance for Agentic AI", local
  source `AI Governance papers/ssrn-6306980.pdf`: model heterogeneity and
  monoculture risk concepts.
- Georgios Fradelos, PhD, "The Honey Badger Management Framework for Human-AI
  Hybrid Organizations", local source `AI Governance papers/ssrn-6306679.pdf`:
  governance/audit role separation and operating cadence concepts.
- Solana Foundation documentation:
  - https://solana.com/docs/intro/installation
  - https://solana.com/docs/intro/installation/solana-cli-basics
  - https://solana.com/docs/intro/installation/anchor-cli-basics
  - https://solana.com/docs/intro/installation/surfpool-cli-basics
- Cubiczan Consensus Hardening Protocol:
  https://codeberg.org/cubiczan/consensus-hardening-protocol
  - Canonical design reference for parity checks, R0/foundation gates, payload
    envelopes, VCL diagnosis, third-party validation, lock progression, and
    triangulation runner concepts used by
    `orchestrator/cross_harness_scaffolder.py` and
    `docs/CROSS_HARNESS_SCAFFOLDER.md`.
  - The user's TLP v2.2.4 origin-agnostic convergence protocol provided the
    cross-harness packet contract and Codex/Claude Code operating split.

## Candidate Projects For Future Review

- [desplega-ai/agent-swarm](https://github.com/desplega-ai/agent-swarm)
- [fcn06/swarm](https://github.com/fcn06/swarm)
- [joewinke/jat](https://github.com/joewinke/jat)
- [agentscope-ai/HiClaw](https://github.com/agentscope-ai/HiClaw)
- [ChristianAlmurr/openclaw-dashboard](https://github.com/ChristianAlmurr/openclaw-dashboard)
- [clawfleet/ClawFleet](https://github.com/clawfleet/ClawFleet)

Review licensing and implementation details before any code reuse.
