---
name: sync-codex-envs
description: Sync Codex `.codex/environments/environment.toml` files between local repo checkouts and another Mac or server over SSH. Use when the user wants to send, receive, copy, compare, refresh, or keep Codex Environment TOML configs in sync across machines.
---

# Sync Codex Envs

Use this skill to synchronize repo-local Codex environment files:

```text
<repo>/.codex/environments/environment.toml
```

## Workflow

1. Determine the direction for each repo:
   - `send`: copy local TOMLs to the remote machine.
   - `receive`: copy remote TOMLs to this machine.
2. Determine the remote SSH target. Ask for it when the user does not provide one.
3. Determine repo names. If missing, ask which local repos to sync after discovering repos under `~/Code`.
4. Run `scripts/sync_env_tomls.py` with the chosen direction, remote, and repos. Use `--send-repo` and `--receive-repo` when one run needs mixed directions.
5. Verify the output: the script validates TOML before overwriting, backs up destinations, and prints every copied path.

## Script

Prefer the bundled helper because it handles discovery, prompting, backups, SCP, and TOML validation:

```bash
python ~/.codex/skills/sync-codex-envs/scripts/sync_env_tomls.py
```

Common non-interactive forms:

```bash
python ~/.codex/skills/sync-codex-envs/scripts/sync_env_tomls.py --direction send --remote user@host.local --repo example-app --repo example-api
```

```bash
python ~/.codex/skills/sync-codex-envs/scripts/sync_env_tomls.py --direction receive --remote user@host.local --repo example-app --repo example-api
```

Mixed directions in one run:

```bash
python ~/.codex/skills/sync-codex-envs/scripts/sync_env_tomls.py --remote user@host.local --send-repo example-app --send-repo example-api --receive-repo example-model
```

Use `--dry-run` before live copies when checking paths:

```bash
python ~/.codex/skills/sync-codex-envs/scripts/sync_env_tomls.py --direction send --remote user@host.local --repo all --dry-run
```

## Defaults

- Local code root: `~/Code`
- Remote code root: `Code` relative to the SSH user's home
- Remote target: required as `--remote` or prompted interactively
- Destination backups: `environment.toml.bak-YYYYmmdd-HHMMSS`

## Notes

- Do not sync `.env` secrets with this skill; it is only for Codex Environment TOML files.
- If the user asks for shell-only commands instead of using the helper, give explicit `scp` commands for each repo and include a backup command first.
