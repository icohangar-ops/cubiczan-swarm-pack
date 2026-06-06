"use client";

import React, { useRef, useCallback, useEffect, useMemo } from "react";
import { useSwarmStore } from "@/lib/store";
import { runSimulation } from "@/lib/mock-data";
import type { TaskStatus, ScentType, StreamEvent } from "@/lib/types";
import {
  Activity,
  Users,
  ListTodo,
  Radio,
  Vote,
  FileText,
  Play,
  Square,
  Wifi,
  WifiOff,
  Loader2,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  Zap,
  Brain,
} from "lucide-react";

// ── Helpers ────────────────────────────────────────────────────────

function formatTime(iso: string): string {
  if (!iso) return "--:--:--";
  const d = new Date(iso);
  return d.toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

const TASK_STATUS_CONFIG: Record<
  TaskStatus,
  { bg: string; text: string; dot: string; label: string }
> = {
  Pending: { bg: "bg-slate-500/20", text: "text-slate-400", dot: "bg-slate-500", label: "Pending" },
  Ready: { bg: "bg-blue-500/20", text: "text-blue-400", dot: "bg-blue-500", label: "Ready" },
  Active: { bg: "bg-green-500/20", text: "text-green-400", dot: "bg-green-500 animate-pulse", label: "Active" },
  Complete: { bg: "bg-emerald-500/20", text: "text-emerald-400", dot: "bg-emerald-500", label: "Complete" },
  Failed: { bg: "bg-red-500/20", text: "text-red-400", dot: "bg-red-500", label: "Failed" },
  Escalate: { bg: "bg-orange-500/20", text: "text-orange-400", dot: "bg-orange-500", label: "Escalate" },
};

const SCENT_CONFIG: Record<
  ScentType,
  { color: string; bg: string; label: string }
> = {
  Completion: { color: "bg-emerald-500", bg: "bg-emerald-500/20", label: "Completion" },
  Failure: { color: "bg-red-500", bg: "bg-red-500/20", label: "Failure" },
  Difficulty: { color: "bg-orange-500", bg: "bg-orange-500/20", label: "Difficulty" },
  Urgency: { color: "bg-yellow-500", bg: "bg-yellow-500/20", label: "Urgency" },
  Progress: { color: "bg-blue-500", bg: "bg-blue-500/20", label: "Progress" },
  HelpWanted: { color: "bg-purple-500", bg: "bg-purple-500/20", label: "HelpWanted" },
};

const CONNECTION_STATUS_STYLE: Record<string, { dot: string; label: string }> = {
  disconnected: { dot: "bg-slate-500", label: "Disconnected" },
  connecting: { dot: "bg-yellow-500 animate-pulse", label: "Connecting..." },
  connected: { dot: "bg-emerald-500", label: "Connected" },
  error: { dot: "bg-red-500", label: "Error" },
};

function SeverityIcon({ severity }: { severity: StreamEvent["severity"] }) {
  switch (severity) {
    case "success":
      return <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />;
    case "warning":
      return <AlertTriangle className="w-3.5 h-3.5 text-yellow-400 shrink-0" />;
    case "error":
      return <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />;
    default:
      return <Info className="w-3.5 h-3.5 text-blue-400 shrink-0" />;
  }
}

// ── Card Shell ─────────────────────────────────────────────────────

function Card({
  title,
  icon,
  children,
  className = "",
}: {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-xl border border-border bg-card p-4 lg:p-5 flex flex-col gap-3 ${className}`}
    >
      <div className="flex items-center gap-2 text-sm font-semibold text-muted">
        {icon}
        <h2>{title}</h2>
      </div>
      {children}
    </div>
  );
}

// ── Scent Bar ──────────────────────────────────────────────────────

function ScentBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-[4.5rem] text-muted shrink-0 text-right">{label}</span>
      <div className="flex-1 h-2 rounded-full bg-slate-700/60 overflow-hidden">
        <div
          className={`h-full rounded-full ${color} transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-8 text-muted tabular-nums">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}

// ── Dashboard ──────────────────────────────────────────────────────

export default function Dashboard() {
  // Store selectors
  const workers = useSwarmStore((s) => s.workers);
  const tasks = useSwarmStore((s) => s.tasks);
  const scentSignals = useSwarmStore((s) => s.scentSignals);
  const consensusVotes = useSwarmStore((s) => s.consensusVotes);
  const consensusResults = useSwarmStore((s) => s.consensusResults);
  const swarmSessions = useSwarmStore((s) => s.swarmSessions);
  const streamEvents = useSwarmStore((s) => s.streamEvents);
  const scentAggregates = useSwarmStore((s) => s.scentAggregates);
  const connectionStatus = useSwarmStore((s) => s.connectionStatus);
  const isSimulating = useSwarmStore((s) => s.isSimulating);

  const setWorkers = useSwarmStore((s) => s.setWorkers);
  const setTasks = useSwarmStore((s) => s.setTasks);
  const setScentSignals = useSwarmStore((s) => s.setScentSignals);
  const setConsensusVotes = useSwarmStore((s) => s.setConsensusVotes);
  const setConsensusResults = useSwarmStore((s) => s.setConsensusResults);
  const setAuditEvents = useSwarmStore((s) => s.setAuditEvents);
  const setSwarmSessions = useSwarmStore((s) => s.setSwarmSessions);
  const addStreamEvent = useSwarmStore((s) => s.addStreamEvent);
  const setConnectionStatus = useSwarmStore((s) => s.setConnectionStatus);
  const setIsSimulating = useSwarmStore((s) => s.setIsSimulating);

  const abortRef = useRef({ aborted: false });
  const eventStreamRef = useRef<HTMLDivElement>(null);

  // Auto-scroll event stream to bottom
  useEffect(() => {
    if (eventStreamRef.current) {
      eventStreamRef.current.scrollTop = eventStreamRef.current.scrollHeight;
    }
  }, [streamEvents.length]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      abortRef.current.aborted = true;
    };
  }, []);

  // ── Simulation control ──────────────────────────────────────────

  const handleToggleSimulation = useCallback(() => {
    if (isSimulating) {
      abortRef.current.aborted = true;
      setIsSimulating(false);
      setConnectionStatus("disconnected");
      return;
    }

    abortRef.current = { aborted: false };
    setIsSimulating(true);
    setConnectionStatus("connected");

    runSimulation(
      {
        onWorkers: (w) => setWorkers(w),
        onSession: (s) => setSwarmSessions([s]),
        onTasks: (t) => setTasks(t),
        onSignals: (s) => setScentSignals(s),
        onVotes: (v) => setConsensusVotes(v),
        onConsensus: (r) => {
          const current = useSwarmStore.getState().consensusResults;
          setConsensusResults([r, ...current]);
        },
        onAudit: (e) => {
          const current = useSwarmStore.getState().auditEvents;
          setAuditEvents([e, ...current]);
        },
        onEvent: (e) => addStreamEvent(e),
      },
      abortRef.current
    ).finally(() => {
      if (!abortRef.current.aborted) {
        setIsSimulating(false);
      }
    });
  }, [
    isSimulating,
    setIsSimulating,
    setConnectionStatus,
    setWorkers,
    setSwarmSessions,
    setTasks,
    setScentSignals,
    setConsensusVotes,
    setConsensusResults,
    setAuditEvents,
    addStreamEvent,
  ]);

  // ── Derived / memoized data ───────────────────────────────────────

  const workerMap = useMemo(
    () => new Map(workers.map((w) => [w.worker_id, w])),
    [workers]
  );

  const taskMap = useMemo(
    () => new Map(tasks.map((t) => [t.task_id, t])),
    [tasks]
  );

  const totalWorkers = workers.length;
  const onlineWorkers = workers.filter((w) => w.is_online).length;
  const completedTasks = tasks.filter((t) => t.status === "Complete").length;
  const totalTasks = tasks.length;
  const latestConsensus = consensusResults[0] ?? null;
  const latestSession = swarmSessions[0] ?? null;
  const taskProgress = totalTasks > 0 ? completedTasks / totalTasks : 0;

  const connStyle = CONNECTION_STATUS_STYLE[connectionStatus] ?? CONNECTION_STATUS_STYLE.disconnected;

  // ── Render ───────────────────────────────────────────────────────

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      {/* ── Header ──────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md px-4 lg:px-6 py-3">
        <div className="max-w-[1600px] mx-auto flex items-center justify-between gap-4">
          {/* Title */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Brain className="w-6 h-6 text-primary" />
              <h1 className="text-lg font-bold tracking-tight text-foreground">
                Swarm Pack
              </h1>
            </div>
            <span className="hidden sm:inline text-xs text-muted border border-border rounded-full px-2.5 py-0.5">
              SpaceTimeDB Coordination
            </span>
          </div>

          {/* Right side: status + button */}
          <div className="flex items-center gap-4">
            {/* Connection indicator */}
            <div className="flex items-center gap-2 text-xs text-muted">
              <span
                className={`w-2 h-2 rounded-full ${connStyle.dot}`}
              />
              <span className="hidden sm:inline">{connStyle.label}</span>
            </div>

            {/* Simulation toggle */}
            <button
              onClick={handleToggleSimulation}
              className={`
                flex items-center gap-2 text-sm font-medium rounded-lg px-4 py-2
                transition-all duration-200 cursor-pointer
                ${
                  isSimulating
                    ? "bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/40"
                    : "bg-primary/20 text-primary hover:bg-primary/30 border border-primary/40"
                }
              `}
            >
              {isSimulating ? (
                <>
                  <Square className="w-4 h-4" />
                  Stop Simulation
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Run Simulation
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* ── Main Content ──────────────────────────────────────────── */}
      <main className="flex-1 px-4 lg:px-6 py-4 lg:py-6">
        <div className="max-w-[1600px] mx-auto flex flex-col gap-4 lg:gap-5">
          {/* ── Stats Row ────────────────────────────────────────── */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4">
            {/* Total Workers */}
            <div className="rounded-xl border border-border bg-card p-4 flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10">
                <Users className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-xs text-muted">Total Workers</p>
                <p className="text-xl font-bold tabular-nums">
                  {totalWorkers}
                  {totalWorkers > 0 && (
                    <span className="text-sm font-normal text-emerald-400 ml-1">
                      {onlineWorkers} online
                    </span>
                  )}
                </p>
              </div>
            </div>

            {/* Tasks Complete */}
            <div className="rounded-xl border border-border bg-card p-4 flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-blue-500/10">
                <ListTodo className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <p className="text-xs text-muted">Tasks Complete</p>
                <p className="text-xl font-bold tabular-nums">
                  {completedTasks}
                  <span className="text-sm font-normal text-muted">/{totalTasks}</span>
                </p>
              </div>
            </div>

            {/* Scent Signals */}
            <div className="rounded-xl border border-border bg-card p-4 flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-orange-500/10">
                <Radio className="w-5 h-5 text-orange-400" />
              </div>
              <div>
                <p className="text-xs text-muted">Scent Signals</p>
                <p className="text-xl font-bold tabular-nums">{scentSignals.length}</p>
              </div>
            </div>

            {/* Consensus Score */}
            <div className="rounded-xl border border-border bg-card p-4 flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-purple-500/10">
                <Vote className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <p className="text-xs text-muted">Consensus Score</p>
                <p className="text-xl font-bold tabular-nums">
                  {latestConsensus
                    ? `${(latestConsensus.consensus_score * 100).toFixed(0)}%`
                    : "—"}
                </p>
              </div>
            </div>
          </div>

          {/* ── Main 2-column Grid ─────────────────────────────── */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-5">
            {/* ── LEFT COLUMN ──────────────────────────────────────── */}

            {/* Workers Panel */}
            <Card title="Workers" icon={<Users className="w-4 h-4" />}>
              <div className="flex flex-col gap-2 max-h-80 overflow-y-auto pr-1">
                {workers.length === 0 ? (
                  <p className="text-xs text-muted py-4 text-center">
                    No workers connected. Run a simulation to see agents.
                  </p>
                ) : (
                  workers.map((w) => (
                    <div
                      key={w.worker_id}
                      className="flex items-start gap-3 p-3 rounded-lg bg-background/50 border border-border/50 hover:border-border transition-colors"
                    >
                      {/* Online dot */}
                      <span
                        className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${
                          w.is_online ? "bg-emerald-500" : "bg-slate-600"
                        }`}
                      />
                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-semibold text-foreground">
                            {w.display_name}
                          </span>
                          <span className="text-xs text-muted">{w.model_name}</span>
                        </div>
                        <p className="text-xs text-muted mt-0.5">{w.domain}</p>
                        <div className="flex flex-wrap gap-1 mt-1.5">
                          {w.tags.map((tag) => (
                            <span
                              key={tag}
                              className="text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                      {/* Heartbeat */}
                      <span className="text-[10px] text-muted tabular-nums whitespace-nowrap mt-0.5">
                        {formatTime(w.last_heartbeat)}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </Card>

            {/* Consensus Panel */}
            <Card title="Consensus" icon={<Vote className="w-4 h-4" />}>
              {latestConsensus ? (
                <>
                  {/* Summary */}
                  <div className="flex flex-col gap-3 p-3 rounded-lg bg-background/50 border border-border/50">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-foreground">
                        Final Position
                      </span>
                      <span className="text-sm font-bold text-primary">
                        {latestConsensus.final_position}
                      </span>
                    </div>

                    {/* Score bar */}
                    <div>
                      <div className="flex items-center justify-between text-xs text-muted mb-1">
                        <span>Consensus Score</span>
                        <span className="tabular-nums">
                          {(latestConsensus.consensus_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="h-2.5 rounded-full bg-slate-700/60 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-primary transition-all duration-700"
                          style={{
                            width: `${latestConsensus.consensus_score * 100}%`,
                          }}
                        />
                      </div>
                    </div>

                    {/* Metrics */}
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div>
                        <span className="text-muted">Heterogeneity</span>
                        <p className="font-semibold tabular-nums">
                          {latestConsensus.heterogeneity_score.toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <span className="text-muted">Debate Rounds</span>
                        <p className="font-semibold tabular-nums">
                          {latestConsensus.debate_rounds}
                        </p>
                      </div>
                      <div>
                        <span className="text-muted">Dissenting</span>
                        <p className="font-semibold tabular-nums">
                          {latestConsensus.dissenting_count}/{latestConsensus.total_votes}
                        </p>
                      </div>
                    </div>

                    {latestConsensus.escalate_to_human && (
                      <div className="flex items-center gap-2 text-xs text-orange-400 bg-orange-500/10 rounded-lg px-3 py-2 border border-orange-500/20">
                        <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                        <span>Escalated to human review</span>
                      </div>
                    )}
                  </div>

                  {/* Votes list */}
                  <div className="flex flex-col gap-1.5 max-h-48 overflow-y-auto pr-1">
                    {consensusVotes.map((v) => (
                      <div
                        key={v.vote_id}
                        className="flex items-center gap-3 p-2 rounded-lg bg-background/40 border border-border/30"
                      >
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-xs font-semibold text-foreground">
                              {v.model_name}
                            </span>
                            <span className="text-xs font-medium text-muted">
                              {v.position}
                            </span>
                            {v.is_contrarian && (
                              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-orange-500/20 text-orange-400 border border-orange-500/30">
                                CONTRARIAN
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 shrink-0 w-24">
                          <div className="flex-1 h-1.5 rounded-full bg-slate-700/60 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-purple-400 transition-all duration-500"
                              style={{ width: `${v.confidence * 100}%` }}
                            />
                          </div>
                          <span className="text-[10px] text-muted tabular-nums w-8 text-right">
                            {(v.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <p className="text-xs text-muted py-4 text-center">
                  No consensus results yet. Run a simulation to see agent
                  consensus.
                </p>
              )}
            </Card>

            {/* Task DAG Panel */}
            <Card title="Task DAG" icon={<ListTodo className="w-4 h-4" />}>
              {/* Progress bar */}
              {totalTasks > 0 && (
                <div className="mb-2">
                  <div className="flex items-center justify-between text-xs text-muted mb-1">
                    <span>Overall Progress</span>
                    <span className="tabular-nums">
                      {completedTasks}/{totalTasks} tasks
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-700/60 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-emerald-500 transition-all duration-500"
                      style={{ width: `${taskProgress * 100}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="flex flex-col gap-2 max-h-72 overflow-y-auto pr-1">
                {tasks.length === 0 ? (
                  <p className="text-xs text-muted py-4 text-center">
                    No tasks. Run a simulation to see the task DAG.
                  </p>
                ) : (
                  tasks.map((t) => {
                    const statusCfg = TASK_STATUS_CONFIG[t.status];
                    const worker = workerMap.get(t.worker_id);

                    return (
                      <div
                        key={t.task_id}
                        className={`p-3 rounded-lg border transition-colors ${
                          t.status === "Active"
                            ? "glow-active border-primary/30 bg-primary/5"
                            : "border-border/50 bg-background/50 hover:border-border"
                        }`}
                      >
                        {/* Description + status */}
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-sm text-foreground leading-snug flex-1">
                            {t.description}
                          </p>
                          <span
                            className={`shrink-0 inline-flex items-center gap-1.5 text-[11px] font-medium px-2 py-0.5 rounded-full ${statusCfg.bg} ${statusCfg.text}`}
                          >
                            <span className={`w-1.5 h-1.5 rounded-full ${statusCfg.dot}`} />
                            {statusCfg.label}
                          </span>
                        </div>

                        {/* Meta row */}
                        <div className="flex items-center gap-3 mt-2 text-[11px] text-muted flex-wrap">
                          {worker && (
                            <span className="flex items-center gap-1">
                              <Zap className="w-3 h-3" />
                              {worker.display_name}
                            </span>
                          )}
                          {t.dependencies.length > 0 && (
                            <span className="flex items-center gap-1">
                              <Activity className="w-3 h-3" />
                              {t.dependencies.length} dep
                              {t.dependencies.length > 1 ? "s" : ""}
                            </span>
                          )}
                          {t.reward > 0 && (
                            <span className="text-emerald-400">
                              reward: {t.reward.toFixed(2)}
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </Card>

            {/* Event Stream Panel */}
            <Card title="Event Stream" icon={<FileText className="w-4 h-4" />}>
              <div
                ref={eventStreamRef}
                className="max-h-72 min-h-[8rem] overflow-y-auto rounded-lg bg-background/60 border border-border/50 p-2 font-mono text-[11px] leading-relaxed"
              >
                {streamEvents.length === 0 ? (
                  <p className="text-muted text-center py-6">
                    No events. Run a simulation to see the stream.
                  </p>
                ) : (
                  streamEvents
                    .slice()
                    .reverse()
                    .map((ev) => (
                      <div
                        key={ev.id}
                        className="flex items-start gap-2 py-1 border-b border-border/20 last:border-0"
                      >
                        <span className="text-muted shrink-0 tabular-nums">
                          {formatTime(ev.timestamp)}
                        </span>
                        <SeverityIcon severity={ev.severity} />
                        <span className="text-foreground/80 break-all">{ev.message}</span>
                      </div>
                    ))
                )}
              </div>
            </Card>

            {/* Scent Field Panel */}
            <Card title="Scent Field" icon={<Radio className="w-4 h-4" />}>
              <div className="flex flex-col gap-4 max-h-80 overflow-y-auto pr-1">
                {scentAggregates.length === 0 ? (
                  <p className="text-xs text-muted py-4 text-center">
                    No scent data. Run a simulation to see the field heatmap.
                  </p>
                ) : (
                  scentAggregates.map((agg) => {
                    const task = taskMap.get(agg.task_id);
                    if (!task) return null;

                    const scentTypes: ScentType[] = [
                      "Completion",
                      "Failure",
                      "Difficulty",
                      "Urgency",
                      "Progress",
                      "HelpWanted",
                    ];

                    return (
                      <div
                        key={agg.task_id}
                        className="p-3 rounded-lg bg-background/50 border border-border/50"
                      >
                        <p className="text-xs font-medium text-foreground mb-2 truncate">
                          {task.description.length > 55
                            ? `${task.description.slice(0, 55)}…`
                            : task.description}
                        </p>
                        <div className="flex flex-col gap-1.5">
                          {scentTypes.map((type) => {
                            const cfg = SCENT_CONFIG[type];
                            const value = agg[type] as number;
                            return (
                              <ScentBar
                                key={type}
                                label={cfg.label}
                                value={value}
                                color={cfg.color}
                              />
                            );
                          })}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </Card>

            {/* Session Panel */}
            <Card title="Swarm Session" icon={<Activity className="w-4 h-4" />}>
              {latestSession ? (
                <div className="flex flex-col gap-3">
                  {/* Session progress bar */}
                  <div>
                    <div className="flex items-center justify-between text-xs text-muted mb-1">
                      <span>Session Progress</span>
                      <span className="tabular-nums">
                        {latestSession.completed_tasks}/{latestSession.total_tasks}
                      </span>
                    </div>
                    <div className="h-2.5 rounded-full bg-slate-700/60 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          latestSession.status === "Completed"
                            ? "bg-emerald-500"
                            : latestSession.status === "Failed"
                            ? "bg-red-500"
                            : "bg-blue-500"
                        }`}
                        style={{
                          width: `${
                            latestSession.total_tasks > 0
                              ? (latestSession.completed_tasks / latestSession.total_tasks) * 100
                              : 0
                          }%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Session details */}
                  <div className="p-3 rounded-lg bg-background/50 border border-border/50 flex flex-col gap-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted">Domain</span>
                      <span className="text-xs font-semibold text-foreground">
                        {latestSession.domain}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted">Status</span>
                      <StatusBadge status={latestSession.status} />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted">Agents Used</span>
                      <span className="text-xs font-semibold text-foreground tabular-nums">
                        {latestSession.agents_used}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted">PARL Reward</span>
                      <span className="text-xs font-bold text-primary tabular-nums">
                        {latestSession.parl_reward > 0
                          ? latestSession.parl_reward.toFixed(2)
                          : "—"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted">Speedup</span>
                      <span className="text-xs font-semibold text-foreground tabular-nums">
                        {latestSession.theoretical_speedup}x
                      </span>
                    </div>
                  </div>

                  {/* Description */}
                  {latestSession.task_description && (
                    <p className="text-xs text-muted leading-relaxed">
                      {latestSession.task_description}
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-xs text-muted py-4 text-center">
                  No active session. Run a simulation to start a swarm.
                </p>
              )}
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

// ── Session status badge ────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string; dot: string }> = {
    Initializing: { bg: "bg-blue-500/20", text: "text-blue-400", dot: "bg-blue-500" },
    Running: { bg: "bg-emerald-500/20", text: "text-emerald-400", dot: "bg-emerald-500 animate-pulse" },
    Paused: { bg: "bg-yellow-500/20", text: "text-yellow-400", dot: "bg-yellow-500" },
    Completed: { bg: "bg-emerald-500/20", text: "text-emerald-400", dot: "bg-emerald-500" },
    Failed: { bg: "bg-red-500/20", text: "text-red-400", dot: "bg-red-500" },
    PartialSuccess: { bg: "bg-orange-500/20", text: "text-orange-400", dot: "bg-orange-500" },
  };
  const c = config[status] ?? config.Initializing;
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-[11px] font-medium px-2 py-0.5 rounded-full ${c.bg} ${c.text}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {status}
    </span>
  );
}
