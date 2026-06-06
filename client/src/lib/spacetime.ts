// @ts-nocheck — spacetimedb SDK API in flux; not used in simulation mode
import { connect, type DbConnection } from "spacetimedb";

const STDB_HOST = process.env.NEXT_PUBLIC_SPACETIMEDB_HOST || "ws://localhost:3000";
const STDB_DB = process.env.NEXT_PUBLIC_SPACETIMEDB_DB || "swarm-module";

let _conn: DbConnection | null = null;

export type ConnectionStatus = "disconnected" | "connecting" | "connected" | "error";

export interface SpaceTimeCallbacks {
  onStatusChange: (status: ConnectionStatus) => void;
  onWorkerInsert: (row: Record<string, unknown>) => void;
  onWorkerUpdate: (row: Record<string, unknown>) => void;
  onWorkerDelete: (row: Record<string, unknown>) => void;
  onTaskInsert: (row: Record<string, unknown>) => void;
  onTaskUpdate: (row: Record<string, unknown>) => void;
  onTaskDelete: (row: Record<string, unknown>) => void;
  onScentInsert: (row: Record<string, unknown>) => void;
  onVoteInsert: (row: Record<string, unknown>) => void;
  onConsensusInsert: (row: Record<string, unknown>) => void;
  onSessionInsert: (row: Record<string, unknown>) => void;
  onSessionUpdate: (row: Record<string, unknown>) => void;
  onAuditInsert: (row: Record<string, unknown>) => void;
}

const noop = () => {};

export function createConnection(callbacks: Partial<SpaceTimeCallbacks> = {}) {
  const cb: SpaceTimeCallbacks = {
    onStatusChange: noop,
    onWorkerInsert: noop,
    onWorkerUpdate: noop,
    onWorkerDelete: noop,
    onTaskInsert: noop,
    onTaskUpdate: noop,
    onTaskDelete: noop,
    onScentInsert: noop,
    onVoteInsert: noop,
    onConsensusInsert: noop,
    onSessionInsert: noop,
    onSessionUpdate: noop,
    onAuditInsert: noop,
    ...callbacks,
  };

  try {
    cb.onStatusChange("connecting");

    const conn = connect(STDB_HOST, STDB_DB);

    conn.onConnect(() => {
      cb.onStatusChange("connected");
      console.log("[SpaceTimeDB] Connected to", STDB_DB, "at", STDB_HOST);

      // Subscribe to all public tables using SQL
      conn.subscriptionBuilder().subscribe("SELECT * FROM Worker");
      conn.subscriptionBuilder().subscribe("SELECT * FROM Task");
      conn.subscriptionBuilder().subscribe("SELECT * FROM ScentSignal");
      conn.subscriptionBuilder().subscribe("SELECT * FROM SwarmSession");
      conn.subscriptionBuilder().subscribe("SELECT * FROM ConsensusVote");
      conn.subscriptionBuilder().subscribe("SELECT * FROM ConsensusResult");
      conn.subscriptionBuilder().subscribe("SELECT * FROM AuditEvent");
      conn.subscriptionBuilder().subscribe("SELECT * FROM Policy");
    });

    conn.onDisconnect(() => {
      cb.onStatusChange("disconnected");
      console.log("[SpaceTimeDB] Disconnected");
    });

    conn.onError((err) => {
      cb.onStatusChange("error");
      console.error("[SpaceTimeDB] Error:", err);
    });

    // Register event handlers for table inserts/updates/deletes
    conn.onEvent("Worker", "insert", cb.onWorkerInsert);
    conn.onEvent("Worker", "update", cb.onWorkerUpdate);
    conn.onEvent("Worker", "delete", cb.onWorkerDelete);

    conn.onEvent("Task", "insert", cb.onTaskInsert);
    conn.onEvent("Task", "update", cb.onTaskUpdate);
    conn.onEvent("Task", "delete", cb.onTaskDelete);

    conn.onEvent("ScentSignal", "insert", cb.onScentInsert);
    conn.onEvent("ConsensusVote", "insert", cb.onVoteInsert);
    conn.onEvent("ConsensusResult", "insert", cb.onConsensusInsert);

    conn.onEvent("SwarmSession", "insert", cb.onSessionInsert);
    conn.onEvent("SwarmSession", "update", cb.onSessionUpdate);

    conn.onEvent("AuditEvent", "insert", cb.onAuditInsert);

    _conn = conn;
    return conn;
  } catch (err) {
    cb.onStatusChange("error");
    console.error("[SpaceTimeDB] Failed to connect:", err);
    return null;
  }
}

export function getConnection(): DbConnection | null {
  return _conn;
}

export function disconnect() {
  if (_conn) {
    _conn.disconnect();
    _conn = null;
  }
}
