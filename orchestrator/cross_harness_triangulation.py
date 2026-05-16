"""Compatibility shim for the former Cross-Harness Triangulation module name."""

try:
    from .cross_harness_scaffolder import *  # noqa: F401,F403
except ImportError:  # pragma: no cover - supports direct module-path imports in tests/scripts.
    from cross_harness_scaffolder import *  # type: ignore # noqa: F401,F403
