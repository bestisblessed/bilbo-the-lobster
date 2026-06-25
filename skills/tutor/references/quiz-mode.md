# Quiz Mode

Use quiz mode when the user asks to be quizzed on a topic, asks for spaced repetition, or says "quiz me".

## Priority

When helper scripts exist, use the quiz-priority script. Until then, choose in this order:

1. Tutorials never quizzed.
2. Low scores that are overdue.
3. Older high-score tutorials whose review interval has elapsed.
4. The topic the user explicitly requested.

Recommended review intervals:

```text
score null: immediate baseline
score 1: 2 days
score 2: 3 days
score 3: 5 days
score 4: 8 days
score 5: 13 days
score 6: 21 days
score 7: 34 days
score 8: 55 days
score 9: 89 days
score 10: 144 days
```

## Question Style

Ask one question at a time and wait for the answer.

Mix these types:

- Conceptual: "When would this pattern be useful?"
- Code reading: "What does this code path do?"
- Debugging: "What is likely wrong here?"
- Code writing: "Write a small version of this pattern."
- Comparison: "Why use this instead of that?"

Use repo examples and tutorial history whenever possible.

## Scoring

Use this rubric:

```text
1-3: cannot recall the concept; needs reteaching
4-5: vague memory or partial answer
6-7: solid understanding with minor gaps
8-9: strong grasp and handles edge cases
10: could teach the concept to someone else
```

After the quiz, update the tutorial frontmatter:

```yaml
understanding_score: 7
last_quizzed: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
```

Append this to `## Quiz History`:

```markdown
### Quiz - YYYY-MM-DD

**Q:** Question asked.
**A:** Brief summary of the learner's answer and what it revealed.
Score updated: 5 -> 7
```

Never update `understanding_score` during normal teaching. Only quiz mode changes it.
