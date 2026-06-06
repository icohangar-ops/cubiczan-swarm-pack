// SpaceTimeDB table type definitions matching Rust module structs

export type TaskStatus =
  | "Pending"
  | "Ready"
  | "Active"
  | "Complete"
  | "Failed"
  | "Escalate";

export type ScentType =
  | "Completion"
  | "Failure"
  | "Difficulty"
  | "Urgency"
  | "Progress"
  | "HelpWanted";

export type SwarmSessionStatus =
  | "Initializing"
  | "Running"
  | "Paused"
  | "Completed"
  | "Failed"
  | "PartialSuccess";

export type PolicyTrustLevel = "High" | "Medium" | "Low" | "Blocked";

export type ConnectionStatus = "disconnected" | "connecting" | "connected" | "error";

export interface Worker {
  worker_id: string;
  display_name: string;
  model_name: string;
  tags: string[];
  domain: string;
  is_online: boolean;
  connected_at: string;
  last_heartbeat: string;
}

export interface Task {
  task_id: string;
  graph_id: string;
  status: TaskStatus;
  description: string;
  agent_type: string;
  tags: string[];
  dependencies: string[];
  worker_id: string;
  result: string;
  retries: number;
  reward: number;
  created_at: string;
  started_at: string;
  completed_at: string;
}

export interface ScentSignal {
  signal_id: string;
  task_id: string;
  worker_id: string;
  scent_type: ScentType;
  intensity: number;
  emitted_at: string;
  metadata: string;
}

export interface ConsensusVote {
  vote_id: string;
  round_id: string;
  task_id: string;
  agent_id: string;
  model_name: string;
  position: string;
  confidence: number;
  reasoning: string;
  is_contrarian: boolean;
  voted_at: string;
}

export interface ConsensusResult {
  round_id: string;
  task_id: string;
  final_position: string;
  consensus_score: number;
  debate_rounds: number;
  escalate_to_human: boolean;
  heterogeneity_score: number;
  total_votes: number;
  dissenting_count: number;
  computed_at: string;
}

export interface AuditEvent {
  event_id: string;
  actor: string;
  action: string;
  resource: string;
  payload: string;
  decision: string;
  policy_id: string;
  previous_hash: string;
  hash: string;
  timestamp: string;
}

export interface SwarmSession {
  session_id: string;
  graph_id: string;
  domain: string;
  task_description: string;
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  agents_used: number;
  status: SwarmSessionStatus;
  parl_reward: number;
  theoretical_speedup: number;
  started_at: string;
  completed_at: string;
}

export interface Policy {
  policy_id: string;
  tool: string;
  trust_level: PolicyTrustLevel;
  max_calls: number;
  window_seconds: number;
  blocked_actions: string[];
  approval_required_actions: string[];
}

// Event stream entry for UI
export interface StreamEvent {
  id: string;
  timestamp: string;
  type: "task" | "signal" | "vote" | "consensus" | "worker" | "session" | "audit";
  message: string;
  severity: "info" | "success" | "warning" | "error";
}

// Aggregated scent per task
export interface ScentAggregate {
  task_id: string;
  Completion: number;
  Failure: number;
  Difficulty: number;
  Urgency: number;
  Progress: number;
  HelpWanted: number;
}
