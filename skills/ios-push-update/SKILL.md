---
name: ios-push-update
description: Build, archive, upload, and submit the MMA AI iOS app update for App Store review. Use when the user says /iOSPushUpdate, iOSPushUpdate, asks to push an iOS update, archive the main MMA Swift app, upload a build to App Store Connect, fill required App Store Connect release fields, or submit the MMA AI app for review.
---

# iOS Push Update

## Purpose

Use this skill for the MMA AI Swift app release workflow: build/archive the main app code, upload the archive to App Store Connect, wait for the build to appear, complete required release metadata, and submit the version for App Review.

Keep the workflow narrow. Do not refresh MMA datasets, restart DonPablo, commit, push, merge, or modify unrelated code unless the user explicitly asks in the current turn.

## Preflight

1. Confirm the repo and branch:
   - Expected local path: `/Users/td/Code/mma-ai-swift-app`
   - Expected DonPablo path: `~/Code/mma-ai-swift-app`
   - Run `git status --short --branch`.
   - Note unrelated dirty files and leave them alone.
2. Confirm the Xcode project:
   - Project path: `<repo>/mma-ai-swift/MMAChat.xcodeproj`
   - App Store Connect app: `MMA AI`
3. Confirm release versioning before creating a build:
   - Check the latest App Store Connect version train.
   - Set `CFBundleShortVersionString` one minor version higher than the latest closed or approved App Store Connect version train.
   - Increment `CFBundleVersion` / build number as usual.
   - Verify only intended version/build files changed.
4. If the user asked only to prepare or upload, stop before final App Review submission. If the current-turn user request explicitly asks to submit for review, proceed through submission.

## Build And Archive

Prefer Xcode/XcodeBuildMCP for Apple build work when available. Use the Xcode UI when App Store signing, archive distribution, or App Store Connect upload requires authenticated local state.

Recorded Xcode UI path:

1. Open `MMAChat.xcodeproj` in Xcode.
2. Select the `mma-ai-swift` app scheme and a generic iOS/device distribution destination.
3. Run `Product > Clean Build Folder` when practical.
4. Run `Product > Archive`.
5. Wait until Xcode reports `Build Succeeded`.
6. In Archives Organizer, select the newest archive and choose `Distribute App`.
7. Choose the App Store Connect upload path and follow Xcode prompts.
8. Wait for Xcode to report that upload finished successfully.

If archive or upload fails, stop and report the exact Xcode error. Do not continue to App Store Connect metadata.

## Wait For Build Processing

1. Open App Store Connect for `MMA AI`.
2. Go to the intended iOS version or TestFlight build list.
3. Refresh until the uploaded build appears and is selectable.
4. Verify the selectable build matches the local `CFBundleShortVersionString` and `CFBundleVersion`.
5. If processing takes too long, report the current App Store Connect status and stop instead of selecting an older build.

## Fill Required App Store Connect Fields

Create or open the target iOS version and complete only required release fields. Use current project/release context, not personal details copied from recordings.

Required field checklist:

1. Version: must match `CFBundleShortVersionString`.
2. Build: select the newly uploaded build.
3. Promotional text: concise current update summary.
4. Description: accurate app description for MMA AI.
5. What's New: concise release notes for this update.
6. Keywords: comma-separated MMA/search terms within Apple limits.
7. Support URL and Marketing URL: use approved public project/support URLs.
8. Copyright: current owner/year text.
9. App Review Information:
   - Fill required contact fields from existing approved App Store Connect account context.
   - Do not expose phone numbers, emails, or private notes in chat summaries.
   - Mark sign-in required only if the app actually requires reviewer credentials.
10. App Store Version Release:
   - Use the release option requested by the user.
   - If unspecified, keep the existing page/default choice and mention it in the final report.

Save the page and confirm required-field errors are cleared before submission.

## Submit For Review

Only submit when the current user request explicitly asks to submit the app for review. Otherwise stop after saving metadata and selecting the build.

Submission path:

1. Click `Add for Review`.
2. Resolve any blocking warnings or missing required fields.
3. Click `Submit for Review`.
4. Verify App Store Connect shows the submitted iOS version in App Review with a current submission date and a review status such as `Waiting for Review` or `In Review`.

## Final Report

Report:

1. Repo branch and dirty-state summary.
2. Version/build values used.
3. Xcode clean/build/archive/upload result.
4. App Store Connect build selected.
5. Required metadata fields completed.
6. Final submission status, or the exact stopping point if not submitted.
7. Any remaining risks, especially build processing delays, missing screenshots, unresolved metadata errors, or Apple review warnings.
