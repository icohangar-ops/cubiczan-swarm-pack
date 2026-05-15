# Solana CLI Integration

This repo exposes the Solana Developer Platform CLI as a guarded swarm
capability. The goal is to let agents inspect Solana state, prepare transaction
plans, run local/devnet workflows, and surface mainnet actions for human
approval without giving agents raw wallet material.

## Attribution

Implementation guidance references the official Solana documentation:

- Solana Foundation, "Quick Installation", https://solana.com/docs/intro/installation
- Solana Foundation, "Solana CLI Basics", https://solana.com/docs/intro/installation/solana-cli-basics
- Solana Foundation, "Anchor CLI Basics", https://solana.com/docs/intro/installation/anchor-cli-basics
- Solana Foundation, "Surfpool CLI Basics", https://solana.com/docs/intro/installation/surfpool-cli-basics

## Install And Verify

Install the Solana Developer Platform CLI using the official installer, then run
one of the repo-local doctor scripts:

```bash
bash scripts/solana-doctor.sh
```

```powershell
.\scripts\solana-doctor.ps1
```

The scripts check for `rustc`, `solana`, `anchor`, `surfpool`, `node`, and
`yarn`, then print the active Solana CLI config.

## Guardrail Model

The swarm wrapper lives in `orchestrator/solana_cli.py`.

Default policy:

- Read-only commands are allowed on `localhost`, `devnet`, `testnet`, and
  `mainnet-beta`.
- `airdrop` is allowed only on `localhost` and `devnet`.
- Writes and program mutations are allowed on `localhost`.
- Writes, deploys, and program mutations on `devnet`, `testnet`, or
  `mainnet-beta` require `approved_by_human=true` and an `approval_id`.
- Agents cannot pass `--keypair`, `-k`, or `--config`.
- Real execution is disabled unless `SOLANA_CLI_EXECUTION_ENABLED=1` is set.
- API execution defaults to dry-run.

This keeps private keys and config paths outside agent control. Wallets should
live in a vault or operator-managed filesystem path, not in Git and not in agent
prompts.

## API Endpoints

Plan a command without executing it:

```bash
curl -X POST http://localhost:5002/api/swarm/solana/plan \
  -H "Content-Type: application/json" \
  -d '{"cluster":"devnet","args":["balance","11111111111111111111111111111111"]}'
```

Dry-run an allowed command:

```bash
curl -X POST http://localhost:5002/api/swarm/solana/execute \
  -H "Content-Type: application/json" \
  -d '{"cluster":"devnet","args":["balance","11111111111111111111111111111111"]}'
```

Approved mainnet write plan:

```bash
curl -X POST http://localhost:5002/api/swarm/solana/plan \
  -H "Content-Type: application/json" \
  -d '{
    "cluster": "mainnet-beta",
    "args": ["transfer", "11111111111111111111111111111111", "0.01"],
    "approved_by_human": true,
    "approval_id": "approval-123"
  }'
```

## Agent Use Cases

- Verify wallet balances before a finance or treasury task.
- Check transaction confirmation status.
- Read program/account state for research tasks.
- Prepare Solana transaction plans for approval.
- Run localnet/devnet swarm simulations with Surfpool.
- Later: anchor audit hashes or consensus proof digests after approval.

## Explicit Non-Goals

- No keypair generation by agents.
- No keypair paths in requests.
- No autonomous mainnet transfers.
- No program deployment without explicit human approval.
- No confidential content on-chain; only hashes or public metadata should be
  considered for future proof anchoring.
