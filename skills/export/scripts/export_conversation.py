#!/usr/bin/env python3

import json
import sys
from pathlib import Path

session_id = sys.argv[1]
matches = sorted(Path("~/.codex/sessions").expanduser().glob(f"*/*/*/*{session_id}*"))

if not matches:
    raise SystemExit(1)

for match in matches:
    lines = []
    seen = set()
    for line in match.open():
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
    out = Path(f"~/Documents/Exports/{match.stem[28:]}.md").expanduser()
    out.write_text("\n---\n\n".join(lines).strip() + "\n")
    print(out)
