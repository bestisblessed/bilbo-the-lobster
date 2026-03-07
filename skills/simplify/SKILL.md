---
name: simplify
description: "Simplifies and refines code for clarity, consistency, and maintainability while preserving all exact functionality. Use when the user types /simplify or asks to simplify code. Inspired by the new Claude Code /simplify command: https://x.com/bcherny/status/2027534984534544489?s=20"
metadata: {"openclaw": {"emoji": "🧹", "user-invocable": true, "homepage": "https://x.com/bcherny/status/2027534984534544489?s=20"}}
---

# Simplify

Simplifies and refines code for clarity, consistency, and maintainability while preserving all exact functionality.

## Guidelines

Follow these guidlines:

1. Preserve Functionality: Never change what the code does - only how it does it.
2. Apply Project Standards.
3. Enhance Clarity: Simplify code structure by:
   - Reducing unnecessary complexity and nesting
   - Eliminating redundant code and abstractions
   - Limiting number of variables unless reused heavily
   - Improving readability through clear variable and function names
   - Consolidating related logic

## Scope

Focuses on recently modified code unless instructed otherwise.
