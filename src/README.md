# Swarm Intelligence Coordination Module

A [SpaceTimeDB](https://spacetimedb.com/) module that provides real-time, replicated tables and reducers for a swarm intelligence coordination platform. The module defines the shared data layer that multiple AI agent workers subscribe to for coordinated task execution, pheromone-based stigmergy, multi-model consensus, and tamper-evident governance auditing.

## Prerequisites

- [Rust](https://rustup.rs/) (edition 2021)
- [SpaceTimeDB CLI](https://docs.spacetimedb.com/) (`cargo install spacetimedb-cli` or per-platform installer)

## Compiling

From this directory (`src/swarm_module/`):

```bash
cargo build --release
```

> **Note:** The `spacetimedb` crate version must match the server you deploy against. If the crate version `1.0.0` is unavailable, adjust `Cargo.toml` to the latest compatible version.

## Running Locally

Start a local SpaceTimeDB instance that loads this module:

```bash
spacetimedb start --host 0.0.0.0 --port 3000
```

The server will expose:
- **WebSocket** on port 3000 for client subscriptions and reducer calls.
- **HTTP** on port 3000 for REST-style queries.

## How the Client Connects

The Next.js frontend uses the `@spacetimedb/client` SDK (or the generated TypeScript bindings) to:

1. **Connect** to the SpaceTimeDB instance via WebSocket:
   ```ts
   import { connect } from '@spacetimedb/client';
   const db = await connect('ws://localhost:3000');
   ```

2. **Subscribe** to tables — any insert/update/delete triggers a real-time callback:
   ```ts
   db.subscribe([
     { tableName: 'Worker' },
     { tableName: 'Task' },
     { tableName: 'ScentSignal' },
   ], (ctx) => {
     console.log('Workers:', ctx.db.worker.iter());
     console.log('Tasks:', ctx.db.task.iter());
   });
   ```

3. **Call reducers** to mutate state:
   ```ts
   db.registerWorker('w1', 'GPT-4o', 'OpenAI', ['code'], 'engineering');
   db.emitScent('sig1', 't1', 'w1', 'Urgency', 3.5, '');
   ```

## Module Architecture

### Tables (8)

| Table | Purpose |
|---|---|
| `Worker` | Online/offline agent workers |
| `Task` | Dependency-DAG tasks with status lifecycle |
| `ScentSignal` | Pheromone intensity field (stigmergy) |
| `SwarmSession` | Top-level session metadata and metrics |
| `ConsensusVote` | Per-agent votes in a debate round |
| `ConsensusResult` | Aggregated consensus outcome |
| `AuditEvent` | Hash-chained tamper-evident log |
| `Policy` | Governance policy rules |

### Reducers (16)

| Reducer | Description |
|---|---|
| `register_worker` | Bring a worker online |
| `unregister_worker` | Take a worker offline |
| `heartbeat` | Liveness ping |
| `create_session` | Initialize a swarm run |
| `start_session` | Transition to "Running" |
| `add_task` | Insert a task into the DAG |
| `claim_task` | Assign a task to a worker |
| `complete_task` | Finish a task; promote dependents |
| `fail_task` | Record failure; increment retries |
| `emit_scent` | Publish a pheromone signal |
| `cast_vote` | Submit a consensus vote |
| `compute_consensus` | Aggregate votes → result |
| `complete_session` | Finalize session metrics |
| `log_audit` | Append to the audit chain |
| `decay_scents` | Evaporate old pheromone signals |
| `grow_urgency` | Increase urgency scent for a task |
