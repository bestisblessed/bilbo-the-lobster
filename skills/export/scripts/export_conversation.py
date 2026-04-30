#!/usr/bin/env python3

import json
import os
import re
import sys
from pathlib import Path

session_id = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CODEX_THREAD_ID")
if not session_id:
    raise SystemExit("Missing session id. Pass one explicitly or set CODEX_THREAD_ID.")

if not re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", session_id):
    raise SystemExit("Session id must be a UUID.")

sessions_dir = Path.home() / ".codex" / "sessions"
matches = sorted(sessions_dir.glob(f"*/*/*/rollout-*-{session_id}.jsonl"))

if not matches:
    raise SystemExit(f"No Codex session found for {session_id}.")

match = matches[-1]
lines = []
seen = set()
for line in match.open(encoding="utf-8"):
    payload = json.loads(line).get("payload", {})
    if payload.get("type") != "message" or payload.get("role") not in {"user", "assistant"}:
        continue
    text = "\n".join(x.get("text", "") for x in payload.get("content", []) if x.get("text")).strip()
    if not text or text.startswith("# AGENTS.md instructions") or text.startswith("<turn_aborted>") or text.startswith("<skill>"):
        continue
    block = f"**{payload['role'].title()}**\n\n{text}\n"
    if block not in seen:
        lines.append(block)
        seen.add(block)

export_dir = Path.home() / "Documents" / "Exports"
export_dir.mkdir(parents=True, exist_ok=True)
out = export_dir / f"{session_id}.md"
out.unlink(missing_ok=True)
out.write_text("\n---\n\n".join(lines).strip() + "\n", encoding="utf-8")
print(out)
