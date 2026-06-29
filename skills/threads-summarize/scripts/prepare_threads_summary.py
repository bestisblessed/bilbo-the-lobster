#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


def project_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return Path(result.stdout.strip())
    except Exception:
        return Path.cwd()


def text_from_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if text:
                    parts.append(text)
        return "\n".join(parts)
    return ""


def find_session_file(codex_home: Path, session_id: str) -> Path | None:
    sessions_dir = codex_home / "sessions"
    if not sessions_dir.exists():
        return None
    matches = sorted(sessions_dir.rglob(f"*{session_id}*.jsonl"))
    return matches[0] if matches else None


def thread_metadata(codex_home: Path, session_id: str) -> dict:
    db = codex_home / "state_5.sqlite"
    if not db.exists():
        return {}
    try:
        con = sqlite3.connect(db)
        con.row_factory = sqlite3.Row
        row = con.execute(
            "select id, title, cwd, datetime(updated_at, 'unixepoch', 'localtime') as updated_local "
            "from threads where id = ?",
            (session_id,),
        ).fetchone()
    except Exception:
        return {}
    finally:
        try:
            con.close()
        except Exception:
            pass
    return dict(row) if row else {}


def app_name(codex_home: Path, session_id: str) -> str:
    index = codex_home / "session_index.jsonl"
    if not index.exists():
        return ""
    latest = ""
    for line in index.read_text(errors="replace").splitlines():
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("id") == session_id:
            latest = obj.get("thread_name") or latest
    return latest


def extract_messages(session_file: Path, output_file: Path) -> None:
    lines = []
    for raw in session_file.read_text(errors="replace").splitlines():
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        payload = obj.get("payload") or {}
        if obj.get("type") == "session_meta":
            lines.append(
                f"# session_meta {payload.get('id')} "
                f"cwd={payload.get('cwd')} timestamp={payload.get('timestamp')}"
            )
            continue
        if obj.get("type") != "response_item":
            continue
        if payload.get("type") != "message":
            continue
        role = payload.get("role")
        if role not in {"user", "assistant"}:
            continue
        text = text_from_content(payload.get("content"))
        lines.append(f"\n## {obj.get('timestamp', '')} {role}\n{text}")
    output_file.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare extracted Codex thread message files for summarization."
    )
    parser.add_argument("session_ids", nargs="+", help="Codex session/thread ids to include")
    parser.add_argument("--output-dir", help="Directory for extracted message files")
    args = parser.parse_args()

    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    root = project_root()
    output_dir = Path(args.output_dir) if args.output_dir else Path(tempfile.mkdtemp(prefix="threads-summary-"))
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {"project_root": str(root), "output_dir": str(output_dir), "threads": []}

    for session_id in args.session_ids:
        session_file = find_session_file(codex_home, session_id)
        if not session_file:
            result["threads"].append({"id": session_id, "error": "session file not found"})
            continue
        messages_path = output_dir / f"{session_id}.messages.md"
        extract_messages(session_file, messages_path)
        meta = thread_metadata(codex_home, session_id)
        result["threads"].append(
            {
                "id": session_id,
                "name": app_name(codex_home, session_id) or meta.get("title", ""),
                "title": meta.get("title", ""),
                "updated_local": meta.get("updated_local", ""),
                "cwd": meta.get("cwd", ""),
                "session_file": str(session_file),
                "messages_path": str(messages_path),
            }
        )

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
