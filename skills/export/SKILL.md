---
name: export
description: Export a Codex session JSONL from ~/.codex/sessions into a clean Markdown transcript in ~/Documents/Exports. Use when the user wants to export, save, or convert the current Codex conversation or another conversation by session id.
---

# Export Conversation

Run `scripts/export_conversation.py`.

This exports the current chat by default using the Codex thread id from the environment.

To export a different conversation, pass a raw session id, for example:

```bash
scripts/export_conversation.py 019dc927-dac9-7f23-b313-917d776d189e
```

The script reads from `~/.codex/sessions` and writes:

`~/Documents/Exports/<session-id>.md`

The script creates `~/Documents/Exports` when needed.

Print the saved path after running it.

## Local Scope

This skill only reads local Codex session JSONL files under:

`~/.codex/sessions`

This skill only writes Markdown exports under:

`~/Documents/Exports`

It makes no network calls, reads no credentials, installs no packages, and downloads no external files.
