#!/usr/bin/env bash
set -euo pipefail

remote="${1:-pablo@DonPabloMBP.local}"
local_code_root="${LOCAL_CODE_ROOT:-$HOME/Code}"
remote_code_root="${REMOTE_CODE_ROOT:-/Users/pablo/Code}"

env_rel=".codex/environments/environment.toml"
global_files=("AGENTS.md" "keybindings.json")

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

local_repos="$tmp_dir/local-repos.txt"
remote_repos="$tmp_dir/remote-repos.txt"
all_repos="$tmp_dir/all-repos.txt"
remote_home="$(ssh -n "$remote" 'printf %s "$HOME"')"

find "$local_code_root" -maxdepth 4 -path "*/$env_rel" -print \
  | sed "s#^$local_code_root/##; s#/$env_rel\$##" \
  | sort > "$local_repos"

ssh -n "$remote" "find '$remote_code_root' -maxdepth 4 -path '*/$env_rel' -print" \
  | sed "s#^$remote_code_root/##; s#/$env_rel\$##" \
  | sort > "$remote_repos"

sort -u "$local_repos" "$remote_repos" > "$all_repos"

remote_file_exists() {
  ssh -n "$remote" "test -f '$1'" >/dev/null 2>&1
}

print_diff() {
  local label="$1"
  local local_path="$2"
  local remote_path="$3"
  local remote_tmp="$tmp_dir/remote-${label//[^A-Za-z0-9_.-]/_}"

  if [[ ! -f "$local_path" ]] && ! remote_file_exists "$remote_path"; then
    return
  fi

  if [[ ! -f "$local_path" ]]; then
    printf '[only-remote] %s\n' "$label"
    printf '  remote: %s:%s\n\n' "$remote" "$remote_path"
    return
  fi

  if ! remote_file_exists "$remote_path"; then
    printf '[only-local] %s\n' "$label"
    printf '  local:  %s\n\n' "$local_path"
    return
  fi

  ssh -n "$remote" "cat '$remote_path'" > "$remote_tmp"

  if cmp -s "$local_path" "$remote_tmp"; then
    printf '[same] %s\n' "$label"
    return
  fi

  printf '[different] %s\n' "$label"
  diff -u "$local_path" "$remote_tmp" || true
  printf '\n'
}

printf 'Comparing local %s with remote %s:%s\n\n' "$local_code_root" "$remote" "$remote_code_root"

while IFS= read -r repo; do
  [[ -n "$repo" ]] || continue
  print_diff \
    "$repo/$env_rel" \
    "$local_code_root/$repo/$env_rel" \
    "$remote_code_root/$repo/$env_rel"
done < "$all_repos"

printf '\nComparing global Codex config files\n\n'

for file in "${global_files[@]}"; do
  print_diff \
    "~/.codex/$file" \
    "$HOME/.codex/$file" \
    "$remote_home/.codex/$file"
done

printf '\nComparing installed plugins and user skills\n\n'

python3 "$(dirname "$0")/diff_plugins_skills.py" "$remote"
