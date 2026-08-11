---
name: add-sidebar-favorite
description: Inventory the folders currently configured in SidebarFavorites Manager with visual previews of their macOS SF Symbol icons, then add a directory to Finder sidebar favorites with a user-confirmed built-in symbol, enable the matching File Provider extension in System Settings, refresh the app, and verify the favorite is Active. Use when the user invokes /add-sidebar-favorite or asks to list or add folders in Finder's sidebar through SidebarFavorites Manager.
---

# Add Sidebar Favorite

Use Computer Use to operate SidebarFavorites Manager and System Settings. Treat the demonstrated workflow as the UI reference, but identify controls from fresh accessibility state and screenshots instead of replaying coordinates.

## Required inputs and gates

Collect or derive these values for every fresh run:

- Directory: after displaying the current favorites inventory, ask which existing directory to add. Resolve `~` for verification, but display the concise user-facing path.
- Favorite name: default to the directory basename. Ask only if the user wants a different label.
- Icon: recommend at least five context-appropriate built-in SF Symbols, show a visual preview of every option, and obtain an explicit selection before continuing.

Never carry the directory, label, icon, or approvals over from a previous run.

Require two separate action-time confirmations:

1. Immediately before clicking **Add** in SidebarFavorites Manager, show the directory, label, and chosen symbol and ask for confirmation.
2. After locating the newly created matching File Provider extension in System Settings, immediately before turning its switch on, show the exact extension name and ask for confirmation.

Do not combine or pre-collect these confirmations. A general request to run the skill does not satisfy either gate.

## Workflow

### 1. Inventory current favorites

Do not ask for a directory yet. Open SidebarFavorites Manager (`com.ivg-design.SidebarFavoritesManager`) with Computer Use and inspect fresh state. Before opening the Add Favorite sheet, read every configured favorite from the app:

- Capture the favorite name, directory path, SF Symbol identifier or displayed icon description, enabled toggle state, and runtime status such as **Active**, **Starting...**, or unavailable.
- Scroll through the favorites list until reaching the end. Re-inspect after every scroll and deduplicate entries by normalized directory path; do not assume the initial accessibility tree contains the full list.
- Produce a genuine visual preview for every configured icon. Deduplicate repeated symbol identifiers and reuse the same preview for matching rows.
- Prefer a compact 48–64 px square PNG cropped from SidebarFavorites Manager or from the Add Favorite sheet's rendered Preview after entering that exact symbol. Opening the sheet and changing its preview fields is read-only preflight: never click **Add**, and cancel the sheet after collecting previews.
- Save preview PNGs in a fresh temporary directory and reference them with absolute paths. Do not use emoji, unrelated web images, AI-generated substitutes, or an unverified approximation of the SF Symbol.
- Present the result before the icon suggestions in a neat Markdown table with columns `Favorite`, `Directory`, `Icon`, `Preview`, `Enabled`, and `Status`. Put an inline Markdown image in each `Preview` cell next to its symbol name, for example `![photo.fill](/absolute/path/photo.fill.png)`. Use `Unknown` only when the app does not expose a field after a fresh state and screenshot check.
- If the response renderer cannot display images inside table cells, keep the `Preview` column with numbered references such as `Preview 1` and place a compact, clearly numbered visual contact sheet immediately below the table. Maintain a one-to-one mapping between every row and its preview; do not silently omit visuals.
- State the total number of configured favorites. If none exist, say so plainly instead of rendering an empty table.

The inventory is read-only and requires no confirmation. End this turn after displaying it and ask: `Which directory would you like to configure next?` Do not generate icon suggestions until the user provides a directory.

### 2. Confirm the directory and prevent duplicates

When the user provides a directory, verify that it exists and is a directory using a read-only filesystem check. Stop and explain if it does not exist.

Re-inspect the configured favorites before comparison in case the app changed while waiting for the user's reply. If the inventory changed, show the updated rows. Compare the requested directory's resolved path with the current inventory. If it is already configured, identify the matching row and stop before opening Add Favorite to avoid a duplicate. Ask the user for a different directory or a separate request to edit the existing entry.

Re-inspect SidebarFavorites Manager, click **Add Favorite**, and use **Browse...** to select the requested directory. Selecting the directory in the chooser is preflight; do not click the final **Add** button.

### 3. Preview and confirm the icon

Use the Add Favorite sheet's built-in SF Symbol picker and preview to create a shortlist of at least five icons:

- Choose symbols whose meaning fits the directory name or apparent purpose.
- Use only symbols that the current app/system successfully renders in the Preview area.
- Prefer familiar, visually distinct symbols. Avoid five near-duplicates.
- For each candidate, enter or select the symbol, inspect the rendered Preview, and capture a clean app-only screenshot showing that icon preview.
- Present a numbered list with the symbol name, a short rationale, and its screenshot. If individual crops are unavailable, provide clearly labeled app-only screenshots, one per candidate; do not substitute text glyphs or emoji for the visuals.

Ask the user to select one of the suggestions or name another built-in SF Symbol. If they name another symbol, preview it and show its screenshot before asking them to confirm it. Do not continue until the user explicitly confirms the icon.

### 4. Prepare and confirm the favorite

Return to or preserve the Add Favorite sheet. Set:

- **Name** to the confirmed label.
- **Folder Path** to the confirmed directory.
- **Type** to **SF Symbol**.
- **Symbol Name** to the confirmed symbol.

Inspect fresh state and verify the Preview shows the chosen symbol and label. Present a compact summary and, when available, the clean Add Favorite screenshot. Ask: `Add this Finder sidebar favorite now?`

Stop here until the user explicitly confirms. After confirmation, re-inspect the sheet and click the current **Add** control. Never infer approval from the earlier icon selection.

### 5. Locate and confirm the extension switch

After Add succeeds, inspect SidebarFavorites Manager and identify the new row. Use its **Enable Extension** action or the app's **Extensions** control to open **System Settings > General > Login Items & Extensions**.

Locate the extension that corresponds to the new favorite, normally `<favorite name> File Provider`. Use stable labels such as the favorite name, directory basename, `File Provider`, **Show Detail**, and the switch state. Do not choose an unlabeled button or switch unless fresh UI state or a screenshot establishes that it belongs to the matching extension.

If the matching switch is already on, do not toggle it. Report that no change is needed and continue to verification.

If it is off, show the exact extension name and current off state, then ask: `Turn on the <name> File Provider extension now?`

Stop here until the user explicitly confirms. After confirmation, re-inspect the System Settings detail view and turn on only that matching switch. Do not change any other login item, background activity, extension, privacy, security, or network setting.

### 6. Refresh and verify

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
- Use screenshots when accessibility text does not identify a control or when generating icon visuals.
- Before referencing a preview image, verify that its file exists, opens successfully, and shows the intended symbol. Use app-only captures and exclude desktop or unrelated window content.
- Treat preview files as temporary run artifacts; do not add them to the skill folder or another repository.
- If targeting an app by display name fails, retry with its bundle identifier obtained from `list_apps`.
- Do not install SidebarFavorites Manager, SF Symbols, or any other software. If the required app is missing, stop and tell the user.
- Listing all configured SidebarFavorites Manager favorites is authorized by invoking this skill. Do not expose unrelated account details, login items, or System Settings extensions, and crop icon-preview screenshots to the relevant Add Favorite area.
