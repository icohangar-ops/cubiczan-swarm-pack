# CUBICZAN Agent Swarm Intelligence Platform — SpaceTimeDB Edition

<p align="center">
  <img src="https://img.shields.io/badge/Coordination-Zero_Token-green" alt="Zero Token" />
  <img src="https://img.shields.io/badge/Speed-5.86x_Faster-blue" alt="5.86x Faster" />
  <img src="https://img.shields.io/badge/Cost-3.4x_Cheaper-green" alt="3.4x Cheaper" />
  <img src="https://img.shields.io/badge/Domains-9_Enterprise-orange" alt="9 Domains" />
  <img src="https://img.shields.io/badge/Backend-SpaceTimeDB-purple" alt="SpaceTimeDB" />
  <img src="https://img.shields.io/badge/License-AGPL--3.0-blue" alt="AGPL-3.0" />
</p>

> **SpaceTimeDB DevSpot Submission** — A fork of [cubiczan-swarm-pack](https://github.com/cubiczan/cubiczan-swarm-pack), migrated from SQLite + Flask to [SpaceTimeDB](https://spacetimedb.com/) for real-time, serverless coordination with zero-polling WebSocket subscriptions.

---

## Demo

https://github.com/user-attachments/assets/demo.mp4

> _Generated with [demo-video-generator](https://github.com/zan-maker/demo-video-generator)_
> Zero-token coordination. Heterogeneous agents. Enterprise-grade swarm intelligence.
> Now with real-time reactive state via SpaceTimeDB.

Built on [MiroFish](https://github.com/666ghj/MiroFish) (AGPL-3.0) swarm simulation + [TEMM1E](https://github.com/nagisanzenin/temm1e) (MIT) stigmergic coordination + [Kimi K2.5 PARL](https://arxiv.org/abs/2602.02276) parallel agent architecture + [SpaceTimeDB](https://spacetimedb.com/) real-time database.

---

## SpaceTimeDB Integration

This fork replaces the original SQLite + Flask architecture with SpaceTimeDB, a **hosted, real-time relational database** that exposes state changes as subscribable WebSocket events. This is not a wrapper or an ORM shim — the entire coordination layer runs as compiled Rust reducers inside the SpaceTimeDB runtime.

### What Changed

| Aspect | Original (SQLite + Flask) | SpaceTimeDB Edition |
|--------|--------------------------|---------------------|
| **State Store** | SQLite (polling via Flask API) | SpaceTimeDB tables (reactive subscriptions) |
| **Backend API** | Flask REST endpoints | SpaceTimeDB reducers (called directly by clients) |
| **Coordination** | HTTP polling → Python orchestrator | WebSocket subscribe → reducer invocation |
| **Pheromone Field** | SQLite `scent_signals` table | SpaceTimeDB `ScentSignal` table (real-time inserts stream to subscribers) |
| **Task Claiming** | `UPDATE ... WHERE status='ready'` (atomic SQL) | `claim_task` reducer (atomic STDB row mutation) |
| **Polling Overhead** | Clients poll every 1–5 seconds | **Zero polling** — changes push via WebSocket |

### How It Works

1. **Clients connect** to SpaceTimeDB via the `spacetimedb` SDK (`ws://host/db`)
2. **Clients subscribe** to tables: `SELECT * FROM Task`, `SELECT * FROM ScentSignal`, etc.
3. **Any connected client** can invoke a reducer (e.g., `claim_task(task_id, worker_id)`) — SpaceTimeDB executes it atomically on the server
4. **All subscribers** receive row-level insert/update/delete events instantly
5. **Pheromone signals** are rows in `ScentSignal` — workers emit by inserting, read by aggregating subscribed rows
6. **Zero Flask. Zero polling. Zero coordination tokens.**

---

## Why This Exists

Every major multi-agent framework (AutoGen, CrewAI, LangGraph) coordinates agents by making them **talk to each other**. Every coordination message is an LLM call. Every LLM call costs tokens. In complex workflows, the coordination overhead can **exceed the actual work**.

**This is an architecture bug, not a feature.**

Cubiczan replaces inter-agent LLM chat with **stigmergy** — indirect communication via environmental signals (scent pheromones), the same mechanism ant colonies use to solve NP-hard routing problems without centralized control.

### The Math That Matters

| Metric | Traditional (AutoGen/CrewAI) | Cubiczan Hybrid |
|--------|------------------------------|-----------------|
| 12-subtask coordination tokens | ~78 LLM calls | **0 coordination calls** |
| Context growth per subtask | **28x** (quadratic: h̄·m(m+1)/2) | **~190 bytes flat** (linear) |
| Speed (12 independent tasks) | 103s | **18s (5.86x faster)** |
| Cost (12 independent tasks) | 7,379 tokens | **2,149 tokens (3.4x cheaper)** |
| Simple task overhead | Framework boot cost | **Zero. Invisible.** |

---

## Architecture: 3-Layer Hybrid

```
  REQUEST
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Layer 1: MoE ROUTER (1 nano LLM call)                      │
│  Classifies domain + complexity. Simple tasks → single agent │
│  Complex tasks (3+ deliverables, speedup ≥1.3x) → swarm     │
└────────────────────────┬─────────────────────────────────────┘
                         │ (complex only)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Layer 2: ALPHA DECOMPOSITION (1 LLM call → DAG)            │
│  Kahn's topological sort, critical path optimization         │
│  Produces dependency graph with tagged subtasks               │
└────────────────────────┬─────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Worker 1   │ │   Worker 2   │ │   Worker 3   │   Heterogeneous
│  Qwen-2.5    │ │  DeepSeek-R1 │ │  Llama-3.3   │   models (frozen)
│  ┌────────┐  │ │  ┌────────┐  │ │  ┌────────┐  │
│  │STIGMERGY│ │ │  │STIGMERGY│ │ │  │STIGMERGY│ │   Zero-token
│  │ Claim   │  │ │  │ Claim   │  │ │  │ Claim   │  │   coordination
│  │ Emit    │  │ │  │ Emit    │  │ │  │ Emit    │  │
│  │ Read    │  │ │  │ Read    │  │ │  │ Read    │  │
│  └────────┘  │ │  └────────┘  │ │  └────────┘  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
              ┌──────────────────┐
              │  SCENT FIELD     │  SpaceTimeDB ScentSignal table
              │  6 signal types  │  Exponential decay, GC via reducer
              │  Task selection: │  S = A^2.0 · U^1.5 · (1-D)^1.0
              │  Pure arithmetic │     · (1-F)^0.8 · R^1.2
              │  Zero LLM calls │
              └──────────────────┘
                        │
                        ▼ (if high-stakes)
              ┌──────────────────┐
              │ CONSENSUS ENGINE │  Adversarial debate + LMSR scoring
              │ Anti-sycophancy  │  Contrarian agent stress-testing
              │ Heterogeneous    │  Min 2 distinct model families
              └──────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  PARL REWARD     │  rPARL = λ1·r_parallel + λ2·r_finish + r_perf
              │  (Kimi K2.5)     │  Prevents serial collapse + over-decomposition
              └──────────────────┘
```

### Stigmergy: How Workers Coordinate Without Talking

```
Worker 1 completes Task A → emits COMPLETION scent (5 min half-life)
Worker 2 reads scent field → sees Task B now has all deps met
Worker 2 claims Task B via claim_task reducer (atomic STDB mutation)
Worker 3 struggles on Task C → emits DIFFICULTY scent (2 min half-life)
Worker 4 reads field → avoids Task C, picks Task D instead (higher score)

Zero LLM calls. Zero coordination tokens. Pure arithmetic. Zero polling.
```

**6 Scent Signal Types:**

| Signal | Half-Life | Purpose |
|--------|-----------|---------|
| `COMPLETION` | 5 min | Task finished |
| `FAILURE` | 6 min | Attempt failed |
| `DIFFICULTY` | 2 min | Worker struggling |
| `URGENCY` | Grows (cap 5.0) | Prevents starvation |
| `PROGRESS` | 20 sec | Worker heartbeat |
| `HELP_WANTED` | 2 min | Specialist needed |

**Task Selection Formula** (40 lines of arithmetic, not an LLM call):
```
S(worker, task) = Affinity^2.0 × Urgency^1.5 × (1-Difficulty)^1.0
                  × (1-Failure)^0.8 × Reward^1.2
```

---

## SpaceTimeDB Schema

All state lives in 8 SpaceTimeDB tables. The dashboard client subscribes to each via SQL queries and receives real-time row events over WebSocket.

### Tables

| Table | Columns | Purpose |
|-------|---------|---------|
| **Worker** | `worker_id`, `display_name`, `model_name`, `tags[]`, `domain`, `is_online`, `connected_at`, `last_heartbeat` | Registered agent instances |
| **Task** | `task_id`, `graph_id`, `status`, `description`, `agent_type`, `tags[]`, `dependencies[]`, `worker_id`, `result`, `retries`, `reward`, `created_at`, `started_at`, `completed_at` | DAG task nodes with lifecycle |
| **ScentSignal** | `signal_id`, `task_id`, `worker_id`, `scent_type`, `intensity`, `emitted_at`, `metadata` | Pheromone signals (6 scent types) |
| **ConsensusVote** | `vote_id`, `round_id`, `task_id`, `agent_id`, `model_name`, `position`, `confidence`, `reasoning`, `is_contrarian`, `voted_at` | Individual consensus votes |
| **ConsensusResult** | `round_id`, `task_id`, `final_position`, `consensus_score`, `debate_rounds`, `escalate_to_human`, `heterogeneity_score`, `total_votes`, `dissenting_count`, `computed_at` | Aggregated consensus outcome |
| **AuditEvent** | `event_id`, `actor`, `action`, `resource`, `payload`, `decision`, `policy_id`, `previous_hash`, `hash`, `timestamp` | Tamper-evident audit chain (HMAC-SHA256) |
| **SwarmSession** | `session_id`, `graph_id`, `domain`, `task_description`, `total_tasks`, `completed_tasks`, `failed_tasks`, `agents_used`, `status`, `parl_reward`, `theoretical_speedup`, `started_at`, `completed_at` | Session-level tracking |
| **Policy** | `policy_id`, `tool`, `trust_level`, `max_calls`, `window_seconds`, `blocked_actions[]`, `approval_required_actions[]` | Governance policy rules |

### Key Enumerations

**Task Status State Machine:**
```
Pending → Ready → Active → Complete
                 Active → Retry → Ready (loop)
                 Active → Retry → Escalate (max retries)
                 Active → Blocked → Pending (unblock)
```

**Scent Types:** `Completion`, `Failure`, `Difficulty`, `Urgency`, `Progress`, `HelpWanted`

**Session Status:** `Initializing`, `Running`, `Paused`, `Completed`, `Failed`, `PartialSuccess`

**Policy Trust Levels:** `High`, `Medium`, `Low`, `Blocked`

---

## Reducers

SpaceTimeDB reducers are server-side functions that mutate tables atomically. Any connected client can invoke them — no Flask, no REST, no polling.

| # | Reducer | Description |
|---|---------|-------------|
| 1 | `register_worker` | Register a new agent instance into the swarm |
| 2 | `update_worker_heartbeat` | Update worker's last heartbeat timestamp |
| 3 | `unregister_worker` | Remove a worker from the swarm |
| 4 | `create_task` | Insert a new task into the DAG with dependencies |
| 5 | `activate_ready_tasks` | Transition tasks from Pending → Ready when deps are met |
| 6 | `claim_task` | Atomically claim a Ready task for a worker (Ready → Active) |
| 7 | `complete_task` | Mark a task complete with result payload (Active → Complete) |
| 8 | `fail_task` | Fail a task, retry or escalate based on retry count |
| 9 | `block_task` | Block a task (Active → Blocked) |
| 10 | `unblock_task` | Unblock a task (Blocked → Pending) |
| 11 | `emit_scent` | Insert a pheromone signal into the scent field |
| 12 | `decay_pheromones` | Decay expired scent signals (GC — removes signals below threshold) |
| 13 | `grow_urgency` | Increase urgency signals for long-waiting tasks (prevent starvation) |
| 14 | `cast_vote` | Submit a consensus vote for a task |
| 15 | `compute_consensus` | Aggregate votes via LMSR scoring, produce ConsensusResult |
| 16 | `record_audit` | Append a tamper-evident event to the audit chain (HMAC-SHA256 linked) |

---

## Supported Domains (9)

| # | Domain | Feasibility | Key Use Cases |
|---|--------|------------|---------------|
| 1 | **Financial Markets & Trading** | HIGH | Kalshi/Polymarket, commodities, crypto, M&A screening |
| 2 | **Business Intelligence** | HIGH | M&A targets, competitive scanning, multi-source synthesis |
| 3 | **Cybersecurity & Threat Intel** | HIGH | SOC triage (88-97% noise reduction), threat hunting |
| 4 | **Predictive Simulation** | HIGH | Social dynamics forecasting via MiroFish OASIS engine |
| 5 | **Content & Marketing** | MED-HIGH | 3-5x production speed, viral prediction, SEO |
| 6 | **Healthcare & Drug Discovery** | MEDIUM | Drug repurposing, clinical trial design, regulatory nav |
| 7 | **Political & Social Forecasting** | MEDIUM | Election prediction (Brier 0.101 → closing gap) |
| 8 | **Real Estate & Location Intel** | MEDIUM | Gentrification prediction, site selection, climate risk |
| 9 | **Talent & HR Intelligence** | MEDIUM | Hiring timing, retention signals, comp benchmarking |

---

## Open-Source Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Real-Time Database** | **SpaceTimeDB** | Hosted relational DB with WebSocket subscriptions + compiled Rust reducers |
| **Coordination Backend** | **SpaceTimeDB Reducers** | Atomic task claiming, scent emission, consensus, audit (replaces Flask) |
| **Client Transport** | **WebSocket Subscriptions** | Zero-polling real-time state sync (replaces HTTP polling) |
| **Simulation Engine** | MiroFish + OASIS (CAMEL-AI) | Multi-agent swarm simulation |
| **Coordination Logic** | Stigmergy (TEMM1E-inspired) | Zero-token pheromone signals |
| **Parallelism** | PARL (Kimi K2.5-inspired) | Dynamic decomposition + reward shaping |
| **Consensus** | LMSR + Contrarian Agents | Anti-sycophancy adversarial debate |
| **Governance Kernel** | PolicyGate + AuditKernel | Approval gates, HMAC-SHA256 audit chain |
| **LLM Backend** | Ollama / vLLM / llama.cpp | Self-hosted inference ($0 API cost) |
| **Models** | Qwen-2.5, DeepSeek-R1, Llama-3.3 | Heterogeneous pool (anti-groupthink) |
| **Dashboard Client** | Next.js 16 + TypeScript + Zustand | Real-time swarm monitoring UI |
| **Monitoring** | Grafana + Prometheus | Swarm health, cost, sycophancy alerts |

---

## Quick Start

```bash
# 1. Clone
git clone <this-repo>
cd swarm-pack-spacetimedb

# 2. Start SpaceTimeDB
spacetimedb start --host 0.0.0.0 --port 3000

# 3. Build and publish the Rust module
cd src/swarm_module
cargo build --release
spacetimedb publish --module-name swarm-module ./target/release/swarm_module.so

# 4. Start the dashboard client
cd ../../client
npm install
npm run dev

# 5. Open http://localhost:3001
```

> **Note:** The dashboard runs in demo/simulation mode when SpaceTimeDB is not connected, using the built-in mock-data simulation runner. No database or backend is required to preview the UI.

---

## Project Structure

```
swarm-pack-spacetimedb/
├── client/                        # Next.js 16 dashboard
│   ├── src/lib/types.ts           # STDB table type definitions
│   ├── src/lib/spacetime.ts       # WebSocket connection + subscriptions
│   ├── src/lib/store.ts           # Zustand state management
│   ├── src/lib/mock-data.ts       # Simulation runner (demo mode)
│   └── src/app/page.tsx           # Full dashboard UI
├── src/swarm_module/              # SpaceTimeDB Rust module
│   └── src/lib.rs                 # Tables + 16 reducers
└── README.md
```

---

## How It Compares

### vs. AutoGen / CrewAI / LangGraph

| Feature | AutoGen | CrewAI | LangGraph | **Cubiczan** | **Cubiczan + STDB** |
|---------|---------|--------|-----------|-------------|---------------------|
| Coordination | LLM-to-LLM chat | LLM delegation | Graph routing | **Stigmergy (0 tokens)** | **Stigmergy (0 tokens)** |
| Context growth | Quadratic | Quadratic | Linear (nodes) | **Flat (~190 bytes/worker)** | **Flat (~190 bytes/worker)** |
| Anti-sycophancy | None | None | None | **LMSR + contrarian + model diversity** | **LMSR + contrarian + model diversity** |
| Parallel execution | Sequential | Sequential default | Node-level | **Task-level (atomic SQLite)** | **Task-level (atomic STDB reducers)** |
| Simple task overhead | Framework boot | Framework boot | Framework boot | **Zero. Invisible.** | **Zero. Invisible.** |
| Real-time updates | Polling | Polling | Polling | HTTP polling | **WebSocket push (zero polling)** |
| Domain specialization | Manual | Role-based | Manual | **9 pre-built enterprise domains** | **9 pre-built enterprise domains** |
| Simulation engine | None | None | None | **MiroFish OASIS (33K+ stars)** | **MiroFish OASIS (33K+ stars)** |

### vs. TEMM1E (direct)

| Feature | TEMM1E | **Cubiczan + STDB** |
|---------|--------|---------------------|
| Language | Rust (17 crates) | **Rust reducers + TypeScript client** |
| Coordination | Stigmergy | **Stigmergy + PARL + Consensus** |
| State store | In-memory | **SpaceTimeDB (persistent, distributed)** |
| Real-time sync | None | **WebSocket subscriptions** |
| Domain configs | Generic | **9 enterprise domain packs** |
| Simulation | None | **MiroFish parallel worlds** |
| Anti-sycophancy | N/A (single-model) | **Heterogeneous models + contrarian** |

### vs. Kimi K2.5 Agent Swarm (direct)

| Feature | Kimi K2.5 PARL | **Cubiczan + STDB** |
|---------|---------------|---------------------|
| Coordination tokens | Reduced | **Zero (stigmergy)** |
| Open source models | Kimi K2.5 only | **Any OpenAI-compatible** |
| Task selection | LLM-based | **Arithmetic (40 LOC formula)** |
| Real-time visibility | Logs | **Live WebSocket dashboard** |
| Deployment | Research | **SpaceTimeDB hosted + Docker** |
| Enterprise domains | None | **9 pre-configured domains** |

---

## Cost Estimates

| Configuration | Cloud API (Tiered) | DeepSeek-only | Self-hosted (Ollama) |
|---------------|--------------------|---------------|---------------------|
| 20 agents, hourly | ~$55/mo | ~$15/mo | Compute only |
| 20 agents, 5-min | ~$660/mo | ~$180/mo | Compute only |
| 50 agents, 5-min | ~$5,000/mo | ~$1,166/mo | Compute only |
| **Stigmergy savings** | **~3.4x cheaper** | **~3.4x cheaper** | **~3.4x fewer GPU-hours** |

---

## Key Research References

1. **MiroFish** — Swarm intelligence engine (33K+ GitHub stars). Parallel digital world simulation with OASIS.
2. **TEMM1E v3.0.0** — Stigmergic coordination. 5.86x faster, 3.4x cheaper than LLM-to-LLM chat. MIT licensed.
3. **Kimi K2.5 Agent Swarm** (arXiv:2602.02276) — PARL: trainable orchestrator + frozen subagents. 3-4.5x latency reduction.
4. **CONSENSAGENT** (ACL 2025) — Same-model agents converge sycophantically in 1-2 rounds. Heterogeneous models required.
5. **Google Research** — Centralized hub-and-spoke contains errors to 4.4x vs free-form multi-agent chat.
6. **SpaceTimeDB** — Real-time relational database with compiled module runtime. Rust reducers for atomic state transitions.

---

## License

- MiroFish core: AGPL-3.0
- TEMM1E stigmergy concepts: MIT
- Cubiczan extensions: AGPL-3.0
- Domain configurations: AGPL-3.0
- SpaceTimeDB integration: AGPL-3.0

---

## CHP Governance

This repository is hardened with the [Consensus Hardening Protocol (CHP)](https://codeberg.org/cubiczan/consensus-hardening-protocol), Cubiczan's decision-governance layer for multi-agent AI systems.

### Protocol Layers
- **R0 Gate**: All decisions must pass Solvable, Scoped, Valid, Worth_it checks
- **Foundation Disclosure**: 1-3 weakest assumptions, 1-2 invalidation conditions, 1 key vulnerability
- **Adversarial Layer**: Mandatory devil's advocate at Phase 0 and Round 3
- **State Machine**: EXPLORING → PROVISIONAL → PROVISIONAL_LOCK → LOCKED
- **Third-Party Validation**: Independent CONFIRM/REJECT before lock

### Domain Configuration
- **Category**: AI / Agents
- **Foundation Threshold**: 70
- **CFO Accuracy Guard**: Disabled

### Compliance Artifacts
| File | Purpose |
|------|---------|
| `.chp/STATE_MACHINE.md` | Decision state transitions |
| `.chp/R0_CONFIG.yaml` | Domain-calibrated thresholds |
| `.chp/ADVERSARIAL_PROMPTS.md` | Standardized challenge templates |
| `.chp/CHP_COMPLIANCE.md` | Compliance tracking & audit trail |

### CHP Version
cognitive-mesh-orchestrator 0.1.0 | [Protocol Docs](https://codeberg.org/cubiczan/consensus-hardening-protocol)
