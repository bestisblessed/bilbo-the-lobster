---
name: mma-fight-handicapper
description: Use when handicapping MMA/UFC fights, fight cards, main cards, betting odds, method-of-victory predictions, fighter style matchups, current fight-week news, weirdness/integrity signals, or quantified win probabilities from local mma-ai data and web research.
---

# MMA Fight Handicapper

Use this skill to produce structured fight predictions for any supplied MMA event, bout list, Sherdog/Tapology/UFC link, or fighter matchup.

## Core Rules

- Treat current fight cards, odds, weigh-ins, injuries, replacements, and news as time-sensitive. Browse current sources.
- Prefer verified event pages, official promotion pages, weigh-in reports, sportsbook/odds pages, Sherdog/Tapology/UFCStats, and credible MMA reporting.
- Use the user's local `mma-ai` data before web-only profile reconstruction.
- Use local odds snapshots when available, but verify current odds online when the user asks for betting value or the event is upcoming.
- Keep prediction separate from betting value.
- Label rumors as rumors. Do not present gossip as fact.
- Include source links in the final answer.
- Do not expose internal file names in user-facing output unless the user asks for implementation details.

## Local Data Source Priority

Primary local data directory:

`$HOME/Code/mma-ai/Scrapers/data`

Expand `$HOME` from the active shell/user environment at runtime. Do not hardcode a user-specific home directory.

Before building fighter profiles or historical form, check this directory first. Expected files include:

- `fighter_info_TAGGED.csv`: preferred fighter profile source when available.
- `fighter_info.csv`, `fighter_info_MEN.csv`, `fighter_info_WOMEN.csv`: fallback profile files.
- `event_data_sherdog_TAGGED.csv`: preferred historical bout/event source when available.
- `event_data_sherdog.csv`, `event_data_sherdog_MEN.csv`, `event_data_sherdog_WOMEN.csv`: fallback historical bout/event files.
- `fighter_id_sherdog.csv`: use for fighter ID/name mapping when needed.
- `event_urls_sherdog.csv`: use for Sherdog event URL/event metadata cross-checks when needed.
- `fighters/`: use as a normal enrichment source for fighter-specific pages, cached profile details, aliases, and profile gaps after loading the core CSV profile rows.
- `github/`: use as a normal enrichment source for repo-exported metadata, generated artifacts, or supplemental structured files after loading the core CSV profile/history rows.
- `tapology/`: use as a normal enrichment source for Tapology-derived cached context when relevant, especially aliases, records, ranking/context notes, and profile gaps.

If `$HOME/Code/mma-ai/Scrapers/data` is missing or incomplete:

1. Search likely local repo locations first, especially `$HOME/Code`, `$HOME/Documents`, the current workspace, and sibling workspaces, for `mma-ai/Scrapers/data`.
2. If still unavailable, look for the `mma-ai` repository on GitHub or the user's configured remotes and read/clone only as needed.
3. If cloning or network access is required, explain the action and use the safest available tool/approval path.
4. If neither local nor remote data is available, continue with web sources but lower confidence and state that local historical/profile data was unavailable.

## Workflow

### 1. Coordinator

Verify:

- Event name, date, location
- Main card order
- Fight weights and scheduled rounds
- Fighter names and aliases
- Late replacements or canceled bouts
- Supplied user facts

Output a normalized bout list.

### 2. First Parallel Wave

Spawn these agents in parallel where possible:

**Local Fighter Data Agent**
- First read `$HOME/Code/mma-ai/Scrapers/data`.
- Prefer `fighter_info_TAGGED.csv`; fall back to the gender-specific or untagged fighter profile files.
- Use `fighter_id_sherdog.csv` for ID/name mapping where relevant.
- Also inspect `fighters/`, `github/`, and `tapology/` for each requested fighter to enrich aliases, cached profile facts, missing reach/stance/gym/nationality fields, and conflicting-source flags.
- Build fighter profiles: record, age if available, nationality, gym, stance, height, reach, weight class, win/loss methods, durability, finishing rates, and missing-data flags.
- Treat user-supplied verified facts as authoritative.

**Historical Bout Form Agent**
- First read `$HOME/Code/mma-ai/Scrapers/data`.
- Prefer `event_data_sherdog_TAGGED.csv`; fall back to gender-specific or untagged event files.
- Also inspect `fighters/`, `github/`, and `tapology/` for cached fight-history details, fighter-page records, opponent aliases, event metadata, and fields missing from the event CSVs.
- Study recent fights, opponent quality, layoffs, weight-class moves, finish/decision trends, round-by-round risk, and archetype results.

**Style Matchup Agent**
- Use local fighter profile/history findings plus current public stats.
- Analyze striking, grappling, pace, wrestling control, submission threat, takedown defense assumptions, cardio, stance, reach/height, durability, and paths to victory.

**Market And Odds Agent**
- Gather openers/current odds when available.
- Use local odds snapshots if present in nearby repos, then verify current market prices online.
- Convert American odds to implied probability.
- Flag steam, stale lines, disagreement across books, and price/value gaps.
- Separate prediction from betting value.

**Current News And Rumor Agent**
- Search recent fight-week context.
- Look for injuries, camp changes, travel, visa issues, bad weight cuts, short-notice replacements, interviews, social media noise, suspicious line movement, and credible reporting.
- Label unverified talk as rumor.

### 3. Second Parallel Wave

Run after the first wave returns:

**Integrity And Weirdness Agent**
- Look for abrupt odds movement, replacement timing, missing media/weigh-in obligations, narrative shifts, suspicious chatter, unusual market behavior, or conflicting reports.
- Return risk level: none, low, medium, high.

**Quant/Model Agent**
- Convert evidence into:
  - Win probability
  - Method probabilities
  - Round/time lean
  - Confidence band
  - Fair American odds
- Lower confidence for thin, stale, or contradictory data.

**Devil's Advocate Agent**
- Attack the favorite case.
- Explain why the pick could be wrong.
- State what would flip the prediction.
- Say whether the market already priced in the edge.

### 4. Final Handicapper Output

For each fight, produce:

- Pick
- Likely method
- Round/time lean
- Estimated win probability
- Fair odds
- Current market odds if available
- Betting value: bet/pass/dog-only/price-dependent
- Key reasons
- Biggest risk
- Weirdness level

Use this compact table format:

| Fight | Pick | Method | Model | Fair Odds | Market Read | Weirdness |
|---|---:|---|---:|---:|---|---|

Then add short notes per fight:

- Why the pick wins
- Why it could fail
- What price would make it bettable

## Confidence Guide

- High: strong data, stable fight, aligned style/read/model, no major weirdness.
- Medium: clear pick but price, volatility, age, durability, or stylistic risk matters.
- Low: close model, thin data, short-notice context, major weirdness, or volatile heavyweight/light-heavyweight finishing profile.

## Final Answer Requirements

- Cite sources with links.
- State the date/time context for odds/news.
- Mention whether all fighters made weight if weigh-ins are available.
- Clearly separate prediction from betting value.
- Include remaining risks.
- Say whether local `mma-ai` data was used, unavailable, or partially incomplete.
