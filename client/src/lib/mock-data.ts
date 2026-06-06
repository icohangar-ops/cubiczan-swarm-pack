import type {
  Worker,
  Task,
  ScentSignal,
  ConsensusVote,
  ConsensusResult,
  AuditEvent,
  SwarmSession,
  StreamEvent,
  ScentType,
} from "./types";

// UIDs
let _uid = 0;
const uid = () => String(++_uid);
const now = () => new Date().toISOString();

// ── Seed Workers ───────────────────────────────────────────────
export function seedWorkers(): Worker[] {
  const models = [
    { model: "GPT-4o", domain: "reasoning", tags: ["research", "analysis"] },
    { model: "Claude 3.5 Sonnet", domain: "coding", tags: ["implementation", "debugging"] },
    { model: "Llama 3 70B", domain: "general", tags: ["fast", "cost-effective"] },
    { model: "Mistral Large", domain: "economics", tags: ["financial", "quantitative"] },
  ];
  return models.map((m, i) => ({
    worker_id: uid(),
    display_name: `Agent-${i + 1}`,
    model_name: m.model,
    tags: m.tags,
    domain: m.domain,
    is_online: true,
    connected_at: now(),
    last_heartbeat: now(),
  }));
}

// ── Seed Swarm Session ───────────────────────────────────────
export function seedSwarmSession(
  sessionId: string,
  graphId: string
): SwarmSession {
  return {
    session_id: sessionId,
    graph_id: graphId,
    domain: "Financial Markets Analysis",
    task_description:
      "Comprehensive analysis of Q4 2024 financial markets: risk assessment, trend forecasting, portfolio optimization, and macro-economic indicators.",
    total_tasks: 8,
    completed_tasks: 0,
    failed_tasks: 0,
    agents_used: 4,
    status: "Initializing",
    parl_reward: 0,
    theoretical_speedup: 3.2,
    started_at: now(),
    completed_at: "",
  };
}

// ── Seed Tasks with dependency DAG ───────────────────────────
export function seedTasks(graphId: string): Task[] {
  const tasks: Task[] = [
    {
      task_id: uid(),
      graph_id: graphId,
      status: "Ready",
      description: "Gather macro-economic indicators (GDP, CPI, interest rates)",
      agent_type: "researcher",
      tags: ["data", "macro"],
      dependencies: [],
      worker_id: "",
      result: "",
      retries: 0,
      reward: 0,
      created_at: now(),
      started_at: "",
      completed_at: "",
    },
    {
      task_id: uid(),
      graph_id: graphId,
      status: "Ready",
      description: "Collect real-time market data feeds (S&P500, NASDAQ, bond yields)",
      agent_type: "researcher",
      tags: ["data", "market"],
      dependencies: [],
      worker_id: "",
      result: "",
      retries: 0,
      reward: 0,
      created_at: now(),
      started_at: "",
      completed_at: "",
    },
    {
      task_id: uid(),
      graph_id: graphId,
      status: "Pending",
      description: "Perform risk assessment on current portfolio positions",
      agent_type: "analyst",
      tags: ["risk", "quant"],
      dependencies: [], // will be set after creation
      worker_id: "",
      result: "",
      retries: 0,
      reward: 0,
      created_at: now(),
      started_at: "",
      completed_at: "",
    },
    {
      task_id: uid(),
      graph_id: graphId,
      status: "Pending",
      description: "Run trend forecasting models (ARIMA, LSTM predictions)",
      agent_type: "ml-engineer",
      tags: ["forecast", "ml"],
      dependencies: [],
      worker_id: "",
      result: "",
      retries: 0,
      reward: 0,
      created_at: now(),
      started_at: "",
      completed_at: "",
    },
    {
      task_id: uid(),
      graph_id: graphId,
      status: "Pending",
      description: "Analyze sector rotation patterns and sector ETF flows",
      agent_type: "analyst",
      tags: ["sector", "analysis"],
      dependencies: [],
      worker_id: "",
      result: "",
      retries: 0,
      reward: 0,
      created_at: now(),
      started_at: "",
      completed_at: "",
    },
    {
      task_id: uid(),
      graph_id: graphId,
      status: "Pending",
      description: "Generate sentiment analysis from financial news corpus",
      agent_type: "nlp-engineer",
      tags: ["sentiment", "nlp"],
      dependencies: [],
      worker_id: "",
      result: "",
      retries: 0,
      reward: 0,
      created_at: now(),
      started_at: "",
      completed_at: "",
    },
    {
      task_id: uid(),
      graph_id: graphId,
      status: "Pending",
      description: "Synthesize consensus: compile findings into investment thesis",
      agent_type: "coordinator",
      tags: ["synthesis", "final"],
      dependencies: [],
      worker_id: "",
      result: "",
      retries: 0,
      reward: 0,
      created_at: now(),
      started_at: "",
      completed_at: "",
    },
    {
      task_id: uid(),
      graph_id: graphId,
      status: "Pending",
      description: "Produce final report with recommendations and risk warnings",
      agent_type: "writer",
      tags: ["report", "output"],
      dependencies: [],
      worker_id: "",
      result: "",
      retries: 0,
      reward: 0,
      created_at: now(),
      started_at: "",
      completed_at: "",
    },
  ];

  // Set up DAG: 0,1 -> 2,3,4,5 -> 6 -> 7
  const t3 = tasks[2];
  t3.dependencies = [tasks[0].task_id, tasks[1].task_id];
  const t4 = tasks[3];
  t4.dependencies = [tasks[0].task_id, tasks[1].task_id];
  const t5 = tasks[4];
  t5.dependencies = [tasks[1].task_id];
  const t6 = tasks[5];
  t6.dependencies = [tasks[0].task_id];
  const t7 = tasks[6];
  t7.dependencies = [
    tasks[2].task_id,
    tasks[3].task_id,
    tasks[4].task_id,
    tasks[5].task_id,
  ];
  const t8 = tasks[7];
  t8.dependencies = [tasks[6].task_id];

  return tasks;
}

// ── Scent signal helper ──────────────────────────────────────
export function createScentSignal(
  taskId: string,
  workerId: string,
  scentType: ScentType,
  intensity: number,
  metadata: string = ""
): ScentSignal {
  return {
    signal_id: uid(),
    task_id: taskId,
    worker_id: workerId,
    scent_type: scentType,
    intensity,
    emitted_at: now(),
    metadata,
  };
}

// ── Consensus votes helper ───────────────────────────────────
export function seedConsensusVotes(
  roundId: string,
  taskId: string,
  workers: Worker[]
): ConsensusVote[] {
  const positions = [
    { pos: "BUY", conf: 0.82, reasoning: "Strong momentum indicators and positive earnings surprise", contrarian: false },
    { pos: "HOLD", conf: 0.65, reasoning: "Mixed signals from technical and fundamental analysis", contrarian: false },
    { pos: "BUY", conf: 0.71, reasoning: "Sector rotation favors this segment; FED dovish stance expected", contrarian: false },
    { pos: "SELL", conf: 0.58, reasoning: "Rising bond yields and inverted yield curve signal recession risk", contrarian: true },
  ];
  return workers.map((w, i) => ({
    vote_id: uid(),
    round_id: roundId,
    task_id: taskId,
    agent_id: w.worker_id,
    model_name: w.model_name,
    position: positions[i].pos,
    confidence: positions[i].conf,
    reasoning: positions[i].reasoning,
    is_contrarian: positions[i].contrarian,
    voted_at: now(),
  }));
}

// ── Consensus result helper ───────────────────────────────────
export function seedConsensusResult(
  roundId: string,
  taskId: string
): ConsensusResult {
  return {
    round_id: roundId,
    task_id: taskId,
    final_position: "BUY (Cautious)",
    consensus_score: 0.72,
    debate_rounds: 2,
    escalate_to_human: true,
    heterogeneity_score: 0.45,
    total_votes: 4,
    dissenting_count: 1,
    computed_at: now(),
  };
}

// ── Audit event helper ────────────────────────────────────────
export function createAuditEvent(
  actor: string,
  action: string,
  resource: string,
  payload: string,
  decision: string
): AuditEvent {
  const prevHash = Math.random().toString(36).slice(2, 10);
  const hash = Math.random().toString(36).slice(2, 14);
  return {
    event_id: uid(),
    actor,
    action,
    resource,
    payload,
    decision,
    policy_id: "pol-001",
    previous_hash: prevHash,
    hash,
    timestamp: now(),
  };
}

// ── Full simulation runner ───────────────────────────────────
export interface SimulationCallbacks {
  onWorkers: (workers: Worker[]) => void;
  onSession: (session: SwarmSession) => void;
  onTasks: (tasks: Task[]) => void;
  onSignals: (signals: ScentSignal[]) => void;
  onVotes: (votes: ConsensusVote[]) => void;
  onConsensus: (result: ConsensusResult) => void;
  onAudit: (event: AuditEvent) => void;
  onEvent: (event: StreamEvent) => void;
}

function delay(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export async function runSimulation(
  callbacks: SimulationCallbacks,
  signal: { aborted: boolean }
) {
  const emit = (
    type: StreamEvent["type"],
    msg: string,
    severity: StreamEvent["severity"] = "info"
  ) => {
    if (signal.aborted) return;
    callbacks.onEvent({
      id: uid(),
      timestamp: now(),
      type,
      message: msg,
      severity,
    });
  };

  // Reset uid counter for deterministic IDs
  _uid = 0;

  // 1. Register workers
  const workers = seedWorkers();
  emit("worker", `🌿 ${workers.length} workers registered`);
  for (const w of workers) {
    emit("worker", `  → ${w.display_name} (${w.model_name}) online`);
  }
  callbacks.onWorkers(workers);

  if (signal.aborted) return;
  await delay(600);

  // 2. Create swarm session
  const sessionId = uid();
  const graphId = uid();
  const session = seedSwarmSession(sessionId, graphId);
  session.status = "Running";
  emit("session", `🚀 Swarm session started: ${session.domain}`);
  callbacks.onSession(session);

  if (signal.aborted) return;
  await delay(400);

  // 3. Add tasks
  const tasks = seedTasks(graphId);
  emit("task", `📋 ${tasks.length} tasks added to DAG`);
  for (const t of tasks) {
    emit("task", `  → Task: ${t.description.slice(0, 60)}…`);
  }
  callbacks.onTasks(tasks);

  if (signal.aborted) return;
  await delay(400);

  // 4. Claim tasks T0 & T1 (Ready, no deps)
  const allSignals: ScentSignal[] = [];

  const claimTask = (taskIdx: number, workerIdx: number) => {
    const task = tasks[taskIdx];
    const worker = workers[workerIdx];
    task.status = "Active";
    task.worker_id = worker.worker_id;
    task.started_at = now();
    emit(
      "task",
      `⚡ ${worker.display_name} claimed: "${task.description.slice(0, 50)}…"`,
      "info"
    );
  };

  claimTask(0, 0); // Agent-1 claims T0
  claimTask(1, 3); // Agent-4 claims T1
  callbacks.onTasks([...tasks]);

  if (signal.aborted) return;
  await delay(500);

  // 5. Emit scent signals during work
  const sig1 = createScentSignal(
    tasks[0].task_id,
    workers[0].worker_id,
    "Progress",
    0.7,
    "GDP data gathered"
  );
  allSignals.push(sig1);
  emit("signal", `📡 Scent [Progress=0.7] on Task 0 from ${workers[0].display_name}`);
  callbacks.onSignals([...allSignals]);

  if (signal.aborted) return;
  await delay(300);

  const sig2 = createScentSignal(
    tasks[1].task_id,
    workers[3].worker_id,
    "Difficulty",
    0.85,
    "Bond yield data inconsistent across sources"
  );
  allSignals.push(sig2);
  emit(
    "signal",
    `📡 Scent [Difficulty=0.85] on Task 1 from ${workers[3].display_name}`,
    "warning"
  );
  callbacks.onSignals([...allSignals]);

  if (signal.aborted) return;
  await delay(500);

  // 6. Complete T0
  const t0 = tasks[0];
  t0.status = "Complete";
  t0.completed_at = now();
  t0.reward = 0.85;
  const sig3 = createScentSignal(t0.task_id, workers[0].worker_id, "Completion", 1.0);
  allSignals.push(sig3);
  emit("task", `✅ Task 0 completed by ${workers[0].display_name} (reward: 0.85)`, "success");

  // Complete T1
  const t1 = tasks[1];
  t1.status = "Complete";
  t1.completed_at = now();
  t1.reward = 0.72;
  const sig4 = createScentSignal(t1.task_id, workers[3].worker_id, "Completion", 1.0);
  allSignals.push(sig4);
  emit("task", `✅ Task 1 completed by ${workers[3].display_name} (reward: 0.72)`, "success");

  // Emit urgency for graph
  const sig5 = createScentSignal("", "", "Urgency", 0.6, "deadline approaching");
  allSignals.push(sig5);
  emit("signal", `📡 Urgency scent emitted [intensity=0.6]`, "warning");

  callbacks.onTasks([...tasks]);
  callbacks.onSignals([...allSignals]);

  // Update session
  session.completed_tasks = 2;
  callbacks.onSession({ ...session });

  if (signal.aborted) return;
  await delay(400);

  // 7. Activate dependent tasks (T2, T3, T4, T5)
  tasks[2].status = "Ready";
  tasks[3].status = "Ready";
  tasks[4].status = "Ready";
  tasks[5].status = "Ready";
  emit("task", `🔓 4 tasks activated (dependencies resolved)`, "info");

  claimTask(2, 1); // Agent-2 claims T2
  claimTask(3, 0); // Agent-1 claims T3
  claimTask(4, 3); // Agent-4 claims T4
  claimTask(5, 2); // Agent-3 claims T5

  callbacks.onTasks([...tasks]);
  emit("task", `⚡ 4 agents now working in parallel`);

  if (signal.aborted) return;
  await delay(600);

  // 8. Simulate HelpWanted scent
  const sig6 = createScentSignal(
    tasks[3].task_id,
    workers[0].worker_id,
    "HelpWanted",
    0.9,
    "Need domain expert for LSTM hyperparameter tuning"
  );
  allSignals.push(sig6);
  emit(
    "signal",
    `🆘 HelpWanted scent [0.9] from ${workers[0].display_name}`,
    "warning"
  );

  const sig7 = createScentSignal(
    tasks[4].task_id,
    workers[3].worker_id,
    "Progress",
    0.5,
    "Sector rotation analysis 50% complete"
  );
  allSignals.push(sig7);
  callbacks.onSignals([...allSignals]);

  if (signal.aborted) return;
  await delay(500);

  // 9. Complete T2, T3, T4; Fail T5
  tasks[2].status = "Complete";
  tasks[2].completed_at = now();
  tasks[2].reward = 0.78;
  emit("task", `✅ Task 2 (risk assessment) completed by ${workers[1].display_name}`, "success");

  tasks[3].status = "Complete";
  tasks[3].completed_at = now();
  tasks[3].reward = 0.91;
  emit("task", `✅ Task 3 (trend forecasting) completed by ${workers[0].display_name}`, "success");

  tasks[4].status = "Complete";
  tasks[4].completed_at = now();
  tasks[4].reward = 0.68;
  emit("task", `✅ Task 4 (sector analysis) completed by ${workers[3].display_name}`, "success");

  // Task 5 fails
  tasks[5].status = "Failed";
  tasks[5].retries = 1;
  const sig8 = createScentSignal(
    tasks[5].task_id,
    workers[2].worker_id,
    "Failure",
    1.0,
    "NLP pipeline OOM — sentiment model too large for context"
  );
  allSignals.push(sig8);
  emit(
    "task",
    `❌ Task 5 (sentiment analysis) FAILED — ${workers[2].display_name}: OOM error`,
    "error"
  );
  emit(
    "signal",
    `📡 Failure scent [1.0] emitted for Task 5`,
    "error"
  );

  session.completed_tasks = 5;
  session.failed_tasks = 1;
  callbacks.onTasks([...tasks]);
  callbacks.onSession({ ...session });

  if (signal.aborted) return;
  await delay(400);

  // 10. Retry Task 5 with another worker
  emit("task", `🔄 Retrying Task 5 (sentiment analysis)...`);
  tasks[5].status = "Active";
  tasks[5].worker_id = workers[0].worker_id;
  tasks[5].started_at = now();
  callbacks.onTasks([...tasks]);

  if (signal.aborted) return;
  await delay(500);

  tasks[5].status = "Complete";
  tasks[5].completed_at = now();
  tasks[5].reward = 0.65;
  session.completed_tasks = 6;
  session.failed_tasks = 0;
  emit(
    "task",
    `✅ Task 5 retry SUCCESS by ${workers[0].display_name} (reward: 0.65)`,
    "success"
  );
  callbacks.onTasks([...tasks]);
  callbacks.onSession({ ...session });

  if (signal.aborted) return;
  await delay(300);

  // 11. Activate T6 (synthesis)
  tasks[6].status = "Ready";
  claimTask(6, 1);
  callbacks.onTasks([...tasks]);
  emit("task", `⚡ ${workers[1].display_name} starts synthesis task`, "info");

  if (signal.aborted) return;
  await delay(600);

  // 12. Run consensus on synthesis
  const roundId = uid();
  emit("vote", `🗳️ Starting consensus round for investment thesis...`);

  const votes = seedConsensusVotes(roundId, tasks[6].task_id, workers);
  for (const v of votes) {
    emit(
      "vote",
      `  → ${v.model_name}: ${v.position} (conf: ${(v.confidence * 100).toFixed(0)}%)${v.is_contrarian ? " ⚠️ CONTRARIAN" : ""}`
    );
  }
  callbacks.onVotes(votes);

  if (signal.aborted) return;
  await delay(500);

  const consensus = seedConsensusResult(roundId, tasks[6].task_id);
  emit(
    "consensus",
    `📊 Consensus: ${consensus.final_position} (score: ${(consensus.consensus_score * 100).toFixed(0)}%, ${consensus.dissenting_count}/${consensus.total_votes} dissenting)`,
    consensus.escalate_to_human ? "warning" : "success"
  );
  emit(
    "consensus",
    `  → Heterogeneity: ${consensus.heterogeneity_score.toFixed(2)}, Debate rounds: ${consensus.debate_rounds}, Escalate: ${consensus.escalate_to_human ? "YES" : "NO"}`
  );
  callbacks.onConsensus(consensus);

  if (signal.aborted) return;
  await delay(400);

  // 13. Complete T6
  tasks[6].status = "Complete";
  tasks[6].completed_at = now();
  tasks[6].reward = 0.88;
  session.completed_tasks = 7;
  callbacks.onTasks([...tasks]);
  callbacks.onSession({ ...session });
  emit("task", `✅ Synthesis task completed — investment thesis generated`, "success");

  if (signal.aborted) return;
  await delay(300);

  // 14. Final report (T7)
  tasks[7].status = "Ready";
  claimTask(7, 2);
  callbacks.onTasks([...tasks]);
  emit("task", `⚡ ${workers[2].display_name} generates final report...`);

  if (signal.aborted) return;
  await delay(500);

  tasks[7].status = "Complete";
  tasks[7].completed_at = now();
  tasks[7].reward = 0.92;
  session.completed_tasks = 8;
  session.status = "Completed";
  session.completed_at = now();
  session.parl_reward = 0.82;
  callbacks.onTasks([...tasks]);
  callbacks.onSession({ ...session });
  emit(
    "session",
    `🎉 Swarm session COMPLETED — PARL Reward: 0.82, Tasks: 8/8`,
    "success"
  );

  // 15. Audit trail
  const audit = createAuditEvent(
    "swarm-coordinator",
    "session_complete",
    session.session_id,
    `8 tasks completed, 0 failed, PARL reward 0.82`,
    "ALLOW"
  );
  emit("audit", `📝 Audit logged: session_complete → ALLOW`);
  callbacks.onAudit(audit);
}
