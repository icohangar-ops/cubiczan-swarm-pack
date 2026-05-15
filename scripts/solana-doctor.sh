#!/usr/bin/env bash
set -euo pipefail

missing=0

for cmd in rustc solana anchor surfpool node yarn; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf "%-8s %s\n" "$cmd" "$($cmd --version 2>&1 | head -n 1)"
  else
    printf "%-8s missing\n" "$cmd"
    missing=1
  fi
done

if command -v solana >/dev/null 2>&1; then
  echo
  solana config get || true
fi

if [ "$missing" -ne 0 ]; then
  echo
  echo "Install the Solana Developer Platform CLI from https://solana.com/docs/intro/installation"
  exit 1
fi
