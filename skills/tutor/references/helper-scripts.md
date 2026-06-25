# Helper Script Spec

This is the script contract for a future implementation. Keep scripts deterministic, testable, and safe to run in temporary directories.

## Shared Requirements

Every script should support:

```text
--tutorials-dir <path>
```

Resolution order:

1. Explicit `--tutorials-dir`.
2. `CODING_TUTOR_HOME`.
3. `~/coding-tutor-tutorials`.

Use ISO dates. Validate YAML with a real YAML parser. Exit non-zero with useful stderr on invalid metadata.

## `setup_library.py`

Purpose: create the tutorial library safely.

Behavior:

- Create the directory and `tutorials/`.
- Create `learner_profile.md` only when supplied profile data exists.
- Create `manifest.json`.
- Optionally initialize git with `--init-git`.
- Check git identity before making an initial commit.
- Never create remotes, GitHub repos, commits, or pushes unless the user explicitly approved the calling workflow.
- If setup fails, do not leave a state that later reports false success.

## `create_tutorial.py`

Purpose: create a tutorial markdown file from validated metadata.

Required arguments:

```text
create_tutorial.py "Topic Title" --concept primary --concept related --source-repo repo-name
```

Behavior:

- Generate safe slugs from lowercase letters, digits, and hyphens.
- Refuse to overwrite an existing tutorial unless `--force` is provided.
- Write valid YAML frontmatter using the schema in `tutorial-format.md`.
- Print the created file path.

## `index_tutorials.py`

Purpose: list tutorial metadata.

Behavior:

- Include only markdown files whose frontmatter has `type: tutorial`.
- Exclude README files, learner profiles, notes, and malformed files.
- Output JSON by default.
- Support `--format human`.

## `quiz_priority.py`

Purpose: rank tutorials for spaced repetition.

Behavior:

- Validate scores and dates.
- Accept `--today YYYY-MM-DD` for tests.
- Sort by urgency.
- Output enough detail for Codex to explain why a concept was picked.

## `update_tutorial.py`

Purpose: safely update metadata and append Q&A or quiz history.

Behavior:

- Preserve existing body text.
- Update `last_updated`.
- Validate frontmatter before and after writing.
- Refuse to update files that are not `type: tutorial`.

## Tests

Add tests for:

- Setup success and setup failure.
- Missing git identity.
- Duplicate tutorial creation.
- Slug sanitization.
- YAML list fields.
- Profile exclusion from indexes.
- Invalid dates and invalid scores.
- Quiz priority ordering with injected `today`.
