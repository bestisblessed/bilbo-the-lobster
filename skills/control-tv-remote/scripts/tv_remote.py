#!/usr/bin/env python3
"""Send natural-language TV remote commands to UniversalRemote.app."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass


APP_NAME = "UniversalRemote"


@dataclass(frozen=True)
class RemoteCommand:
    key: str
    description: str
    identifier: str
    aliases: tuple[str, ...]


COMMANDS = (
    RemoteCommand("power", "Power", "power", ("power", "turn off", "turn on")),
    RemoteCommand("volume-down", "Volume Down", "speaker.minus.fill", ("volume down", "lower volume", "turn down", "quieter")),
    RemoteCommand("mute", "Mute", "speaker.slash.fill", ("mute", "unmute")),
    RemoteCommand("volume-up", "Volume Up", "speaker.plus.fill", ("volume up", "raise volume", "turn up", "louder")),
    RemoteCommand("up", "Up", "chevron.up", ("up", "move up")),
    RemoteCommand("left", "Left", "chevron.left", ("left", "move left")),
    RemoteCommand("select", "Select", "circle.inset.filled", ("select", "ok", "okay", "enter", "confirm")),
    RemoteCommand("right", "Right", "chevron.right", ("right", "move right")),
    RemoteCommand("down", "Down", "chevron.down", ("down", "move down")),
    RemoteCommand("back", "Back", "arrow.uturn.backward", ("back", "return", "go back")),
    RemoteCommand("home", "Home", "house.fill", ("home", "main menu")),
    RemoteCommand("rewind", "Rewind", "backward.fill", ("rewind", "skip back")),
    RemoteCommand("play-pause", "Play/Pause", "playpause.fill", ("play pause", "play/pause", "pause", "play", "resume")),
    RemoteCommand("fast-forward", "Fast Forward", "forward.fill", ("fast forward", "skip forward", "forward")),
    RemoteCommand("channel-down", "Channel Down", "chevron.down.circle", ("channel down", "previous channel")),
    RemoteCommand("channel-up", "Channel Up", "chevron.up.circle", ("channel up", "next channel")),
)

NUMBER_WORDS = {
    "once": 1,
    "one": 1,
    "twice": 2,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def infer_repeat(prompt: str) -> int:
    prompt = normalize(prompt)
    match = re.search(r"\b(\d+)\s*(?:x|times?)\b", prompt)
    if match:
        return int(match.group(1))

    for word, value in NUMBER_WORDS.items():
        if re.search(rf"\b{re.escape(word)}\b(?:\s+times?)?", prompt):
            return value

    return 1


def resolve_command(prompt: str) -> RemoteCommand:
    prompt = normalize(prompt)
    matches: list[tuple[int, RemoteCommand]] = []

    for command in COMMANDS:
        if command.key in prompt:
            matches.append((len(command.key), command))
        if command.description.lower() in prompt:
            matches.append((len(command.description), command))
        for alias in command.aliases:
            if re.search(rf"\b{re.escape(alias)}\b", prompt):
                matches.append((len(alias), command))

    if not matches:
        raise ValueError(f"Could not map prompt to a remote command: {prompt!r}")

    best_score = max(score for score, _ in matches)
    unique = {command.key: command for score, command in matches if score == best_score}
    if len(unique) == 1:
        return next(iter(unique.values()))

    labels = ", ".join(command.key for command in unique.values())
    raise ValueError(f"Prompt is ambiguous; matched multiple equally specific commands: {labels}")


def applescript_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_applescript(command: RemoteCommand, repeat: int, tv_name: str | None) -> str:
    tv_block = ""
    if tv_name:
        tv = applescript_quote(tv_name)
        tv_block = f"""
        set tvName to "{tv}"
        set didSelectTV to false
        set allItems to entire contents of window 1
        repeat with itemRef in allItems
            try
                set itemValue to value of itemRef as text
                set itemRole to role of itemRef as text
                if itemRole is "AXRow" and itemValue contains tvName then
                    click itemRef
                    set didSelectTV to true
                    delay 0.2
                    exit repeat
                end if
            end try
        end repeat
        if didSelectTV is false then error "Could not find TV row containing: " & tvName
        """

    description = applescript_quote(command.description)
    identifier = applescript_quote(command.identifier)
    return textwrap.dedent(
        f"""
        tell application "{APP_NAME}" to activate
        delay 0.5
        tell application "System Events"
            tell process "{APP_NAME}"
                set frontmost to true
                repeat 20 times
                    if exists window 1 then exit repeat
                    delay 0.1
                end repeat
                if not (exists window 1) then error "{APP_NAME} window did not open"
                {textwrap.indent(textwrap.dedent(tv_block).strip(), "                ")}
                repeat with pressIndex from 1 to {repeat}
                    set didClick to false
                    set allItems to entire contents of window 1
                    repeat with itemRef in allItems
                        try
                            if role of itemRef is "AXButton" then
                                set itemDescription to description of itemRef as text
                                set itemIdentifier to value of attribute "AXIdentifier" of itemRef as text
                                if itemDescription is "{description}" or itemIdentifier is "{identifier}" then
                                    click itemRef
                                    set didClick to true
                                    delay 0.25
                                    exit repeat
                                end if
                            end if
                        end try
                    end repeat
                    if didClick is false then error "Could not find button: {description}"
                end repeat
            end tell
        end tell
        """
    ).strip()


def run_command(command: RemoteCommand, repeat: int, tv_name: str | None) -> None:
    script = build_applescript(command, repeat, tv_name)
    subprocess.run(["osascript", "-e", script], check=True)


def list_commands() -> None:
    for command in COMMANDS:
        aliases = ", ".join(command.aliases)
        print(f"{command.key}: {command.description} [{command.identifier}] aliases: {aliases}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Control UniversalRemote.app from a natural-language prompt.")
    parser.add_argument("prompt", nargs="*", help="Natural-language remote command, such as 'volume up twice'.")
    parser.add_argument("--tv", help="Optional TV name to select before sending the command.")
    parser.add_argument("--repeat", type=int, help="Override repeat count.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and print the command without sending it.")
    parser.add_argument("--list", action="store_true", help="List supported commands.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.list:
        list_commands()
        return 0

    prompt = " ".join(args.prompt).strip()
    if not prompt:
        print("Missing prompt. Use --list to see supported commands.", file=sys.stderr)
        return 2

    try:
        command = resolve_command(prompt)
        repeat = args.repeat if args.repeat is not None else infer_repeat(prompt)
        if repeat < 1:
            raise ValueError("--repeat must be at least 1")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    target = args.tv or "currently selected TV"
    print(f"Command: {command.description} x{repeat} -> {target}")
    if args.dry_run:
        return 0

    try:
        run_command(command, repeat, args.tv)
    except subprocess.CalledProcessError as exc:
        print(f"Failed to send command through {APP_NAME}: {exc}", file=sys.stderr)
        return exc.returncode or 1

    print("Sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
