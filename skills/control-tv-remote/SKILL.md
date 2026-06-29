---
name: control-tv-remote
description: Control the user's TV through the macOS UniversalRemote app from natural-language prompts. Use when the user asks Codex to operate the TV or remote, including volume, mute, power, play/pause, navigation, home/back, channel, rewind, fast-forward, selecting a TV, or sending repeated remote button presses.
---

# Control TV Remote

## Overview

Use `UniversalRemote.app` to control the user's TV from plain-language requests. The source recording showed the user opening `UniversalRemote.app`, using the selected `LG webOS TV UR9000PUA`, pressing `Volume Up` twice, and pressing `Play/Pause`; the app confirmed actions with status text such as `Volume Up sent to LG webOS TV UR9000PUA`.

Prefer the bundled script for repeatable commands:

```bash
python3 "$CODEX_HOME/skills/control-tv-remote/scripts/tv_remote.py" "volume up twice"
```

If `CODEX_HOME` is unset, use `~/.codex/skills/control-tv-remote/scripts/tv_remote.py`.

## Workflow

1. Parse the user's prompt into remote button commands.
2. If the prompt names a TV, pass `--tv "<name>"`; otherwise use the currently selected TV in `UniversalRemote.app`.
3. Use `--dry-run` before sending a risky command such as `power`, or when the prompt is ambiguous.
4. Run the script without `--dry-run` to send the command.
5. Verify the command result from the script output and, when needed, by checking the `UniversalRemote.app` status text.

## Commands

The app exposes these stable button descriptions and identifiers:

| Spoken intent | Button description | Identifier |
| --- | --- | --- |
| power, turn TV on/off | `Power` | `power` |
| volume down, lower volume | `Volume Down` | `speaker.minus.fill` |
| mute, unmute | `Mute` | `speaker.slash.fill` |
| volume up, raise volume | `Volume Up` | `speaker.plus.fill` |
| up | `Up` | `chevron.up` |
| left | `Left` | `chevron.left` |
| select, ok, enter | `Select` | `circle.inset.filled` |
| right | `Right` | `chevron.right` |
| down | `Down` | `chevron.down` |
| back, return | `Back` | `arrow.uturn.backward` |
| home | `Home` | `house.fill` |
| rewind | `Rewind` | `backward.fill` |
| play, pause, resume, play pause | `Play/Pause` | `playpause.fill` |
| fast forward, skip forward | `Fast Forward` | `forward.fill` |
| channel down | `Channel Down` | `chevron.down.circle` |
| channel up | `Channel Up` | `chevron.up.circle` |

The script supports repeated presses from phrases such as `twice`, `three times`, `2x`, or an explicit `--repeat N`.

## Examples

```bash
python3 ~/.codex/skills/control-tv-remote/scripts/tv_remote.py "volume up twice"
python3 ~/.codex/skills/control-tv-remote/scripts/tv_remote.py "pause the tv"
python3 ~/.codex/skills/control-tv-remote/scripts/tv_remote.py --tv "Sony" "home"
python3 ~/.codex/skills/control-tv-remote/scripts/tv_remote.py --dry-run "power"
python3 ~/.codex/skills/control-tv-remote/scripts/tv_remote.py --list
```

## Ambiguity And Safety

- Ask a clarifying question when the prompt cannot be mapped to exactly one command.
- Treat `power` as potentially disruptive; dry-run or confirm when the wording is unclear.
- If the app is not open, the script opens `UniversalRemote.app` before sending commands.
- If macOS denies Accessibility automation, tell the user to grant Terminal/Codex accessibility access in System Settings, then retry.
- Avoid coordinate-only control. Use button descriptions or identifiers from the accessibility tree.

## Manual Fallback

If the script fails but UI control is available, use Computer Use or macOS accessibility tooling:

1. Open `UniversalRemote.app`.
2. Select the requested TV in the sidebar if the prompt names one.
3. Click the remote button whose accessibility description matches the mapped command.
4. Confirm the status text changes to `<Command> sent to <TV name>`.
