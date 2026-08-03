---
name: simplify
description: Simplify or clean pasted code using a two-choice workflow. Use when the user provides code and wants it simplified, optimized, stripped of comments or blank lines, or summarized.
---

# Simplify

When given code:

- If no mode was chosen, ask: `Reply 1 to simplify and optimize, or 2 to analyze and clean.`
- If the user already chose a mode, do not ask again.
- First summarize what the code does in 4–5 simple bullets.
- Return code in a fenced code block. Do not edit files unless requested.

## 1 — Simplify and Optimize

Rewrite for maximum simplicity and readability while preserving behavior. Avoid functions, classes, clever constructs, excess comments, and blank lines when practical. Keep only brief section comments.

## 2 — Analyze and Clean

Remove comments and blank lines while preserving everything else. Do not mistake comment-like text inside strings for comments. After the code:

- Summarize its purpose in 1–3 sentences.
- List every file it reads, writes, appends, or creates; say `None identified` when applicable.
- Add only glaring improvement suggestions, or say `No glaring issues`.
- Briefly state what was changed.
