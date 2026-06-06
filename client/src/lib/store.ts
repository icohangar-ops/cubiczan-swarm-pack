import { create } from "zustand";
import type {
  Worker,
  Task,
  ScentSignal,
  ConsensusVote,
  ConsensusResult,
  AuditEvent,
  SwarmSession,
  StreamEvent,
  ScentAggregate,
  ConnectionStatus,
} from "./types";

interface SwarmStore {
  // Connection
  connectionStatus: ConnectionStatus;
  setConnectionStatus: (s: ConnectionStatus) => void;

  // Live data
  workers: Worker[];
  tasks: Task[];
  scentSignals: ScentSignal[];
  consensusVotes: ConsensusVote[];
  consensusResults: ConsensusResult[];
  auditEvents: AuditEvent[];
  swarmSessions: SwarmSession[];

  // Setters
  setWorkers: (w: Worker[]) => void;
  setTasks: (t: Task[]) => void;
  setScentSignals: (s: ScentSignal[]) => void;
  setConsensusVotes: (v: ConsensusVote[]) => void;
  setConsensusResults: (r: ConsensusResult[]) => void;
  setAuditEvents: (e: AuditEvent[]) => void;
  setSwarmSessions: (s: SwarmSession[]) => void;
  updateSwarmSession: (s: SwarmSession) => void;
  addStreamEvent: (e: StreamEvent) => void;

  // Derived
  streamEvents: StreamEvent[];
  scentAggregates: ScentAggregate[];

  // Simulation
  isSimulating: boolean;
  setIsSimulating: (v: boolean) => void;

  // Computed helpers (memoized via selectors outside)
  computeScentAggregates: () => ScentAggregate[];
}

export const useSwarmStore = create<SwarmStore>((set, get) => ({
  // Connection
  connectionStatus: "disconnected",
  setConnectionStatus: (connectionStatus) => set({ connectionStatus }),

  // Live data
  workers: [],
  tasks: [],
  scentSignals: [],
  consensusVotes: [],
  consensusResults: [],
  auditEvents: [],
  swarmSessions: [],

  // Setters
  setWorkers: (workers) => set({ workers }),
  setTasks: (tasks) => set({ tasks }),
  setScentSignals: (scentSignals) =>
    set((state) => {
      // Recompute aggregates when signals change
      const scentAggregates = computeAggregates(scentSignals, state.tasks);
      return { scentSignals, scentAggregates };
    }),
  setConsensusVotes: (consensusVotes) => set({ consensusVotes }),
  setConsensusResults: (consensusResults) => set({ consensusResults }),
  setAuditEvents: (auditEvents) => set({ auditEvents }),
  setSwarmSessions: (swarmSessions) => set({ swarmSessions }),
  updateSwarmSession: (session) =>
    set((state) => ({
      swarmSessions: state.swarmSessions.map((s) =>
        s.session_id === session.session_id ? session : s
      ),
    })),
  addStreamEvent: (event) =>
    set((state) => ({
      streamEvents: [event, ...state.streamEvents].slice(0, 200),
    })),

  // Derived
  streamEvents: [],
  scentAggregates: [],

  // Simulation
  isSimulating: false,
  setIsSimulating: (isSimulating) => set({ isSimulating }),

  // Compute scent aggregates
  computeScentAggregates: () => {
    const { scentSignals, tasks } = get();
    return computeAggregates(scentSignals, tasks);
  },
}));

function computeAggregates(
  signals: ScentSignal[],
  tasks: Task[]
): ScentAggregate[] {
  const map = new Map<string, ScentAggregate>();

  // Initialize for all tasks
  for (const t of tasks) {
    map.set(t.task_id, {
      task_id: t.task_id,
      Completion: 0,
      Failure: 0,
      Difficulty: 0,
      Urgency: 0,
      Progress: 0,
      HelpWanted: 0,
    });
  }

  // Aggregate signals — take max intensity per type per task
  for (const s of signals) {
    if (!s.task_id) continue;
    const agg = map.get(s.task_id);
    if (!agg) continue;
    agg[s.scent_type] = Math.max(agg[s.scent_type], s.intensity);
  }

  return Array.from(map.values());
}
