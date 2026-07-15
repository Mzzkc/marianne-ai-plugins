#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 QUERY" >&2
  exit 2
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
query="$*"

if command -v rg >/dev/null 2>&1; then
  rg -n -i --glob '!tools/search.sh' -- "$query" "$root/index/chunks.jsonl" "$root" || true
else
  grep -Rni --exclude=search.sh -- "$query" "$root/index/chunks.jsonl" "$root" || true
fi

