---
name: sync-codex-envs
description: Sync Codex `.codex/environments/environment.toml` files plus global Codex config files such as `~/.codex/AGENTS.md` and `~/.codex/keybindings.json` between local repo checkouts and another Mac or server over SSH. Use when the user wants to send, receive, copy, compare, refresh, or keep Codex Environment TOML configs, Codex instructions, or keyboard shortcuts in sync across machines such as this M4 Mac and DonPablo.
---

# Sync Codex Envs

Use this skill to synchronize repo-local Codex environment files:

```text
<repo>/.codex/environments/environment.toml
```

Also use this skill for these global Codex config files:

```text
~/.codex/AGENTS.md
~/.codex/keybindings.json
```

## Workflow

0. Default action: before any sync, run the read-only diff helper and print its full output:
   ```bash
   /Users/td/.codex/skills/sync-codex-envs/scripts/diff_codex_configs.sh
   ```
   Then ask the user how they want to proceed. Do not send or receive files until the user chooses a direction and scope.
1. Determine the direction for each repo:
   - `send`: copy local TOMLs to the remote machine.
   - `receive`: copy remote TOMLs to this machine.
2. Determine the remote SSH target. Default to `pablo@DonPabloMBP.local` when the user says DonPablo and gives no other host.
3. Determine repo names. If missing, ask which local repos to sync after discovering repos under `~/Code`.
4. For repo environment TOMLs, run `scripts/sync_env_tomls.py` with the chosen direction, remote, and repos. Use `--send-repo` and `--receive-repo` when one run needs mixed directions.
5. For global config files, use direct `ssh` and `scp` commands with a timestamped backup first.
6. Verify the output: the script validates TOML before overwriting, backs up destinations, and prints every copied path; direct global config sync should list and print the copied remote file.

## Script

Use this read-only diff helper first by default. It compares repo environment TOMLs under `~/Code`, remote repo TOMLs under `/Users/pablo/Code`, remote Codex workspace TOMLs under `/Users/pablo/Documents/Codex`, plus `~/.codex/AGENTS.md` and `~/.codex/keybindings.json` on both machines:

```bash
/Users/td/.codex/skills/sync-codex-envs/scripts/diff_codex_configs.sh
```

Optional target override:

```bash
/Users/td/.codex/skills/sync-codex-envs/scripts/diff_codex_configs.sh pablo@DonPabloMBP.local
```

After printing the diff, ask the user what to sync, if anything.

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
- Remote target for DonPablo: `pablo@DonPabloMBP.local`
- Environment destination backups: `environment.toml.bak-YYYYmmdd-HHMMSS`
- Global config destination backups: `<filename>.bak-YYYYmmdd-HHMMSS`

## Notes

- Do not sync `.env` secrets with this skill; sync only Codex Environment TOML files and the explicit global Codex config files above.
- If the user asks for shell-only commands instead of using the helper, give explicit `scp` commands for each repo or global config file and include a backup command first.
