---
name: simplify
description: Simplify and refine existing code for clarity, consistency, and maintainability while preserving exact functionality. Use when the user asks to simplify, clean up, reduce complexity, remove redundancy, or make code easier to read without changing behavior. Default to recently modified code, but also use this skill when the user names specific files, modules, or diffs to simplify.
---

# Simplify

## Overview

Simplify code with the smallest safe edit set. Preserve exact behavior, align with project conventions, and focus on code that was just changed unless the user specifies another scope.

## Choose Scope

- If the user names files or directories, use that scope.
- Otherwise inspect recent changes first with `git diff`, `git status`, or the task context and simplify the touched code.
- If the recent diff is broad, narrow the work to the most obviously improvable code rather than refactoring unrelated areas.

## Simplify Safely

Apply these rules in order:

1. Preserve functionality exactly. Do not change outputs, side effects, public interfaces, control flow semantics, data shape, error behavior, timing assumptions, or tests unless the existing code is already incorrect and the user asked for a fix.
2. Apply project standards already present in the codebase. Match naming, formatting, abstractions, and framework patterns instead of introducing a personal style.
3. Reduce unnecessary complexity. Flatten avoidable nesting, collapse redundant conditionals, inline one-off variables when that improves readability, and remove dead or duplicate paths.
4. Prefer fewer moving parts. Delete unhelpful abstractions, helper layers, and temporary variables unless they materially improve reuse or comprehension.
5. Improve readability. Use clearer names, group related logic, and make the main path easy to scan.
6. Keep changes minimal. Do not broaden the refactor once the target code is clear and improved.

## Preferred Edits

- Replace branching pyramids with guard clauses when the project already uses them.
- Merge duplicated logic that differs only trivially.
- Remove needless wrappers and pass-through helpers.
- Replace overly clever expressions with straightforward code.
- Consolidate related code that is split across tiny helpers only used once.
- Keep or add brief comments only when the intent is non-obvious after simplification.

## Avoid

- Do not rename widely used public APIs just for style.
- Do not move code across files unless that is the smallest clear simplification.
- Do not introduce new abstractions to "future-proof" the code.
- Do not change formatting-only details unrelated to the simplification target.
- Do not mix bug fixes or feature work into the simplification pass unless the user asked for that separately.

## Verification

- Run the most relevant existing tests or checks for the affected code after editing.
- Confirm the results match expectations and inspect the changed code to verify behavior was not altered.
- In the final response, state what was simplified, what was tested, and any remaining risk if test coverage was limited.

## Example Triggers

- "Use $simplify on the code we just changed."
- "Simplify this component without changing behavior."
- "Clean up `server/auth.py` but keep functionality identical."
- "Reduce the nesting in this handler and remove redundancy."
