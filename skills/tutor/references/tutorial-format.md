# Tutorial Format

Use this format for persistent tutorials in `tutorials/YYYY-MM-DD-topic-slug.md`.

## Frontmatter

Use real YAML and ISO dates:

```yaml
---
type: tutorial
title: "Topic Title"
concepts:
  - primary-concept
  - related-concept
source_repo: "repo-name"
source_paths:
  - "src/example.ts"
description: "One-paragraph summary of what this tutorial teaches."
understanding_score: null
last_quizzed: null
created: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
prerequisites: []
---
```

Rules:

- `type` must be `tutorial`; ignore markdown files without this type when indexing tutorials.
- `understanding_score` must be `null` or an integer from 1 to 10.
- `last_quizzed` must be `null` or `YYYY-MM-DD`.
- `concepts`, `source_paths`, and `prerequisites` must be YAML lists.
- `source_paths` should be relative paths when possible.

## Body

Use this structure:

```markdown
# Topic Title

## Why This Matters Here

Explain the real problem in this repo that makes the concept useful.

## Mental Model

Teach the shape of the idea. Use a small diagram only when it improves clarity.

## Examples From This Codebase

### Example 1: Short Name

Location: `path/to/file.ext:12`

```language
small relevant snippet
```

Explain what the code does and how it demonstrates the concept.

## Try It

Give one small exercise the learner can do in 10-15 minutes.

## Takeaways

- Three to five durable points.

---

## Q&A

## Quiz History
```

## Writing Standard

Write like a private tutor, not a reference manual. Use plain language, explain the "why", and keep the tutorial focused on one main idea.

Avoid:

- Generic examples when repo examples exist.
- Large pasted files.
- Secret values, credentials, or `.env` contents.
- Hidden reasoning or private judgments about the user.
