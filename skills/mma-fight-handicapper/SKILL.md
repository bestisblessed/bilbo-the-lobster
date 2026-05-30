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
- Use local `odds-monitoring/UFC` odds snapshots when available, but verify current odds online when the user asks for betting value or the event is upcoming.
- Keep prediction separate from betting value.
- Label rumors as rumors. Do not present gossip as fact.
- Include source links in the final answer.
- Do not expose internal file names in user-facing output unless the user asks for implementation details.

## Tooling Fallback

Use subagents when the current environment exposes a subagent/delegation tool. If subagents are unavailable, run the same roles sequentially or with parallel read/search/tool calls. Keep separate notes for each role so the final synthesis still distinguishes coordinator, local data, historical form, style, market, news, integrity, quant, and devil's advocate work.

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

## Local Odds Source Priority

Primary local odds repo:

`$HOME/Code/odds-monitoring`

Primary UFC odds snapshots:

`$HOME/Code/odds-monitoring/UFC/Scraping/data/ufc_odds_fightoddsio_*.csv`

Supporting UFC odds code/context:

`$HOME/Code/odds-monitoring/UFC/Scraping/`

If the primary repo path is missing, search `$HOME/Code`, `$HOME/Documents`, the current workspace, and sibling workspaces for `odds-monitoring/UFC`. Do not name `mma-ai/Streamlit/data` as an odds source for this skill.

FightOdds CSV snapshots usually include `Event`, `Event_URL`, `FightOdds_Fight_ID`, `Fighters`, and sportsbook columns such as `betmgm`, `pinnacle-sports`, `draftkings`, `hard-rock-bet`, and `polymarket`. Use newest relevant snapshots first, but cross-check current market odds online for upcoming or live fight-week cards. Flag stale, one-book, broken, or extreme outlier rows before using them in the market read.

## Event URL Intake

For Sherdog, UFC, or Tapology URLs, normalize:

- Event name, date, and location.
- Main-card order.
- Scheduled rounds and weight classes.
- Fighter names, IDs, and aliases.
- Canceled bouts, late replacements, and current fight status.

Cross-check current card order with at least one current public source when the event is upcoming or in fight week.

## Odds Math

- Negative American odds implied probability: `abs(odds) / (abs(odds) + 100)`.
- Positive American odds implied probability: `100 / (odds + 100)`.
- Fair American odds from model probability `p`: if `p >= 0.5`, use `-100 * p / (1 - p)`; otherwise use `100 * (1 - p) / p`.
- When both sides of a market are available, calculate no-vig two-way probabilities before comparing model edge to market price.

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
- First use `$HOME/Code/odds-monitoring/UFC/Scraping/data/ufc_odds_fightoddsio_*.csv` for local FightOdds snapshots.
- Use `$HOME/Code/odds-monitoring/UFC/Scraping/` for supporting scraper/schema context if needed.
- If the expected path is missing, search for `odds-monitoring/UFC` in the fallback locations above.
- Verify current market prices online for upcoming or fight-week cards.
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
- Say whether local `odds-monitoring/UFC` odds snapshots were used, unavailable, or stale.
- Include citations for event/card, fighter/history, odds, and news/weigh-in/current-context sources when available.
- If local data or odds are missing, still give pick, method, risk, and confidence, but lower confidence and state which source class was missing.
