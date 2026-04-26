---
name: export-conversation
description: Export a Codex session JSONL from ~/.codex/sessions into a clean Markdown transcript in ~/Documents/Exports. Use when the user wants to export, save, or convert a Codex conversation by session id.
---

# Export Conversation

Run `scripts/export_conversation.py <session-id>`.

Use the raw session id, for example:

```bash
scripts/export_conversation.py 019dc927-dac9-7f23-b313-917d776d189e
```

The script reads from `~/.codex/sessions` and writes:

`~/Documents/Exports/<session-id>.md`

Print the saved path after running it.

**Make sure `~/Documents/Exports` already exists before running the script.**