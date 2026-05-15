"""Guarded Solana CLI capability for swarm agents.

The wrapper is intentionally conservative: agents can plan Solana CLI actions,
run read-only commands, and use local/devnet workflows, while mainnet writes and
program deployments require an explicit human approval id.

References:
- Solana Foundation, "Quick Installation", https://solana.com/docs/intro/installation
- Solana Foundation, "Solana CLI Basics",
  https://solana.com/docs/intro/installation/solana-cli-basics
- Solana Foundation, "Anchor CLI Basics",
  https://solana.com/docs/intro/installation/anchor-cli-basics
- Solana Foundation, "Surfpool CLI Basics",
  https://solana.com/docs/intro/installation/surfpool-cli-basics
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from typing import Any


READ_ONLY_COMMANDS = {
    "account",
    "address",
    "balance",
    "block",
    "block-height",
    "cluster-date",
    "cluster-version",
    "confirm",
    "epoch",
    "epoch-info",
    "fees",
    "genesis-hash",
    "inflation",
    "largest-accounts",
    "leader-schedule",
    "logs",
    "ping",
    "program",
    "slot",
    "slot-leaders",
    "supply",
    "transaction",
    "validators",
    "vote-account",
}

PROGRAM_READ_SUBCOMMANDS = {"show", "dump"}
CONFIG_READ_SUBCOMMANDS = {"get"}
FAUCET_COMMANDS = {"airdrop"}
DEPLOY_COMMANDS = {"deploy"}
WRITE_COMMANDS = {
    "allocate-address",
    "assign",
    "authorize-nonce-account",
    "create-address-with-seed",
    "create-nonce-account",
    "create-stake-account",
    "create-vote-account",
    "deactivate-stake",
    "delegate-stake",
    "nonce",
    "program",
    "stake-authorize",
    "stake-authorize-checked",
    "stake-set-lockup",
    "transfer",
    "vote-authorize-voter",
    "vote-authorize-withdrawer",
    "withdraw-from-nonce-account",
    "withdraw-stake",
}

FORBIDDEN_AGENT_FLAGS = {"--keypair", "-k", "--config"}

CLUSTER_URLS = {
    "localnet": "localhost",
    "localhost": "localhost",
    "devnet": "devnet",
    "testnet": "testnet",
    "mainnet": "mainnet-beta",
    "mainnet-beta": "mainnet-beta",
}


@dataclass(frozen=True)
class SolanaCommandPlan:
    args: list[str]
    cluster: str
    normalized_cluster: str
    action_type: str
    allowed: bool
    requires_approval: bool
    reason: str
    command_preview: list[str]
    approval_id: str | None = None
    attribution: str = (
        "Solana CLI policy references Solana Foundation installation, CLI, "
        "Anchor, and Surfpool documentation."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "args": self.args,
            "cluster": self.cluster,
            "normalized_cluster": self.normalized_cluster,
            "action_type": self.action_type,
            "allowed": self.allowed,
            "requires_approval": self.requires_approval,
            "reason": self.reason,
            "command_preview": self.command_preview,
            "approval_id": self.approval_id,
            "attribution": self.attribution,
        }


@dataclass(frozen=True)
class SolanaExecutionResult:
    plan: SolanaCommandPlan
    executed: bool
    dry_run: bool
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan": self.plan.to_dict(),
            "executed": self.executed,
            "dry_run": self.dry_run,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "metadata": self.metadata,
        }


class SolanaPolicy:
    """Classify and gate Solana CLI commands for agent use."""

    def __init__(self, solana_binary: str | None = None) -> None:
        self.solana_binary = solana_binary or os.getenv("SOLANA_CLI_BIN", "solana")

    def plan(
        self,
        args: list[str],
        cluster: str = "devnet",
        approved_by_human: bool = False,
        approval_id: str | None = None,
    ) -> SolanaCommandPlan:
        clean_args = [str(arg) for arg in args if str(arg).strip()]
        normalized_cluster = self._normalize_cluster(cluster)
        command_preview = [self.solana_binary, "--url", normalized_cluster, *clean_args]

        if not clean_args:
            return self._blocked(clean_args, cluster, normalized_cluster, "unknown", command_preview, "Missing Solana CLI arguments.")

        if normalized_cluster not in {"localhost", "devnet", "testnet", "mainnet-beta"}:
            return self._blocked(clean_args, cluster, normalized_cluster, "unknown", command_preview, "Unsupported Solana cluster.")

        forbidden_flags = sorted(set(clean_args) & FORBIDDEN_AGENT_FLAGS)
        if forbidden_flags:
            return self._blocked(
                clean_args,
                cluster,
                normalized_cluster,
                "secret_access",
                command_preview,
                f"Agents cannot provide credential/config flags: {', '.join(forbidden_flags)}.",
            )

        action_type = classify_solana_action(clean_args)
        requires_approval = self._requires_approval(action_type, normalized_cluster)

        if requires_approval and not (approved_by_human and approval_id):
            return SolanaCommandPlan(
                clean_args,
                cluster,
                normalized_cluster,
                action_type,
                False,
                True,
                "Human approval with an approval_id is required for this Solana action.",
                command_preview,
                approval_id,
            )

        if action_type == "unsupported":
            return self._blocked(clean_args, cluster, normalized_cluster, action_type, command_preview, "Command is not in the Solana allowlist.")

        return SolanaCommandPlan(
            clean_args,
            cluster,
            normalized_cluster,
            action_type,
            True,
            requires_approval,
            "Command is allowed by Solana swarm policy.",
            command_preview,
            approval_id,
        )

    def _normalize_cluster(self, cluster: str) -> str:
        return CLUSTER_URLS.get((cluster or "devnet").lower(), (cluster or "devnet").lower())

    def _requires_approval(self, action_type: str, normalized_cluster: str) -> bool:
        if action_type in {"read", "config_read"}:
            return False
        if action_type == "faucet":
            return normalized_cluster not in {"localhost", "devnet"}
        if normalized_cluster == "localhost":
            return False
        return True

    def _blocked(
        self,
        args: list[str],
        cluster: str,
        normalized_cluster: str,
        action_type: str,
        command_preview: list[str],
        reason: str,
    ) -> SolanaCommandPlan:
        return SolanaCommandPlan(
            args,
            cluster,
            normalized_cluster,
            action_type,
            False,
            False,
            reason,
            command_preview,
        )


class SolanaCLI:
    """Execute Solana CLI commands through the swarm policy gate."""

    def __init__(self, policy: SolanaPolicy | None = None, timeout_seconds: int = 30) -> None:
        self.policy = policy or SolanaPolicy()
        self.timeout_seconds = timeout_seconds

    def plan(
        self,
        args: list[str],
        cluster: str = "devnet",
        approved_by_human: bool = False,
        approval_id: str | None = None,
    ) -> SolanaCommandPlan:
        return self.policy.plan(args, cluster, approved_by_human, approval_id)

    def execute(
        self,
        args: list[str],
        cluster: str = "devnet",
        approved_by_human: bool = False,
        approval_id: str | None = None,
        dry_run: bool = True,
    ) -> SolanaExecutionResult:
        plan = self.plan(args, cluster, approved_by_human, approval_id)
        if not plan.allowed:
            return SolanaExecutionResult(plan, executed=False, dry_run=dry_run, error=plan.reason)
        if dry_run:
            return SolanaExecutionResult(
                plan,
                executed=False,
                dry_run=True,
                metadata={"message": "Dry run only; no Solana CLI process was started."},
            )
        if os.getenv("SOLANA_CLI_EXECUTION_ENABLED", "0") != "1":
            return SolanaExecutionResult(
                plan,
                executed=False,
                dry_run=False,
                error="Set SOLANA_CLI_EXECUTION_ENABLED=1 to permit real Solana CLI execution.",
            )

        try:
            completed = subprocess.run(
                plan.command_preview,
                capture_output=True,
                check=False,
                text=True,
                timeout=self.timeout_seconds,
            )
        except FileNotFoundError:
            return SolanaExecutionResult(plan, executed=False, dry_run=False, error="Solana CLI binary was not found.")
        except subprocess.TimeoutExpired as exc:
            return SolanaExecutionResult(
                plan,
                executed=True,
                dry_run=False,
                error=f"Solana CLI command timed out after {self.timeout_seconds}s.",
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
            )

        return SolanaExecutionResult(
            plan,
            executed=True,
            dry_run=False,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


def classify_solana_action(args: list[str]) -> str:
    """Return read/write/deploy/faucet/config_read/unsupported for a solana command."""
    if not args:
        return "unsupported"

    command = args[0].lower()
    subcommand = args[1].lower() if len(args) > 1 else ""

    if command == "config" and subcommand in CONFIG_READ_SUBCOMMANDS:
        return "config_read"
    if command == "program":
        if subcommand in PROGRAM_READ_SUBCOMMANDS:
            return "read"
        return "deploy"
    if command in DEPLOY_COMMANDS:
        return "deploy"
    if command in FAUCET_COMMANDS:
        return "faucet"
    if command in WRITE_COMMANDS:
        return "write"
    if command in READ_ONLY_COMMANDS:
        return "read"
    return "unsupported"
