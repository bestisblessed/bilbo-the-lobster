---
name: threads-summarize
description: Summarize selected local Codex app threads into SUMMARY.md for the current project. Use when the user asks for /threads-summarize, wants reports over one or more Codex session ids, asks to read prior thread conversations, compare related threads, or summarize what happened, what was applied, where each thread left off, and overall priority/interference across threads.
---

# Threads Summarize

## First Response

If the user invokes this skill without session ids, ask which session ids to include before doing extraction or summarization.

## Workflow

1. Run the preparation script from the project root. By default it writes extracted message files to an OS temp directory and prints their paths:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/threads-summarize/scripts/prepare_threads_summary.py" SESSION_ID...
```

2. Use the printed `messages_path` files as the evidence source for summaries.
3. For multiple sessions, spawn one subagent per `messages_path` when subagents are available and the user permits or requested subagents. Ask each subagent for a concise Markdown section with:
   - session id and app-facing name/title
   - what the thread was about
   - what was done or applied
   - where the thread left off
   - notable artifacts/files
   - relationship to the other requested threads, if visible
4. Write the final report to `SUMMARY.md` in the project root. Include:
   - a top-level title
   - one section per requested thread
   - an overall summary comparing related work, conflicts/interference, suggested priority, and useful next steps
5. Verify `SUMMARY.md` exists and briefly inspect it before reporting completion.

## Notes

- Use `git rev-parse --show-toplevel` when available; otherwise use `pwd`.
- Treat `${CODEX_HOME:-$HOME/.codex}/state_5.sqlite` as the source of app-facing thread metadata.
- Locate transcripts under `${CODEX_HOME:-$HOME/.codex}/sessions`.
- Do not paste raw session logs into the final answer. Save the report as `SUMMARY.md` and summarize the result.
