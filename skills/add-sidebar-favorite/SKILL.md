---
name: add-sidebar-favorite
description: Inventory the folders currently configured in SidebarFavorites Manager with visual previews of their macOS SF Symbol icons, recommend icons from the full SF Symbols catalog installed with macOS before opening the Add UI, then add a directory with the selected symbol, enable its File Provider extension, refresh, and verify it is Active. Use when the user invokes /add-sidebar-favorite or asks to list or add folders in Finder's sidebar through SidebarFavorites Manager.
---

# Add Sidebar Favorite

Use the bundled `scripts/sf_symbols.swift` for SF Symbol discovery and preview rendering. Use Computer Use only for reading SidebarFavorites Manager inventory and, after icon selection, operating SidebarFavorites Manager and System Settings. Identify controls from fresh accessibility state instead of replaying coordinates.

## Required inputs and gates

Collect or derive these values for every fresh run:

- Directory: after displaying the current favorites inventory, ask which existing directory to add. Resolve `~` for verification, but display the concise user-facing path.
- Favorite name: default to the directory basename. Ask only if the user wants a different label.
- Icon: recommend at least five context-appropriate built-in SF Symbols, show a visual preview of every option, and obtain an explicit selection before continuing.

Never carry the directory, label, icon, or approvals over from a previous run.

The user's explicit icon selection authorizes filling the Add Favorite form and clicking **Add** for that directory; do not ask for another Add confirmation. Still require a separate action-time confirmation immediately before turning on the matching File Provider extension in System Settings. A general request to run the skill does not satisfy the extension gate.

## Workflow

### 1. Inventory current favorites

Do not ask for a directory yet. Open SidebarFavorites Manager (`com.ivg-design.SidebarFavoritesManager`) with Computer Use and inspect fresh state. Before opening the Add Favorite sheet, read every configured favorite from the app:

- Capture the favorite name, directory path, SF Symbol identifier or displayed icon description, enabled toggle state, and runtime status such as **Active**, **Starting...**, or unavailable.
- Scroll through the favorites list until reaching the end. Re-inspect after every scroll and deduplicate entries by normalized directory path; do not assume the initial accessibility tree contains the full list.
- Produce a genuine visual preview for every configured icon with `scripts/sf_symbols.swift render`; deduplicate repeated identifiers and reuse the same preview for matching rows.
- Prefer a compact 32×32 px PNG resized from the script's AppKit-rendered output. If the table still feels vertically crowded, reduce previews to 28×28 px. Do not open Add Favorite to collect inventory previews.
- Save preview PNGs in a fresh temporary directory and reference them with absolute paths. Do not use emoji, unrelated web images, AI-generated substitutes, or an unverified approximation of the SF Symbol.
- Present the result before the icon suggestions in a neat Markdown table with columns `Favorite`, `Directory`, `Icon`, `Preview`, `Enabled`, and `Status`. Put an inline Markdown image in each `Preview` cell next to its symbol name, for example `![photo.fill](/absolute/path/photo.fill.png)`. Keep the image's intrinsic size at 32×32 px (or 28×28 px in the compact fallback) so the row height stays aligned with the text. Use `Unknown` only when the app does not expose a field after a fresh state and screenshot check.
- If the response renderer cannot display images inside table cells, keep the `Preview` column with numbered references such as `Preview 1` and place a compact, clearly numbered visual contact sheet immediately below the table. Maintain a one-to-one mapping between every row and its preview; do not silently omit visuals.
- State the total number of configured favorites. If none exist, say so plainly instead of rendering an empty table.

The inventory is read-only and requires no confirmation. End this turn after displaying it and ask: `Which directory would you like to configure next?` Do not generate icon suggestions until the user provides a directory.

### 2. Verify the directory and recommend icons without Computer Use

When the user provides a directory, verify that it exists and is a directory using a read-only filesystem check. Stop and explain if it does not exist. Default the favorite name to the directory basename.

Do not call Computer Use, open SidebarFavorites Manager, or open its Add Favorite sheet during this icon-proposal phase.

Use Apple's installed catalog at `/System/Library/CoreServices/CoreGlyphs.bundle/Contents/Resources/` through `scripts/sf_symbols.swift`:

- `symbol_order.plist` supplies the full installed symbol-name catalog, including symbols not shown in SidebarFavorites Manager's small picker.
- `symbol_search.plist` supplies Apple's search keywords.
- `NSImage(systemSymbolName:)` validates and renders each candidate using macOS itself.

Search broadly using the directory basename, meaningful tokens from the path, and a read-only inspection of the directory's apparent purpose. Example:

```bash
/usr/bin/swift scripts/sf_symbols.swift search --limit 80 library book reference data chart
```

Choose at least five context-appropriate, visually distinct results from the full output. Include symbols such as `baseball.fill`, `figure.boxing`, or other non-picker symbols whenever they fit. Follow Apple's SF Symbols guidance: prefer symbols that are simple, recognizable, inclusive, and directly related to the content; use a filled variant when extra visual emphasis is useful. Official references:

- <https://developer.apple.com/sf-symbols/>
- <https://developer.apple.com/design/human-interface-guidelines/sf-symbols>
- <https://developer.apple.com/documentation/appkit/nsimage/init(systemsymbolname:accessibilitydescription:)>

Render the shortlist into a fresh temporary directory before presenting it:

```bash
/usr/bin/swift scripts/sf_symbols.swift render /absolute/temp/directory symbol.one symbol.two symbol.three symbol.four symbol.five
```

Verify each PNG exists, opens, and shows its named symbol. Present a numbered list with the exact symbol name, a short rationale, and the individual PNG preview. Do not use SidebarFavorites Manager screenshots, emoji, web images, AI-generated substitutes, or guessed glyphs for these suggestions.

Ask the user to select one suggestion or name another built-in SF Symbol. If they name another symbol, render and show it with the same script before asking for confirmation. Stop until the user explicitly selects the icon.

### 3. Add the favorite after icon selection

After the user selects the symbol, re-inspect SidebarFavorites Manager in case it changed while waiting. Compare the resolved requested path with every current favorite. If it is already configured, identify the matching row and stop before opening Add Favorite.

Open **Add Favorite**, then select the directory with the direct-path flow:

1. Click **Browse...**.
2. Press macOS `command+shift+g`.
3. Enter the resolved absolute path in the **Go to:** field and submit it.
4. Click the chooser's **Select** button for that folder.

Set:

- **Name** to the confirmed label.
- **Folder Path** to the confirmed directory.
- **Type** to **SF Symbol**.
- **Symbol Name** to the confirmed symbol.

Inspect fresh state and verify the form contains the intended directory, label, and exact symbol name and that the Preview renders the chosen symbol. Then click **Add** without requesting another confirmation; the immediately preceding icon selection is the authorization for this step.

### 4. Locate and confirm the extension switch

After Add succeeds, inspect SidebarFavorites Manager and identify the new row. Use its **Enable Extension** action or the app's **Extensions** control to open **System Settings > General > Login Items & Extensions**.

Locate the extension that corresponds to the new favorite, normally `<favorite name> File Provider`. Use stable labels such as the favorite name, directory basename, `File Provider`, **Show Detail**, and the switch state. Do not choose an unlabeled button or switch unless fresh UI state or a screenshot establishes that it belongs to the matching extension.

If the matching switch is already on, do not toggle it. Report that no change is needed and continue to verification.

If it is off, show the exact extension name and current off state, then ask: `Turn on the <name> File Provider extension now?`

Stop here until the user explicitly confirms. After confirmation, re-inspect the System Settings detail view and turn on only that matching switch. Do not change any other login item, background activity, extension, privacy, security, or network setting.

### 5. Refresh and verify

Return to SidebarFavorites Manager. Use **Refresh** to restart its icon helpers and refresh Finder, then inspect fresh state.

Verify all of the following:

- The new row has the intended name and directory path.
- The row shows the selected SF Symbol.
- The row reports **Active** and its toggle is on.
- No unrelated favorite or extension was changed.

If the row remains in **Starting...**, refresh state once after the app finishes processing. If it still does not become Active, report the observed status and stop without making unrelated changes.

Conclude with the directory, label, SF Symbol name, extension name/state, and verification result.

## Computer Use rules

- Initialize Computer Use with `@oai/sky` and call `get_app_state` before acting.
- Prefer accessibility `element_index` targets over coordinates.
- Fetch fresh state after actions and never reuse stale element indices.
- After the user supplies a directory, do not use Computer Use during symbol discovery or suggestion; wait until the user selects a rendered symbol.
- Use screenshots only when accessibility text does not identify a UI control or when verifying the final Add form. Generate SF Symbol visuals with `scripts/sf_symbols.swift`.
- Before referencing a preview image, verify that its file exists, opens successfully, and shows the intended symbol.
- Treat preview files as temporary run artifacts; do not add them to the skill folder or another repository.
- If targeting an app by display name fails, retry with its bundle identifier obtained from `list_apps`.
- Do not install SidebarFavorites Manager, SF Symbols, or any other software. If the required app is missing, stop and tell the user.
- Listing all configured SidebarFavorites Manager favorites is authorized by invoking this skill. Do not expose unrelated account details, login items, or System Settings extensions, and crop icon-preview screenshots to the relevant Add Favorite area.
