"""Governance metrics for swarm risk controls.

Attribution: Heterogeneity Score concept adapted from Georgios Fradelos, PhD,
"Finance-Grade Assurance for Agentic AI", Geneva, January 11, 2026, local
source AI Governance papers/ssrn-6306980.pdf.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class HeterogeneityReport:
    score: float
    families: list[str]
    dominant_family: str
    dominant_share: float
    attribution: str = (
        "Adapted from Georgios Fradelos, PhD, Finance-Grade Assurance for "
        "Agentic AI, Geneva, January 11, 2026, local source "
        "AI Governance papers/ssrn-6306980.pdf."
    )


def compute_heterogeneity_score(model_names: list[str]) -> HeterogeneityReport:
    if not model_names:
        return HeterogeneityReport(0.0, [], "none", 1.0)
    families = [_model_family(name) for name in model_names]
    counts = Counter(families)
    dominant_family, dominant_count = counts.most_common(1)[0]
    dominant_share = dominant_count / len(families)
    unique_ratio = len(counts) / len(families)
    anti_monoculture = 1.0 - dominant_share
    score = round((0.65 * unique_ratio) + (0.35 * anti_monoculture), 3)
    return HeterogeneityReport(score, families, dominant_family, round(dominant_share, 3))


def _model_family(model_name: str) -> str:
    name = (model_name or "unknown").lower()
    if any(marker in name for marker in ["gpt", "openai", "o3", "o4"]):
        return "openai"
    if any(marker in name for marker in ["claude", "anthropic"]):
        return "anthropic"
    if "qwen" in name:
        return "qwen"
    if "deepseek" in name:
        return "deepseek"
    if "llama" in name or "meta" in name:
        return "llama"
    if "gemini" in name or "google" in name:
        return "google"
    if "mistral" in name or "mixtral" in name:
        return "mistral"
    return name.split(":", 1)[0].split("-", 1)[0] or "unknown"
