# Open Source Visibility Playbook

This playbook turns the repo-discovery work into concrete visibility moves.
The aim is not generic promotion; it is to join adjacent projects with useful,
specific contributions.

## Positioning

Cubiczan should be positioned as:

> Governed, auditable swarm coordination with zero-token stigmergy, policy
> gates, approval workflows, and traceable task DAGs.

That separates it from generic multi-agent runners.

## Repo Themes To Reference

- Agent governance: `open-agentic`, `cordum`, `reins`,
  `humanlayer/agentcontrolplane`.
- Swarm orchestration: `fcn06/swarm`, `desplega-ai/agent-swarm`,
  `open-multi-agent/open-multi-agent`, `joewinke/jat`.
- Fleet dashboards: `ChristianAlmurr/openclaw-dashboard`,
  `clawfleet/ClawFleet`.

## Outreach Moves

1. Open one documentation PR or issue in an adjacent governance repo.
   - Good angle: "Here is how Cubiczan models evidence thresholds and approval
     IDs; would a short interop example be useful?"
2. Add a README note comparing governed stigmergy to chat-based agent
   coordination.
   - Good angle: "Coordination tokens should be observable and minimized."
3. Publish a short technical post:
   - Title: "Governed swarms need audit trails before autonomy."
   - Include: zero-token coordination, policy gates, HMAC audit chains,
     approval-required actions, and DAG validation.
4. Create a small demo issue in Cubiczan:
   - "Demo: fail closed on weak evidence, then allow after human approval."
   - Link to `docs/GOVERNED_SWARM_CONTROLS.md`.

## Suggested README Snippet For Cross-Repo Mentions

```markdown
Related research: Cubiczan's governance layer was informed by open-source
agent-control and audit projects including Open Agentic, Cordum, Reins,
HumanLayer Agent Control Plane, and Open Multi-Agent. No upstream source code is
vendored; see ATTRIBUTIONS.md for links and license notes.
```

## What Not To Do

- Do not open vague "check out my project" issues.
- Do not copy code from upstream projects without license review.
- Do not claim compatibility until an adapter or test exists.
- Do not frame Cubiczan as replacing every framework; frame it as a governed
  coordination layer with strong autonomy controls.
