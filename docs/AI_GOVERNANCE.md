# AI Governance Controls

The swarm now computes a Heterogeneity Score for every consensus cluster. This
flags model monoculture risk when many agents share the same model family and may
therefore fail in correlated ways.

Runtime behavior:

- `ConsensusResult.heterogeneity_score` records the score.
- `ConsensusResult.model_families` records normalized model families.
- `MIN_HETEROGENEITY_SCORE` controls the escalation threshold.
- A low score escalates to human review even when the LMSR consensus score is high.

Attribution:

- Heterogeneity Score and model-monoculture risk concepts adapted from Georgios
  Fradelos, PhD, *Finance-Grade Assurance for Agentic AI: Verifiable Governance,
  Systemic Risk Mitigation, and Sustainability/Compute Accounting Architecture
  for Banks, Insurers, and Major Financial Services Providers*, Geneva, January
  11, 2026. Local source: `AI Governance papers/ssrn-6306980.pdf`.
- Governance/audit role separation and short-cycle operating cadence concepts
  adapted from Georgios Fradelos, PhD, *The Honey Badger Management Framework
  for Human-AI Hybrid Organizations: A Proxy Validation and Integration
  Analysis*, Geneva, January 6, 2026. Local source:
  `AI Governance papers/ssrn-6306679.pdf`.
