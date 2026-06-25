---
name: mma-swift-data-update
description: Update and deploy MMA AI Swift app data for mma-ai-swift-app. Use when the user asks to refresh MMA Swift data, run update_data.sh, push updated data files, pull updates on DonPablo, restart the com.bestisblessed.mma-ai-swift-backend launchd service, verify SWIFTSTATUS, or turn the recorded MMA Swift server update workflow into repeatable steps.
---

# MMA Swift Data Update

## Purpose

Use this skill for the MMA AI Swift data refresh and DonPablo deployment workflow. Keep changes narrow: data files first, no main commits or pushes unless the user explicitly approves them in the current turn.

## Local Refresh

1. Confirm the repo and branch:
   - Expected local path: `/Users/td/Code/mma-ai-swift-app`
   - Run `git status --short --branch` before changing anything.
   - Note unrelated dirty files and leave them alone.
2. Run the data refresh from the repo root:
   - `./update_data.sh`
   - Enter the current Sherdog event URL when prompted.
3. Verify script output:
   - Confirm `data/upcoming_event_data_sherdog.csv` was written.
   - Confirm the fight count looks plausible for the event.
   - Confirm odds output copied or regenerated if the script reports it.
4. Review changed files:
   - Prefer `git status --short` and focused diffs for `data/`.
   - Stage only intended data changes, usually `git add data/`.

## Publish Local Data

Before any `git commit` or `git push`, confirm the user approved publishing in the current turn. The project rule is strict: never commit or push to `main` without explicit current-turn approval.

If approved:

1. Commit with a clear message such as `UPDATING DATA`, unless the user requested different wording.
2. Push.
3. If push is rejected because remote `main` moved:
   - Fetch or pull.
   - Inspect the divergence before merging.
   - Merge or rebase only after deciding it is safe for this data-only update.
   - Push again after resolving the branch state.

## DonPablo Update

Use SSH only when live server state matters or the user asks to update the server.

1. Connect:
   - `ssh donpablo`
   - `cd ~/Code/mma-ai-swift-app`
2. Check server status:
   - Run `git status --short --branch` or the user's `S` alias if available.
   - If server-side `data/` files are dirty and should be replaced by the pushed GitHub state, run `git restore data`.
   - Do not restore non-data files unless the user explicitly asks.
3. Pull the update:
   - `git pull`
   - Confirm it fast-forwards to the expected pushed revision.

## Restart And Verify

DonPablo is macOS. Do not rely on `systemctl` there. If `./run.sh` calls `systemctl`, it is the wrong restart path for DonPablo.

Use the launchd aliases:

1. Check current state:
   - `SWIFTSTATUS`
2. Restart:
   - `SWIFTRESTART`
3. Verify:
   - `SWIFTSTATUS`
   - Confirm `state = running`.
   - Confirm `runs` incremented.
   - Confirm `pid` changed.
   - Confirm `last exit code = 0`.
   - Confirm launchd state lines are active.

Known alias shapes:

```bash
SWIFTSTATUS='launchctl print gui/$(id -u)/com.bestisblessed.mma-ai-swift-backend | grep -E "state =|pid =|runs =|last exit|last terminating"'
SWIFTSTART='launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.bestisblessed.mma-ai-swift-backend.plist'
```

## Final Report

Report the exact data files changed, commit and push status if publishing was approved, DonPablo pull result, backend restart result, and any remaining risks. Include command output summaries, especially `SWIFTSTATUS`.

## Validation Helper

For a quick skill sanity check, run:

```bash
python /Users/td/.codex/skills/mma-swift-data-update/scripts/validate_skill.py
```
