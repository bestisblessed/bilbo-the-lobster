#!/usr/bin/env python
"""Sync repo-local Codex environment.toml files over SSH/SCP."""

from __future__ import annotations

import argparse
import datetime as dt
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


ENV_REL = Path(".codex/environments/environment.toml")
DEFAULT_LOCAL_CODE_ROOT = Path("~/Code").expanduser()
DEFAULT_REMOTE = "donpablo"
DEFAULT_REMOTE_CODE_ROOT = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync .codex/environments/environment.toml files between this Mac and an SSH target."
    )
    parser.add_argument("--direction", choices=("send", "receive"), help="send local files to remote, or receive remote files")
    parser.add_argument("--remote", help=f"SSH target, default {DEFAULT_REMOTE}")
    parser.add_argument("--remote-code-root", default=DEFAULT_REMOTE_CODE_ROOT, help="Remote Code directory, default <remote $HOME>/Code")
    parser.add_argument("--local-code-root", type=Path, default=DEFAULT_LOCAL_CODE_ROOT, help=f"Local Code directory, default {DEFAULT_LOCAL_CODE_ROOT}")
    parser.add_argument("--repo", action="append", help="Repo name/path to sync. Repeat, comma-separate, or use 'all'.")
    parser.add_argument("--send-repo", action="append", help="Repo to send from this Mac to remote. Repeat or comma-separate.")
    parser.add_argument("--receive-repo", action="append", help="Repo to receive from remote to this Mac. Repeat or comma-separate.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen without copying files")
    parser.add_argument("--yes", action="store_true", help="Skip final confirmation prompt")
    return parser.parse_args()


def run(cmd: list[str], *, dry_run: bool = False) -> None:
    print("+", " ".join(shlex.quote(part) for part in cmd))
    if not dry_run:
        subprocess.run(cmd, check=True)


def validate_toml(path: Path) -> None:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if data.get("version") is None or data.get("name") is None:
        raise ValueError(f"{path} is valid TOML but is missing expected Codex environment fields")


def discover_repos(local_code_root: Path) -> list[str]:
    if not local_code_root.is_dir():
        return []
    repos: list[str] = []
    for child in sorted(local_code_root.iterdir()):
        if child.is_dir() and (child / ENV_REL).is_file():
            repos.append(child.name)
    return repos


def split_repos(values: list[str] | None) -> list[str]:
    repos: list[str] = []
    for value in values or []:
        repos.extend(part.strip() for part in value.split(",") if part.strip())
    return repos


def prompt_direction(direction: str | None) -> str:
    if direction:
        return direction
    answer = input("Direction [send/receive]: ").strip().lower()
    if answer not in {"send", "receive"}:
        raise SystemExit("Direction must be 'send' or 'receive'.")
    return answer


def prompt_remote(remote: str | None) -> str:
    if remote:
        return remote
    try:
        answer = input(f"Remote SSH target [{DEFAULT_REMOTE}]: ").strip()
    except EOFError:
        return DEFAULT_REMOTE
    return answer or DEFAULT_REMOTE


def get_remote_home(remote: str) -> str:
    return subprocess.check_output(["ssh", remote, 'printf %s "$HOME"'], text=True).strip()


def prompt_repos(repos: list[str], discovered: list[str]) -> list[str]:
    if repos:
        requested = repos
    else:
        if discovered:
            print("Discovered repos with Codex environment TOMLs:")
            for index, repo in enumerate(discovered, start=1):
                print(f"  {index}. {repo}")
            raw = input("Repos to sync [all, numbers, names, comma-separated]: ").strip() or "all"
        else:
            raw = input("Repos to sync [comma-separated names]: ").strip()
        requested = [part.strip() for part in raw.split(",") if part.strip()]

    if any(repo.lower() == "all" for repo in requested):
        if not discovered:
            raise SystemExit("No local repos with environment.toml were discovered.")
        return discovered

    selected: list[str] = []
    for repo in requested:
        if repo.isdigit() and discovered:
            index = int(repo)
            if index < 1 or index > len(discovered):
                raise SystemExit(f"Repo index out of range: {repo}")
            selected.append(discovered[index - 1])
        else:
            selected.append(Path(repo).name)
    return list(dict.fromkeys(selected))


def local_env_path(local_code_root: Path, repo: str) -> Path:
    candidate = Path(repo).expanduser()
    if candidate.is_absolute():
        return candidate / ENV_REL
    return local_code_root / repo / ENV_REL


def remote_env_path(remote_code_root: str, repo: str) -> str:
    return f"{remote_code_root.rstrip('/')}/{repo}/{ENV_REL.as_posix()}"


def timestamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def confirm(args: argparse.Namespace, remote: str, operations: list[tuple[str, str]]) -> None:
    if args.yes or args.dry_run:
        return
    print()
    print(f"Remote: {remote}")
    for direction, repo in operations:
        print(f"{direction}: {repo}")
    answer = input("Proceed? [y/N]: ").strip().lower()
    if answer not in {"y", "yes"}:
        raise SystemExit("Canceled.")


def build_operations(args: argparse.Namespace, discovered: list[str]) -> list[tuple[str, str]]:
    send_repos = prompt_repos(split_repos(args.send_repo), discovered) if args.send_repo else []
    receive_repos = prompt_repos(split_repos(args.receive_repo), discovered) if args.receive_repo else []
    operations = [("send", repo) for repo in send_repos] + [("receive", repo) for repo in receive_repos]
    if operations:
        return operations

    direction = prompt_direction(args.direction)
    repos = prompt_repos(split_repos(args.repo), discovered)
    return [(direction, repo) for repo in repos]


def send_repo(args: argparse.Namespace, remote: str, repo: str) -> None:
    local_path = local_env_path(args.local_code_root.expanduser(), repo)
    remote_path = remote_env_path(args.remote_code_root, repo)
    if not local_path.is_file():
        raise FileNotFoundError(f"Missing local source: {local_path}")
    validate_toml(local_path)

    remote_dir = str(Path(remote_path).parent)
    backup_path = f"{remote_path}.bak-{timestamp()}"
    backup_cmd = (
        f"mkdir -p {shlex.quote(remote_dir)} && "
        f"test ! -f {shlex.quote(remote_path)} || cp {shlex.quote(remote_path)} {shlex.quote(backup_path)}"
    )
    run(["ssh", remote, backup_cmd], dry_run=args.dry_run)
    run(["scp", str(local_path), f"{remote}:{remote_path}"], dry_run=args.dry_run)
    verb = "would send" if args.dry_run else "sent"
    print(f"{verb}: {local_path} -> {remote}:{remote_path}")


def receive_repo(args: argparse.Namespace, remote: str, repo: str) -> None:
    local_path = local_env_path(args.local_code_root.expanduser(), repo)
    remote_path = remote_env_path(args.remote_code_root, repo)
    with tempfile.TemporaryDirectory() as tmp:
        temp_path = Path(tmp) / f"{repo}-environment.toml"
        run(["scp", f"{remote}:{remote_path}", str(temp_path)], dry_run=args.dry_run)
        if args.dry_run:
            print(f"would receive: {remote}:{remote_path} -> {local_path}")
            return
        validate_toml(temp_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        if local_path.exists():
            backup_path = local_path.with_name(f"{local_path.name}.bak-{timestamp()}")
            shutil.copy2(local_path, backup_path)
            print(f"backup: {backup_path}")
        shutil.copy2(temp_path, local_path)
        validate_toml(local_path)
        print(f"received: {remote}:{remote_path} -> {local_path}")


def main() -> int:
    args = parse_args()
    args.local_code_root = args.local_code_root.expanduser()
    remote = prompt_remote(args.remote)
    if args.remote_code_root is None:
        args.remote_code_root = f"{get_remote_home(remote)}/Code"
    discovered = discover_repos(args.local_code_root)
    operations = build_operations(args, discovered)
    confirm(args, remote, operations)

    for direction, repo in operations:
        if direction == "send":
            send_repo(args, remote, repo)
        else:
            receive_repo(args, remote, repo)

    print("done")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
