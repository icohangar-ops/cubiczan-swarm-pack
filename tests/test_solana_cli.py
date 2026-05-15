import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestrator"))

from solana_cli import SolanaCLI, SolanaPolicy, classify_solana_action  # noqa: E402


def test_read_only_mainnet_command_is_allowed_without_approval() -> None:
    plan = SolanaPolicy(solana_binary="solana").plan(
        ["balance", "11111111111111111111111111111111"],
        cluster="mainnet-beta",
    )

    assert plan.allowed is True
    assert plan.requires_approval is False
    assert plan.action_type == "read"
    assert plan.command_preview[:3] == ["solana", "--url", "mainnet-beta"]


def test_mainnet_transfer_requires_human_approval_id() -> None:
    blocked = SolanaPolicy().plan(
        ["transfer", "11111111111111111111111111111111", "0.01"],
        cluster="mainnet-beta",
    )

    assert blocked.allowed is False
    assert blocked.requires_approval is True

    approved = SolanaPolicy().plan(
        ["transfer", "11111111111111111111111111111111", "0.01"],
        cluster="mainnet-beta",
        approved_by_human=True,
        approval_id="approval-123",
    )

    assert approved.allowed is True
    assert approved.requires_approval is True
    assert approved.approval_id == "approval-123"


def test_agent_cannot_pass_keypair_or_config_flags() -> None:
    plan = SolanaPolicy().plan(["balance", "--keypair", "id.json"], cluster="devnet")

    assert plan.allowed is False
    assert plan.action_type == "secret_access"
    assert "credential" in plan.reason.lower()


def test_devnet_airdrop_is_sandbox_allowed() -> None:
    plan = SolanaPolicy().plan(
        ["airdrop", "1", "11111111111111111111111111111111"],
        cluster="devnet",
    )

    assert plan.allowed is True
    assert plan.requires_approval is False
    assert plan.action_type == "faucet"


def test_execute_defaults_to_dry_run() -> None:
    result = SolanaCLI(policy=SolanaPolicy(solana_binary="solana")).execute(
        ["balance", "11111111111111111111111111111111"],
        cluster="devnet",
    )

    assert result.executed is False
    assert result.dry_run is True
    assert result.error is None


def test_classifies_program_mutation_as_deploy_gate() -> None:
    assert classify_solana_action(["program", "show", "Example111111111111111111111111111111111"]) == "read"
    assert classify_solana_action(["program", "close", "Example111111111111111111111111111111111"]) == "deploy"
