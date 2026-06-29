---
name: sync-codex-envs
description: Sync Codex `.codex/environments/environment.toml` files plus global Codex config files such as `~/.codex/AGENTS.md`, `~/.codex/keybindings.json`, and plugin or MCP entries in `~/.codex/config.toml` between local repo checkouts and another Mac or server over SSH. Use when the user wants to send, receive, copy, compare, refresh, or keep Codex Environment TOML configs, Codex instructions, keyboard shortcuts, plugin install/status entries, MCP server entries, or user skills in sync across machines such as this M4 Mac and DonPablo.
---

# Sync Codex Envs

Use this skill to synchronize repo-local Codex environment files:

```text
<repo>/.codex/environments/environment.toml
```

Also use this skill for these global Codex config files and user extension directories:

```text
~/.codex/AGENTS.md
~/.codex/keybindings.json
~/.codex/config.toml                 # plugin entries and MCP entries
~/.codex/skills/<skill-name>          # user-installed Codex skills, excluding .system
~/.agents/skills/<skill-name>         # legacy user-installed skills
```

## Workflow

0. Default action: before any sync, run the read-only diff helper and print its full output:
   ```bash
   /Users/td/.codex/skills/sync-codex-envs/scripts/diff_codex_configs.sh
   ```
   This includes repo environment TOMLs, global Codex config files, installed plugin config entries, standalone MCP server presence, plugin MCP override presence, and user-installed skills. Then ask the user how they want to proceed. Do not send or receive files until the user chooses a direction and scope.
1. Determine the direction for each repo:
   - `send`: copy local TOMLs to the remote machine.
   - `receive`: copy remote TOMLs to this machine.
2. Determine the remote SSH target. Default to `pablo@DonPabloMBP.local` when the user says DonPablo and gives no other host.
3. Determine repo names. If missing, ask which local repos to sync after discovering repos under `~/Code`.
4. For repo environment TOMLs, run `scripts/sync_env_tomls.py` with the chosen direction, remote, and repos. Use `--send-repo` and `--receive-repo` when one run needs mixed directions.
5. For global config files, use direct `ssh` and `scp` commands with a timestamped backup first.
6. For plugin differences, manage only the plugin entries the user names:
   - `[only-local]` or `[only-remote]` plugin install differences can be aligned with `codex plugin add` or `codex plugin remove` when the CLI is available on the target host.
   - `[different-status]` plugin differences are `enabled = true` / `enabled = false` values under the matching `[plugins."name@marketplace"]` table in `~/.codex/config.toml`. If `codex plugin --help` does not show a plugin enable/disable command, edit those TOML booleans directly after backing up the destination config.
   - On remote hosts, first check CLI availability with `ssh <remote> 'zsh -lc "command -v codex && codex plugin --help"'`; non-login SSH shells may not have `codex` on `PATH`. If unavailable, edit `~/.codex/config.toml` directly and validate TOML afterward.
7. For MCP differences, manage only the MCP entries the user names:
   - Standalone MCP servers live under `[mcp_servers.<name>]` in `~/.codex/config.toml`.
   - Plugin MCP overrides live under nested plugin tables such as `[plugins."name@marketplace".mcp_servers.<server>...]`.
   - Use `codex mcp add`, `codex mcp remove`, `codex mcp list`, and `codex mcp get` when available. If CLI commands are unavailable over SSH, edit only the requested TOML table(s) after backing up the destination config.
   - Treat MCP `env`, `http_headers`, bearer token env vars, API keys, and machine-specific paths as sensitive or host-specific. The diff helper intentionally checks MCP presence only and does not compare or print config fingerprints for same-name MCPs.
8. For user skill differences, copy only user-approved skill directories under `~/.codex/skills` or `~/.agents/skills`; never copy managed `~/.codex/skills/.system`.
9. Verify the output: the script validates TOML before overwriting, backs up destinations, and prints every copied path; direct global config sync should list and print the copied remote file. Plugin and MCP config edits must be validated as TOML on both sides and then verified by rerunning the read-only diff helper.

## Script

Use this read-only diff helper first by default. It compares repo environment TOMLs under `~/Code`, remote repo TOMLs under `/Users/pablo/Code`, remote Codex workspace TOMLs under `/Users/pablo/Documents/Dev/Codex`, `~/.codex/AGENTS.md`, `~/.codex/keybindings.json`, installed plugin config entries, standalone MCP server presence, plugin MCP override presence, and user-installed skills on both machines:

```bash
/Users/td/.codex/skills/sync-codex-envs/scripts/diff_codex_configs.sh
```

Optional target override:

```bash
/Users/td/.codex/skills/sync-codex-envs/scripts/diff_codex_configs.sh pablo@DonPabloMBP.local
```

After printing the diff, ask the user what to sync, if anything.

To compare only installed plugins, MCP entries, and user skills without checking environment TOMLs or global config files, run:

```bash
python3 /Users/td/.codex/skills/sync-codex-envs/scripts/diff_plugins_skills.py pablo@DonPabloMBP.local
```

This is read-only. It prints plugin entries, standalone MCP server presence, plugin MCP override presence from `~/.codex/config.toml`, and user skill directories from `~/.codex/skills` and `~/.agents/skills`, excluding Codex-managed `~/.codex/skills/.system`. MCP entries are presence-only: when the same MCP name exists on both machines, the helper does not report config or version differences.


## Plugin, MCP, And Skill Sync

Plugin state is tracked in `~/.codex/config.toml` under tables like:

```toml
[plugins."spreadsheets@openai-primary-runtime"]
enabled = true
```

Use `codex plugin add` and `codex plugin remove` when adding or removing plugin install entries and the CLI is available:

```bash
codex plugin add spreadsheets@openai-primary-runtime
codex plugin remove latex@openai-bundled
```

The current CLI exposes `plugin add`, `plugin list`, `plugin marketplace`, and `plugin remove`. If `codex plugin --help` still does not show plugin-specific enable/disable commands, sync `[different-status]` entries by backing up `~/.codex/config.toml`, changing only the requested plugin table's `enabled` boolean, validating TOML, and rerunning the read-only diff helper.

Local plugin status edit pattern:

```bash
cp ~/.codex/config.toml ~/.codex/config.toml.bak-$(date +%Y%m%d-%H%M%S)
python3 - <<'PY'
from pathlib import Path
import tomllib

path = Path.home() / ".codex" / "config.toml"
text = path.read_text()
# Edit only the requested [plugins."name@marketplace"] table(s), then validate:
tomllib.loads(text)
PY
```

Remote plugin status edit pattern:

```bash
ssh pablo@DonPabloMBP.local 'cp ~/.codex/config.toml ~/.codex/config.toml.bak-$(date +%Y%m%d-%H%M%S)'
ssh pablo@DonPabloMBP.local 'zsh -lc "command -v codex && codex plugin --help"'
```

If the remote `codex` command is unavailable in SSH, patch `~/.codex/config.toml` directly on the remote, copy it back or print it, validate it with local `python3`/`tomllib` when needed, and rerun:

```bash
/Users/td/.codex/skills/sync-codex-envs/scripts/diff_codex_configs.sh pablo@DonPabloMBP.local
```

For user skills, sync only explicit user-approved directories:

```bash
scp -r ~/.codex/skills/sync-codex-envs pablo@DonPabloMBP.local:~/.codex/skills/
```

Back up an existing destination skill directory before overwriting it. Do not copy `~/.codex/skills/.system`.

## MCP Sync

Standalone MCP server state is tracked in `~/.codex/config.toml` under tables like:

```toml
[mcp_servers.context7]
url = "https://mcp.context7.com/mcp"

[mcp_servers.context7.http_headers]
CONTEXT7_API_KEY = "..."
```

Plugin-specific MCP overrides can also appear under plugin tables:

```toml
[plugins."build-ios-apps@openai-curated".mcp_servers.xcodebuildmcp.tools.clean]
approval_mode = "approve"
```

Use `codex mcp` commands when the CLI is available:

```bash
codex mcp list
codex mcp get context7
codex mcp add context7 --url https://mcp.context7.com/mcp
codex mcp remove context7
```

For stdio servers, include the command after `--`; for HTTP servers, use `--url`. Add environment variables with `--env KEY=VALUE` only when the value is safe to copy to that host.

Remote MCP status pattern:

```bash
ssh pablo@DonPabloMBP.local 'zsh -lc "command -v codex && codex mcp list"'
```

If `codex mcp` is unavailable over SSH, back up `~/.codex/config.toml`, edit only the requested `[mcp_servers.<name>]` or plugin MCP override table, validate TOML, and rerun the read-only diff helper. The helper intentionally reports only `[only-local]` and `[only-remote]` MCP entries; it does not report `[different-config]` for same-name MCPs because paths, app versions, tokens, and runtime locations can legitimately differ by host. Do not print or copy MCP secrets unless the user explicitly asks to sync that named secret-bearing entry.

Prefer the bundled helper because it handles discovery, prompting, backups, SCP, and TOML validation:

```bash
python /Users/td/.codex/skills/sync-codex-envs/scripts/sync_env_tomls.py
```

Common non-interactive forms:

```bash
python /Users/td/.codex/skills/sync-codex-envs/scripts/sync_env_tomls.py --direction send --remote pablo@DonPabloMBP.local --repo mma-ai-swift-app --repo odds-monitoring
```

```bash
python /Users/td/.codex/skills/sync-codex-envs/scripts/sync_env_tomls.py --direction receive --remote pablo@DonPabloMBP.local --repo mma-ai-swift-app --repo odds-monitoring
```

Mixed directions in one run:

```bash
python /Users/td/.codex/skills/sync-codex-envs/scripts/sync_env_tomls.py --remote pablo@DonPabloMBP.local --send-repo mma-ai-swift-app --send-repo the-fight-predictor-agent --receive-repo mma-ai
```

Use `--dry-run` before live copies when checking paths:

```bash
python /Users/td/.codex/skills/sync-codex-envs/scripts/sync_env_tomls.py --direction send --remote pablo@DonPabloMBP.local --repo all --dry-run
```

## Global Config Files

For shell-only global config syncs, default to these commands when sending local config to DonPablo. Do not create `~/.codex` unless the user asks; this workflow assumes Codex already exists on the remote.

```bash
ssh pablo@DonPabloMBP.local 'if [ -f ~/.codex/AGENTS.md ]; then cp ~/.codex/AGENTS.md ~/.codex/AGENTS.md.bak-$(date +%Y%m%d-%H%M%S); fi'
scp ~/.codex/AGENTS.md pablo@DonPabloMBP.local:~/.codex/AGENTS.md
ssh pablo@DonPabloMBP.local 'ls -l ~/.codex/AGENTS.md && sed -n "1,220p" ~/.codex/AGENTS.md'
```

```bash
ssh pablo@DonPabloMBP.local 'if [ -f ~/.codex/keybindings.json ]; then cp ~/.codex/keybindings.json ~/.codex/keybindings.json.bak-$(date +%Y%m%d-%H%M%S); fi'
scp ~/.codex/keybindings.json pablo@DonPabloMBP.local:~/.codex/keybindings.json
ssh pablo@DonPabloMBP.local 'ls -l ~/.codex/keybindings.json && sed -n "1,220p" ~/.codex/keybindings.json'
```

For receive direction, reverse the `scp` source and destination and back up the local destination before overwriting.

## Defaults

- Local code root: `~/Code`
- Remote code root: `/Users/pablo/Code`
- Remote Codex workspace root: `/Users/pablo/Documents/Dev/Codex` (`REMOTE_CODEX_WORKSPACE_ROOT` overrides this for `diff_codex_configs.sh`)
- Remote target for DonPablo: `pablo@DonPabloMBP.local`
- Environment destination backups: `environment.toml.bak-YYYYmmdd-HHMMSS`
- Global config destination backups: `<filename>.bak-YYYYmmdd-HHMMSS`

## Notes

- Do not sync `.env` secrets with this skill; sync only Codex Environment TOML files and the explicit global Codex config files above.
- If the user asks for shell-only commands instead of using the helper, give explicit `scp` commands for each repo or global config file and include a backup command first.
