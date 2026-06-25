#!/usr/bin/env python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"

REQUIRED = [
    "name: mma-swift-data-update",
    "description: Update and deploy MMA AI Swift app data",
    "## Local Refresh",
    "## Publish Local Data",
    "## DonPablo Update",
    "## Restart And Verify",
    "SWIFTRESTART",
    "SWIFTSTATUS",
    "systemctl",
    "com.bestisblessed.mma-ai-swift-backend",
]


def main() -> int:
    text = SKILL.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED if item not in text]
    if missing:
        print("Missing required skill anchors:")
        for item in missing:
            print(f"- {item}")
        return 1
    print(f"OK: {SKILL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
