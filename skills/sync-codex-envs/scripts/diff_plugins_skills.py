#!/usr/bin/env python3
"""Print read-only differences in Codex global config, plugins, MCPs, and skills."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path


DEFAULT_REMOTE = "pablo@DonPabloMBP.local"
EXPECTED_LOCAL_ONLY_SKILLS = {"add-sidebar-favorite"}

# Keep the stable, user-facing global controls; exclude desktop/UI state,
# trusted directories, project state, marketplaces, and machine-local paths.
MAJOR_GLOBAL_KEYS = {
    "model", "model_reasoning_effort", "sandbox_mode", "approval_policy",
    "web_search", "approvals_reviewer", "service_tier", "notify",
}
MAJOR_GLOBAL_TABLES = {"sandbox_workspace_write"}
SENSITIVE_WORDS = ("token", "secret", "password", "api_key", "apikey", "authorization")
USER_PATH_RE = re.compile(r"/Users/[^/]+/")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare installed Codex plugins, MCPs, and user skills with an SSH target."
    )
    parser.add_argument("remote", nargs="?", default=DEFAULT_REMOTE, help=f"SSH target, default {DEFAULT_REMOTE}")
    return parser.parse_args()


def run_remote(remote: str, command: str) -> str:
    return subprocess.check_output(["ssh", "-n", remote, command], text=True)


def parse_plugins(config_text: str) -> dict[str, str]:
    if not config_text.strip():
        return {}
    data = tomllib.loads(config_text)
    plugins = data.get("plugins", {})
    result: dict[str, str] = {}
    for name, config in plugins.items():
        if isinstance(config, dict):
            enabled = config.get("enabled")
            result[name] = "enabled" if enabled is True else "disabled"
    return result


def _safe_value(key: str, value: object) -> object:
    if any(word in key.lower() for word in SENSITIVE_WORDS):
        return "<redacted>"
    if isinstance(value, dict):
        return {str(k): _safe_value(str(k), v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [_safe_value(key, item) for item in value]
    if isinstance(value, str):
        return USER_PATH_RE.sub("/Users/<user>/", value)
    return value


def parse_major_global_config(config_text: str) -> dict[str, object]:
    if not config_text.strip():
        return {}
    data = tomllib.loads(config_text)
    result = {key: _safe_value(key, data[key]) for key in sorted(MAJOR_GLOBAL_KEYS) if key in data}
    for table in sorted(MAJOR_GLOBAL_TABLES):
        if isinstance(data.get(table), dict):
            result[table] = _safe_value(table, data[table])
    return result


def parse_skill_config(config_text: str) -> dict[str, object]:
    if not config_text.strip():
        return {}
    data = tomllib.loads(config_text)
    skills = data.get("skills", {})
    configured = skills.get("config") if isinstance(skills, dict) else None
    if not isinstance(configured, list):
        return {}
    result = {}
    for item in configured:
        if not isinstance(item, dict) or "path" not in item:
            continue
        path = str(item["path"])
        result[path] = {key: _safe_value(key, value) for key, value in sorted(item.items()) if key != "path"}
    return result


def parse_standalone_mcps(config_text: str) -> dict[str, str]:
    if not config_text.strip():
        return {}
    data = tomllib.loads(config_text)
    servers = data.get("mcp_servers", {})
    result: dict[str, str] = {}
    for name, config in servers.items():
        if isinstance(config, dict):
            result[name] = "present"
    return result


def parse_plugin_mcp_overrides(config_text: str) -> dict[str, str]:
    if not config_text.strip():
        return {}
    data = tomllib.loads(config_text)
    plugins = data.get("plugins", {})
    result: dict[str, str] = {}
    for plugin_name, config in plugins.items():
        if not isinstance(config, dict):
            continue
        mcp_servers = config.get("mcp_servers")
        if isinstance(mcp_servers, dict) and mcp_servers:
            result[plugin_name] = "present"
    return result


def local_config_text() -> str:
    path = Path.home() / ".codex/config.toml"
    return path.read_text() if path.is_file() else ""


def remote_config_text(remote: str) -> str:
    return run_remote(remote, 'if [ -f "$HOME/.codex/config.toml" ]; then cat "$HOME/.codex/config.toml"; fi')


def local_skills() -> set[str]:
    items: set[str] = set()
    roots = [
        ("codex", Path.home() / ".codex/skills"),
        ("agents", Path.home() / ".agents/skills"),
    ]
    for label, root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*/SKILL.md")):
            if label == "codex" and path.parent.name in {".system", "sync-codex-envs", *EXPECTED_LOCAL_ONLY_SKILLS}:
                continue
            items.add(f"{label}:{path.parent.name}")
    return items


def remote_skills(remote: str) -> set[str]:
    output = run_remote(
        remote,
        r'''
for root in "$HOME/.codex/skills" "$HOME/.agents/skills"; do
  if [ "$root" = "$HOME/.codex/skills" ]; then
    label="codex"
  else
    label="agents"
  fi
  if [ -d "$root" ]; then
    find "$root" -mindepth 2 -maxdepth 2 -name SKILL.md -print | while IFS= read -r skill; do
      name="${skill%/SKILL.md}"
      name="${name##*/}"
      if [ "$label" = "codex" ] && { [ "$name" = ".system" ] || [ "$name" = "sync-codex-envs" ] || [ "$name" = "add-sidebar-favorite" ]; }; then
        continue
      fi
      printf '%s:%s\n' "$label" "$name"
    done
  fi
done
''',
    )
    return {line.strip() for line in output.splitlines() if line.strip()}


def print_set_diff(title: str, local_items: set[str], remote_items: set[str]) -> None:
    only_local = sorted(local_items - remote_items)
    only_remote = sorted(remote_items - local_items)

    print(title)
    if not only_local and not only_remote:
        print("[same] no install differences")
        print()
        return

    for item in only_local:
        print(f"[only-local] {item}")
    for item in only_remote:
        print(f"[only-remote] {item}")
    print()


def print_plugin_diff(local_plugins: dict[str, str], remote_plugins: dict[str, str]) -> None:
    print("Plugins from ~/.codex/config.toml")
    names = sorted(set(local_plugins) | set(remote_plugins))
    printed = False
    for name in names:
        local_status = local_plugins.get(name)
        remote_status = remote_plugins.get(name)
        if local_status is None:
            print(f"[only-remote] {name} ({remote_status})")
            printed = True
        elif remote_status is None:
            print(f"[only-local] {name} ({local_status})")
            printed = True
        elif local_status != remote_status:
            print(f"[different-status] {name} local={local_status} remote={remote_status}")
            printed = True
    if not printed:
        print("[same] no plugin install differences")
    print()


def print_config_diff(title: str, local_items: dict[str, object], remote_items: dict[str, object]) -> None:
    print(title)
    if local_items == remote_items:
        print("[same] no differences")
        print()
        return
    print("| Setting / entry | Local | Remote | Status |")
    print("|---|---|---|---|")
    for key in sorted(set(local_items) | set(remote_items)):
        if key not in local_items:
            print(f"| `{key}` | — | `{remote_items[key]!r}` | only remote |")
        elif key not in remote_items:
            print(f"| `{key}` | `{local_items[key]!r}` | — | only local |")
        elif local_items[key] != remote_items[key]:
            print(f"| `{key}` | `{local_items[key]!r}` | `{remote_items[key]!r}` | different |")
    print()


def print_mcp_presence_diff(title: str, local_items: dict[str, str], remote_items: dict[str, str]) -> None:
    print(title)
    local_names = set(local_items)
    remote_names = set(remote_items)
    only_local = sorted(local_names - remote_names)
    only_remote = sorted(remote_names - local_names)

    if not only_local and not only_remote:
        print("[same] no install differences")
        print()
        return

    for name in only_local:
        print(f"[only-local] {name}")
    for name in only_remote:
        print(f"[only-remote] {name}")
    print()


def main() -> int:
    args = parse_args()

    local_config = local_config_text()
    remote_config = remote_config_text(args.remote)

    print_config_diff(
        "Major global settings from ~/.codex/config.toml",
        parse_major_global_config(local_config),
        parse_major_global_config(remote_config),
    )
    print_config_diff(
        "Configured skill entries from ~/.codex/config.toml",
        parse_skill_config(local_config),
        parse_skill_config(remote_config),
    )

    local_plugins = parse_plugins(local_config)
    remote_plugins = parse_plugins(remote_config)
    print_plugin_diff(local_plugins, remote_plugins)

    print_mcp_presence_diff(
        "Standalone MCP servers from ~/.codex/config.toml",
        parse_standalone_mcps(local_config),
        parse_standalone_mcps(remote_config),
    )

    print_mcp_presence_diff(
        "Plugin MCP overrides from ~/.codex/config.toml",
        parse_plugin_mcp_overrides(local_config),
        parse_plugin_mcp_overrides(remote_config),
    )

    print_set_diff("User skills", local_skills(), remote_skills(args.remote))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (subprocess.CalledProcessError, OSError, tomllib.TOMLDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
