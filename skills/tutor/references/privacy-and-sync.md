# Privacy And Sync

This skill can persist personal learning records. Treat that as user-owned data.

## Consent

Ask before first persistent setup:

```text
I can create a local learning library at `~/coding-tutor-tutorials/` to store your tutorials, quiz history, and optional learner profile. Should I create it?
```

If the user declines, continue with one-off explanations in chat.

## Learner Profile

Store only user-approved information:

- Programming background.
- Learning goals.
- Preferred teaching style.
- Visible tutor notes that would be acceptable for the user to read later.

Do not store:

- Hidden chain-of-thought or internal commentary.
- Sensitive personal details unrelated to learning.
- Credentials, tokens, keys, private URLs, or secret-bearing snippets.

## Code Snippets

Use small snippets that explain the concept. Prefer paths and line references over copying large code blocks.

Before saving tutorial content, check that snippets do not include:

- `.env` values.
- API keys or bearer tokens.
- Passwords, private keys, cookies, or session values.
- Personal contact/payment identifiers.
- Proprietary code unrelated to the lesson.

## Git And Sync

The tutorial library may be a git repo, but all publishing actions require explicit current-turn approval.

Allowed without approval:

- Read files.
- Show `git status`.
- Explain what would be committed.
- Draft a commit message.

Requires explicit approval:

- `git add`
- `git commit`
- `git push`
- `gh repo create`
- Creating or changing remotes.
- Copying tutorials to another machine.

Default GitHub repos, if the user approves creating one, must be private unless the user explicitly asks for public.
