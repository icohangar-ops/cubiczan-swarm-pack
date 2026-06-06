use spacetimedb::ReducerContext;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn now_millis() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_millis() as u64
}

// ---------------------------------------------------------------------------
// Table definitions
// ---------------------------------------------------------------------------

/// Workers coordinating in the swarm.
#[spacetimedb::table(name = worker, public)]
pub struct Worker {
    #[primarykey]
    pub worker_id: String,
    pub display_name: String,
    pub model_name: String,
    pub tags: Vec<String>,
    pub domain: String,
    #[index(name = "idx_worker_online")]
    pub is_online: bool,
    pub connected_at: u64,
    pub last_heartbeat: u64,
}

/// Tasks in the dependency DAG.
#[spacetimedb::table(name = task, public)]
pub struct Task {
    #[primarykey]
    pub task_id: String,
    #[index(name = "idx_task_graph")]
    pub graph_id: String,
    pub status: String, // Pending | Ready | Active | Complete | Failed | Escalate
    pub description: String,
    pub agent_type: String,
    pub tags: Vec<String>,
    pub dependencies: Vec<String>,
    pub worker_id: String,
    pub result: String,
    pub retries: u32,
    pub reward: f64,
    pub created_at: u64,
    pub started_at: u64,
    pub completed_at: u64,
}

/// Pheromone signals in the scent field.
#[spacetimedb::table(name = scent_signal, public)]
pub struct ScentSignal {
    #[primarykey]
    pub signal_id: String,
    #[index(name = "idx_scent_task")]
    pub task_id: String,
    pub worker_id: String,
    #[index(name = "idx_scent_type")]
    pub scent_type: String, // Completion | Failure | Difficulty | Urgency | Progress | HelpWanted
    pub intensity: f64,
    pub emitted_at: u64,
    pub metadata: String,
}

/// Overall swarm session.
#[spacetimedb::table(name = swarm_session, public)]
pub struct SwarmSession {
    #[primarykey]
    pub session_id: String,
    pub graph_id: String,
    pub domain: String,
    pub task_description: String,
    pub total_tasks: u32,
    pub completed_tasks: u32,
    pub failed_tasks: u32,
    pub agents_used: u32,
    pub status: String,
    pub parl_reward: f64,
    pub theoretical_speedup: f64,
    pub started_at: u64,
    pub completed_at: u64,
}

/// Individual votes in consensus rounds.
#[spacetimedb::table(name = consensus_vote, public)]
pub struct ConsensusVote {
    #[primarykey]
    pub vote_id: String,
    #[index(name = "idx_vote_round")]
    pub round_id: String,
    pub task_id: String,
    pub agent_id: String,
    pub model_name: String,
    pub position: String,
    pub confidence: f64,
    pub reasoning: String,
    pub is_contrarian: bool,
    pub voted_at: u64,
}

/// Computed consensus outcome.
#[spacetimedb::table(name = consensus_result, public)]
pub struct ConsensusResult {
    #[primarykey]
    pub round_id: String,
    pub task_id: String,
    pub final_position: String,
    pub consensus_score: f64,
    pub debate_rounds: u32,
    pub escalate_to_human: bool,
    pub heterogeneity_score: f64,
    pub total_votes: u32,
    pub dissenting_count: u32,
    pub computed_at: u64,
}

/// Tamper-evident audit chain.
#[spacetimedb::table(name = audit_event, public)]
pub struct AuditEvent {
    #[primarykey]
    pub event_id: String,
    pub actor: String,
    pub action: String,
    pub resource: String,
    pub payload: String,
    pub decision: String, // ALLOW | DENY | ESCALATE
    pub policy_id: String,
    pub previous_hash: String,
    pub hash: String,
    pub timestamp: u64,
}

/// Governance policies.
#[spacetimedb::table(name = policy, public)]
pub struct Policy {
    #[primarykey]
    pub policy_id: String,
    pub tool: String,
    pub trust_level: String, // High | Medium | Low | Blocked
    pub max_calls: u32,
    pub window_seconds: u32,
    pub blocked_actions: Vec<String>,
    pub approval_required_actions: Vec<String>,
}

// ---------------------------------------------------------------------------
// Reducers
// ---------------------------------------------------------------------------

/// Register a new worker as online.
#[spacetimedb::reducer]
pub fn register_worker(
    ctx: &ReducerContext,
    worker_id: String,
    display_name: String,
    model_name: String,
    tags: Vec<String>,
    domain: String,
) {
    let now = now_millis();
    ctx.db.worker().insert(Worker {
        worker_id,
        display_name,
        model_name,
        tags,
        domain,
        is_online: true,
        connected_at: now,
        last_heartbeat: now,
    });
}

/// Mark a worker as offline.
#[spacetimedb::reducer]
pub fn unregister_worker(ctx: &ReducerContext, worker_id: String) {
    if let Some(mut worker) = ctx.db.worker().find_by_worker_id(&worker_id) {
        worker.is_online = false;
        ctx.db.worker().update(worker);
    }
}

/// Refresh a worker's heartbeat timestamp.
#[spacetimedb::reducer]
pub fn heartbeat(ctx: &ReducerContext, worker_id: String) {
    if let Some(mut worker) = ctx.db.worker().find_by_worker_id(&worker_id) {
        worker.last_heartbeat = now_millis();
        ctx.db.worker().update(worker);
    }
}

/// Create a new swarm session in "Initializing" state.
#[spacetimedb::reducer]
pub fn create_session(
    ctx: &ReducerContext,
    session_id: String,
    graph_id: String,
    domain: String,
    task_description: String,
    total_tasks: u32,
    agents_used: u32,
) {
    ctx.db.swarm_session().insert(SwarmSession {
        session_id,
        graph_id,
        domain,
        task_description,
        total_tasks,
        completed_tasks: 0,
        failed_tasks: 0,
        agents_used,
        status: "Initializing".to_string(),
        parl_reward: 0.0,
        theoretical_speedup: agents_used as f64 * 0.8,
        started_at: now_millis(),
        completed_at: 0,
    });
}

/// Transition a session from "Initializing" to "Running".
#[spacetimedb::reducer]
pub fn start_session(ctx: &ReducerContext, session_id: String) {
    if let Some(mut session) = ctx.db.swarm_session().find_by_session_id(&session_id) {
        session.status = "Running".to_string();
        ctx.db.swarm_session().update(session);
    }
}

/// Add a task to the DAG. Status is "Ready" if it has no dependencies, "Pending" otherwise.
#[spacetimedb::reducer]
pub fn add_task(
    ctx: &ReducerContext,
    task_id: String,
    graph_id: String,
    description: String,
    agent_type: String,
    tags: Vec<String>,
    dependencies: Vec<String>,
) {
    let status = if dependencies.is_empty() {
        "Ready".to_string()
    } else {
        "Pending".to_string()
    };

    ctx.db.task().insert(Task {
        task_id,
        graph_id,
        status,
        description,
        agent_type,
        tags,
        dependencies,
        worker_id: String::new(),
        result: String::new(),
        retries: 0,
        reward: 0.0,
        created_at: now_millis(),
        started_at: 0,
        completed_at: 0,
    });
}

/// Claim a task for a worker, transitioning it to "Active".
#[spacetimedb::reducer]
pub fn claim_task(ctx: &ReducerContext, task_id: String, worker_id: String) {
    if let Some(mut task) = ctx.db.task().find_by_task_id(&task_id) {
        task.status = "Active".to_string();
        task.worker_id = worker_id;
        task.started_at = now_millis();
        ctx.db.task().update(task);
    }
}

/// Mark a task as complete and promote any dependents whose deps are now all satisfied.
/// Also increments the session's completed_tasks counter.
#[spacetimedb::reducer]
pub fn complete_task(ctx: &ReducerContext, task_id: String, result: String, reward: f64) {
    let now = now_millis();
    let completed_task_id = task_id.clone();

    // Update the task itself.
    if let Some(mut task) = ctx.db.task().find_by_task_id(&task_id) {
        task.status = "Complete".to_string();
        task.result = result;
        task.reward = reward;
        task.completed_at = now;
        let graph_id = task.graph_id.clone();
        ctx.db.task().update(task);

        // Bump the session's completed_tasks counter.
        for mut session in ctx.db.swarm_session().iter() {
            if session.graph_id == graph_id {
                session.completed_tasks += 1;
                ctx.db.swarm_session().update(session);
                break;
            }
        }
    }

    // Promote dependents whose dependencies are now all satisfied.
    let dependents: Vec<Task> = ctx
        .db
        .task()
        .iter()
        .filter(|t| t.dependencies.contains(&completed_task_id))
        .collect();

    for mut dep in dependents {
        if dep.status != "Pending" {
            continue;
        }
        let all_deps_complete = dep.dependencies.iter().all(|dep_id| {
            ctx.db
                .task()
                .find_by_task_id(dep_id)
                .map(|t| t.status == "Complete")
                .unwrap_or(false)
        });
        if all_deps_complete {
            dep.status = "Ready".to_string();
            ctx.db.task().update(dep);
        }
    }
}

/// Mark a task as failed, increment its retry counter, and update the session counter.
#[spacetimedb::reducer]
pub fn fail_task(ctx: &ReducerContext, task_id: String, error_reason: String) {
    if let Some(mut task) = ctx.db.task().find_by_task_id(&task_id) {
        task.status = "Failed".to_string();
        task.retries += 1;
        task.result = error_reason;
        let graph_id = task.graph_id.clone();
        ctx.db.task().update(task);

        // Bump the session's failed_tasks counter.
        for mut session in ctx.db.swarm_session().iter() {
            if session.graph_id == graph_id {
                session.failed_tasks += 1;
                ctx.db.swarm_session().update(session);
                break;
            }
        }
    }
}

/// Emit a scent (pheromone) signal into the scent field.
#[spacetimedb::reducer]
pub fn emit_scent(
    ctx: &ReducerContext,
    signal_id: String,
    task_id: String,
    worker_id: String,
    scent_type: String,
    intensity: f64,
    metadata: String,
) {
    ctx.db.scent_signal().insert(ScentSignal {
        signal_id,
        task_id,
        worker_id,
        scent_type,
        intensity,
        emitted_at: now_millis(),
        metadata,
    });
}

/// Cast a vote in a consensus round.
#[spacetimedb::reducer]
pub fn cast_vote(
    ctx: &ReducerContext,
    vote_id: String,
    round_id: String,
    task_id: String,
    agent_id: String,
    model_name: String,
    position: String,
    confidence: f64,
    reasoning: String,
    is_contrarian: bool,
) {
    ctx.db.consensus_vote().insert(ConsensusVote {
        vote_id,
        round_id,
        task_id,
        agent_id,
        model_name,
        position,
        confidence,
        reasoning,
        is_contrarian,
        voted_at: now_millis(),
    });
}

/// Compute the final consensus result for a round, counting votes and dissenters.
#[spacetimedb::reducer]
pub fn compute_consensus(
    ctx: &ReducerContext,
    round_id: String,
    task_id: String,
    final_position: String,
    consensus_score: f64,
    debate_rounds: u32,
    escalate_to_human: bool,
    heterogeneity_score: f64,
) {
    let votes_for_round: Vec<&ConsensusVote> = ctx
        .db
        .consensus_vote()
        .iter()
        .filter(|v| v.round_id == round_id)
        .collect();

    let total_votes = votes_for_round.len() as u32;

    // A vote is "dissenting" if its position differs from the final_position.
    let dissenting_count = votes_for_round
        .iter()
        .filter(|v| v.position != final_position)
        .count() as u32;

    ctx.db.consensus_result().insert(ConsensusResult {
        round_id,
        task_id,
        final_position,
        consensus_score,
        debate_rounds,
        escalate_to_human,
        heterogeneity_score,
        total_votes,
        dissenting_count,
        computed_at: now_millis(),
    });
}

/// Mark a swarm session as completed and record the parl reward.
#[spacetimedb::reducer]
pub fn complete_session(ctx: &ReducerContext, session_id: String, parl_reward: f64) {
    if let Some(mut session) = ctx.db.swarm_session().find_by_session_id(&session_id) {
        session.status = "Completed".to_string();
        session.completed_at = now_millis();
        session.parl_reward = parl_reward;
        ctx.db.swarm_session().update(session);
    }
}

/// Log an audit event with a deterministic hash computed from the payload fields.
#[spacetimedb::reducer]
pub fn log_audit(
    ctx: &ReducerContext,
    event_id: String,
    actor: String,
    action: String,
    resource: String,
    payload: String,
    decision: String,
    policy_id: String,
    previous_hash: String,
) {
    // Simple deterministic hash for demonstration purposes.
    // In production this would use a real cryptographic hash (e.g. SHA-256).
    let hash = format!(
        "{:x}",
        actor.len() * action.len() * 1000 + payload.len()
    );

    ctx.db.audit_event().insert(AuditEvent {
        event_id,
        actor,
        action,
        resource,
        payload,
        decision,
        policy_id,
        previous_hash,
        hash,
        timestamp: now_millis(),
    });
}

/// Decay old scent signals by removing those older than `max_age_seconds`.
/// This is the pheromone evaporation mechanism.
#[spacetimedb::reducer]
pub fn decay_scents(ctx: &ReducerContext, max_age_seconds: u64) {
    let cutoff = now_millis() - (max_age_seconds * 1000);
    let stale: Vec<ScentSignal> = ctx
        .db
        .scent_signal()
        .iter()
        .filter(|s| s.emitted_at < cutoff)
        .collect();
    for s in stale {
        ctx.db.scent_signal().delete_by_signal_id(&s.signal_id);
    }
}

/// Grow the urgency scent for a task by an increment, capped at 5.0.
/// If no urgency scent exists for the task yet, one is created.
#[spacetimedb::reducer]
pub fn grow_urgency(ctx: &ReducerContext, task_id: String, increment: f64) {
    let now = now_millis();

    // Look for an existing urgency scent for this task.
    let mut found = false;
    for mut signal in ctx.db.scent_signal().iter() {
        if signal.task_id == task_id && signal.scent_type == "Urgency" {
            signal.intensity = (signal.intensity + increment).min(5.0);
            ctx.db.scent_signal().update(signal);
            found = true;
            break;
        }
    }

    // If none exists, create one.
    if !found {
        let signal_id = format!("urg-{}-{}", task_id, now);
        ctx.db.scent_signal().insert(ScentSignal {
            signal_id,
            task_id,
            worker_id: String::new(),
            scent_type: "Urgency".to_string(),
            intensity: increment.min(5.0),
            emitted_at: now,
            metadata: String::new(),
        });
    }
}
