"""
Streaming debate CLI — the console counterpart of swarmchat's real-time debate
view, ported into this repo's Python orchestrator stack.

It drives the existing ``ConsensusEngine.stream_consensus`` generator and prints
each debate turn as it happens (agents take turns across rounds, you watch the
positions and confidences arrive live), then prints the final consensus.

Usage:
    python -m orchestrator.debate_stream "Should we acquire CompanyX?"
    python orchestrator/debate_stream.py "Topic" --cluster-size 4 --json

With ``--json`` it emits one JSON event per line (newline-delimited JSON),
which is convenient for piping into other tools or a thin SSE relay.

Agent models are configured via the same env vars ConsensusEngine reads
(AGENT_MODEL_1_* … / LLM_*). See .env.example.
"""

import argparse
import json
import sys

try:
    from consensus import ConsensusEngine
except ImportError:  # when imported as part of the orchestrator package
    from .consensus import ConsensusEngine


# Per-agent colors for the human-readable view (falls back to plain text if the
# terminal doesn't support ANSI — colors are harmless escape codes otherwise).
_COLORS = ["\033[31m", "\033[34m", "\033[32m", "\033[35m", "\033[36m"]
_RESET = "\033[0m"
_DIM = "\033[2m"
_BOLD = "\033[1m"


def _color_for(agent_id: str) -> str:
    # Stable color per agent id without needing to know them in advance.
    return _COLORS[hash(agent_id) % len(_COLORS)]


def render_human(event: dict) -> None:
    """Print one streamed debate event in a readable, live form."""
    etype = event.get("type")

    if etype == "debate_start":
        print(f"{_BOLD}=== DEBATE: {event['task']} ==={_RESET}")
        print(
            f"{_DIM}cluster={event['cluster_size']} "
            f"max_rounds={event['max_rounds']} "
            f"threshold={event['threshold']} "
            f"heterogeneity={event['heterogeneity_score']:.2f}{_RESET}"
        )

    elif etype == "round_start":
        print(f"\n{_BOLD}--- Round {event['round']}/{event['total_rounds']} ---{_RESET}")

    elif etype == "agent_vote":
        color = _color_for(event["agent_id"])
        tag = " [CONTRARIAN]" if event["is_contrarian"] else ""
        print(
            f"{color}{_BOLD}{event['agent_id']} ({event['model_name']}){tag}{_RESET} "
            f"{_DIM}conf={event['confidence']:.2f}{_RESET}"
        )
        print(f"  {event['position']}")
        if event.get("reasoning"):
            print(f"  {_DIM}↳ {event['reasoning']}{_RESET}")

    elif etype == "round_end":
        state = "CONSENSUS" if event["consensus_reached"] else "no consensus yet"
        print(
            f"{_DIM}round consensus score = {event['consensus_score']:.3f} "
            f"({state}){_RESET}"
        )

    elif etype == "debate_end":
        r = event["result"]
        print(f"\n{_BOLD}=== FINAL CONSENSUS ==={_RESET}")
        print(f"Position : {r['final_position']}")
        print(f"Score    : {r['consensus_score']:.3f}")
        print(f"Rounds   : {r['debate_rounds']}")
        print(f"Dissent  : {r['dissenting_count']}/{r['total_votes']}")
        if r["escalate_to_human"]:
            print(f"{_BOLD}⚠ Escalated to human review{_RESET}")

    elif etype == "error":
        print(f"{_BOLD}ERROR:{_RESET} {event.get('message')}", file=sys.stderr)


def render_json(event: dict) -> None:
    """Emit one JSON event per line (drop the internal result object)."""
    payload = {k: v for k, v in event.items() if k != "_result_obj"}
    print(json.dumps(payload), flush=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Stream an adversarial consensus debate.")
    parser.add_argument("task", help="The topic/task to debate")
    parser.add_argument("--cluster-size", type=int, default=4, help="Agents per cluster")
    parser.add_argument(
        "--json", action="store_true",
        help="Emit newline-delimited JSON events instead of the readable view",
    )
    args = parser.parse_args(argv)

    engine = ConsensusEngine()
    render = render_json if args.json else render_human

    try:
        for event in engine.stream_consensus(args.task, cluster_size=args.cluster_size):
            render(event)
    except Exception as e:  # keep the CLI from dumping a traceback at the user
        if args.json:
            render_json({"type": "error", "message": str(e)})
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
