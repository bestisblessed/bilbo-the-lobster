---
name: threads-list
description: List Codex app threads for the current project, including app-facing thread names, session ids, update times, titles, and cwd filtering. Use when the user asks for /threads-list, current project thread ids, Codex session ids, matching threads to the Codex app sidebar, or a reusable shell command for identifying local Codex threads.
---

# Threads List

## Quick Start

Run the bundled script from the project directory the user cares about:

```bash
bash "${CODEX_HOME:-$HOME/.codex}/skills/threads-list/scripts/threads-list.sh"
```

Default output prints one non-archived thread per line:

```text
Thread Name: session-id    updated-local-time
```

Pass `--all` to include archived threads, `--cwd PATH` to inspect a different project, and `--details` to include the database title after the app-facing thread name.

## Notes

- Use `git rev-parse --show-toplevel` when available; otherwise use `pwd`.
- Treat `${CODEX_HOME:-$HOME/.codex}/state_5.sqlite` as the source of truth for cwd-filtered thread records.
- Use `${CODEX_HOME:-$HOME/.codex}/session_index.jsonl` only to recover the latest app-facing thread name, because it does not store cwd.
- If the database files are missing, report that local Codex thread metadata is unavailable rather than guessing from session JSONL files.
