#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: threads-list.sh [--cwd PATH] [--all] [--details]

List Codex app threads for the current project.

Options:
  --cwd PATH   Use PATH instead of the current git root or current directory.
  --all        Include archived threads.
  --details    Also print the database title after the updated time.
USAGE
}

cwd=""
include_archived=0
details=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cwd)
      [[ $# -ge 2 ]] || { echo "missing value for --cwd" >&2; exit 2; }
      cwd="$2"
      shift 2
      ;;
    --all)
      include_archived=1
      shift
      ;;
    --details)
      details=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$cwd" ]]; then
  cwd="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

codex_home="${CODEX_HOME:-$HOME/.codex}"
db="$codex_home/state_5.sqlite"
index="$codex_home/session_index.jsonl"

[[ -f "$db" ]] || { echo "Codex thread database not found: $db" >&2; exit 1; }
command -v sqlite3 >/dev/null || { echo "sqlite3 is required" >&2; exit 1; }

sql_cwd="${cwd//\'/\'\'}"
archive_filter="and archived = 0"
if [[ "$include_archived" -eq 1 ]]; then
  archive_filter=""
fi

sqlite3 -separator $'\t' "$db" \
  "select id, datetime(updated_at, 'unixepoch', 'localtime'), title
   from threads
   where cwd = '$sql_cwd' $archive_filter
   order by updated_at desc;" |
while IFS=$'\t' read -r id updated title; do
  name=""
  if [[ -f "$index" ]] && command -v jq >/dev/null; then
    name="$(jq -r --arg id "$id" 'select(.id == $id) | .thread_name' "$index" | tail -1)"
  fi
  [[ -n "$name" && "$name" != "null" ]] || name="$title"

  if [[ "$details" -eq 1 ]]; then
    printf '%s: %s\t%s\t%s\n' "$name" "$id" "$updated" "$title"
  else
    printf '%s: %s\t%s\n' "$name" "$id" "$updated"
  fi
done
