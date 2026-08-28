---
name: store-compliance
description: Audit, fix, and gate a mobile app for Apple App Store and Google Play submission so it is approved on the first try. Use when the user is preparing to submit, publish, or release an iOS or Android app; when they ask about App Store or Play Store rejection, review guidelines, policy compliance, privacy manifests, data safety forms, IAP/paywall rules, permissions, target API level, or metadata; when they got rejected and need to fix it; or when they mention TestFlight, App Store Connect, Play Console, EAS submit, or Fastlane deliver. Works for native iOS/Swift, native Android/Kotlin, React Native, Expo, Flutter, Unity, and Capacitor projects.
license: MIT
---

# Store Compliance — one-shot App Store & Play Store approval

Your job is to make this app pass review **the first time**. Not "probably fine" — pass.

A rejection costs 1–7 days and, on Play, can cost an account strike. The economics justify
being exhaustive. Work through the whole protocol; do not shortcut it because the app
"looks fine".

---

## Operating rules

1. **Never guess a guideline number.** Every finding cites an exact rule (`Apple 5.1.1(v)`,
   `Play XI.F`). If you can't cite it, it isn't a finding — it's an opinion, and you should
   label it as one.
2. **The merged/built artifact is the source of truth**, not the source file. Audit the
   *merged* `AndroidManifest.xml` and the *built* `Info.plist`. Library manifests merge in;
   build settings substitute values.
3. **Absence of evidence is a finding.** If you cannot find a Restore Purchases button, an
   account-deletion path, or a report control, report it as missing. Do not assume it's
   somewhere you didn't look — search, then report.
4. **Over-declaring is a violation too.** An unused permission, an orphan entitlement, or a
   nutrition-label entry with no matching traffic all fail review. Remove, don't justify.
5. **Auto-fix only what is unambiguous.** Config, manifests, plists, boilerplate UI strings,
   and missing standard links: fix. Product decisions, pricing, business model, content
   judgment, licensing: report and ask.
6. **Never fabricate compliance.** Do not write a privacy policy claiming practices you
   haven't verified. Do not fill a Data safety form with guesses. Do not claim an
   accessibility feature the app doesn't have. Every declaration must be traceable to
   something you actually observed in the code.
7. **Re-verify deadlines.** `references/deadlines.md` has a "last verified" date. If it's
   more than ~30 days old, run `verify-deadlines` before trusting version floors.

---

## Phase 0 — Scope

Ask (via AskUserQuestion when the user is present, otherwise assume and state it):

- **Target stores** — Apple, Google Play, or both?
- **Submission type** — first release of a new app, or an update to a live app?
  *(First releases are reviewed far more strictly on both stores.)*
- **Access** — do you have the repo, the store listing text/assets, and Console/Connect
  access, or only some of these?
- **Categories that change the rules** — does the app have any of: accounts/login, in-app
  purchases or subscriptions, ads, user-generated content, AI/LLM features, children as an
  audience, health data, financial services, crypto, gambling, VPN, MDM, location in the
  background?

Then create a task list covering Phases 1–7 so the user can watch progress.

---

## Phase 1 — Detect the stack

```bash
python3 scripts/oneshot.py detect --path <repo>
```

This identifies the project type and the file locations that matter:

| Stack | Signals | Config that matters |
|---|---|---|
| Native iOS | `*.xcodeproj`, `*.xcworkspace`, `Podfile` | `Info.plist`, `*.entitlements`, `PrivacyInfo.xcprivacy`, `project.pbxproj`, `Podfile.lock` |
| Native Android | `settings.gradle[.kts]`, `app/build.gradle[.kts]` | merged `AndroidManifest.xml`, `build.gradle`, `proguard-rules.pro`, `gradle.properties` |
| React Native | `package.json` with `react-native` | both native folders + `package.json` |
| Expo | `app.json` / `app.config.[jt]s`, `expo` dep | `app.json` `ios.infoPlist` / `android.permissions` / `android.blockedPermissions`, `eas.json` |
| Flutter | `pubspec.yaml` | `ios/Runner/Info.plist`, `android/app/build.gradle`, `pubspec.lock` |
| Unity | `ProjectSettings/ProjectSettings.asset` | Player Settings, exported native projects |
| Capacitor/Cordova | `capacitor.config.*`, `config.xml` | plugin manifests + native folders |

If a stack ships a *generated* native project, audit the **generated output** after a build
(`expo prebuild`, `flutter build`, Unity export), not just the config that generates it.

---

## Phase 2 — Deterministic scan

```bash
python3 scripts/oneshot.py audit --path <repo> --store both --format markdown --out oneshot-report.md
```

The scanner runs every mechanical rule in `scripts/rules/rules.yaml` and emits findings with
`rule_id`, `severity`, `guideline`, `file:line`, `evidence`, and `fix`. It covers:

- Info.plist purpose strings, encryption key, background modes, ATS, orientations
- Privacy manifest presence, structure, Required Reason API categories and reason codes
- Entitlement/capability orphans and `get-task-allow`
- Merged Android manifest: permissions, `debuggable`, `allowBackup`, cleartext, `exported`,
  foreground-service types, Billing metadata
- Gradle: `targetSdk`, `compileSdk`, `minifyEnabled`, ABIs, Billing Library version
- Native `.so` 16 KB alignment and 64-bit presence
- Restricted-permission → required-declaration mapping
- SDK inventory → expected privacy/data-safety declarations
- Payment SDKs vs. digital-goods signals (IAP steering)
- Paywall completeness heuristics, Restore Purchases presence
- Account creation without account deletion
- Privacy policy URL presence and reachability
- UGC signals without report/block controls
- LLM/AI endpoints without disclosure strings
- Placeholder text in strings and metadata across all locales
- Metadata field lengths, name/keyword rules, asset dimensions, icon alpha
- Debug artifacts, staging URLs, hardcoded IPv4, private-API selectors, secrets

**Read the report before doing anything else.** Everything the scanner found is a fact;
everything it *couldn't* check is what Phases 3–5 exist for.

---

## Phase 3 — Agent review (the parts a script can't judge)

Dispatch the specialist agents in `agents/`. They read the code, not just the config, and
each returns findings in the same schema as the scanner.

| Agent | Owns |
|---|---|
| `ios-compliance-auditor` | Apple guidelines 1–5 against the iOS codebase; Info.plist/entitlements/privacy manifest semantics; StoreKit correctness |
| `android-compliance-auditor` | Play policies against the Android codebase; merged manifest; permission justification; Play Billing correctness |
| `privacy-data-auditor` | The four-way reconciliation: code ↔ in-app disclosure ↔ store declarations ↔ privacy policy. ATT, prominent disclosure, account deletion, SDK data map |
| `monetization-auditor` | IAP-vs-external decision tree, paywall completeness, restore, subscription metadata, ads placement |
| `metadata-asset-auditor` | Listing text, names, keywords, screenshots, icons, age rating, declarations, localization |
| `content-policy-auditor` | UGC controls, AI moderation & disclosure, kids/Families, regulated categories, IP risk, 4.2/4.3 minimum-functionality judgment |
| `build-config-auditor` | SDK/Xcode floors, target API, 16 KB, 64-bit, R8, signing, debug artifacts, integrity checks that block reviewers |
| `submission-gatekeeper` | Merges everything, de-duplicates, decides GO / NO-GO, writes reviewer notes |

Run the seven auditors **in parallel**, then `submission-gatekeeper` on their combined
output. Give each agent the scanner report so they don't re-derive it.

If subagents aren't available in the current environment, run each agent's prompt yourself,
sequentially, keeping the same output schema — the checklists in `assets/` are written to be
usable either way.

---

## Phase 4 — Fix

Work findings in severity order: `BLOCKER` → `HIGH` → `MEDIUM` → `LOW`.

```bash
python3 scripts/oneshot.py fix --path <repo> --report oneshot-report.json --apply
# omit --apply for a dry run showing the exact diff
```

**Auto-fixable** (the fixer does these):
- Add/repair `PrivacyInfo.xcprivacy` with correct categories and reason codes
- Add missing `NS*UsageDescription` keys with drafted, feature-specific text
- Set `ITSAppUsesNonExemptEncryption`
- Remove orphan `UIBackgroundModes` and unused permissions
- Set `android:debuggable=false`, `allowBackup=false`, `usesCleartextTraffic=false`
- Bump `targetSdk`/`compileSdk` and Play Billing Library
- Add the `<queries>` block replacing `QUERY_ALL_PACKAGES`
- Add Terms/Privacy links and the renewal-disclosure block to a detected paywall
- Add a Restore Purchases action to a detected paywall
- Scaffold an in-app **Delete Account** screen wired to a `deleteAccount()` stub
- Scaffold a prominent-disclosure dialog before a sensitive permission request
- Scaffold report/block controls for detected UGC surfaces
- Replace placeholder strings flagged in any locale
- Strip the icon alpha channel; regenerate asset sizes

**Never auto-fixed** (report, explain, ask):
- Replacing an external payment flow with IAP
- Changing pricing, tiers, or the business model
- Removing a feature that violates content policy
- Anything requiring a licence, IRB approval, or an entity change
- Rewriting the app to clear the 4.2/4.3 minimum-functionality bar
- Anything where the "fix" is a factual claim you can't verify

Re-run `audit` after fixing. Iterate until the gate passes.

---

## Phase 5 — Behavioral verification

The scanner proves the config is right. **You must still prove the app behaves right.**
Walk the 22-row matrix in `references/submission-playbook.md` §4 — or at minimum these ten,
which account for most first-submission rejections:

1. Clean install on a physical device, oldest supported OS — no crash
2. IPv6-only / NAT64 network — fully functional (Apple's review network)
3. Every permission denied — app still usable, no dead ends
4. ATT denied — no IDFA read, no fingerprinting fallback
5. Demo account logs in from a device that never ran the app, with 2FA off
6. Sandbox purchase + cancel + **Restore Purchases from a signed-out fresh install**
7. Account creation → in-app deletion → data actually gone
8. UGC: report and block reachable in ≤ 2 taps from content *and* profile
9. Release build with R8/minification — no reflection crashes
10. Anti-tamper / root / emulator / Play Integrity checks do **not** block a lab device

Record evidence. Screen recordings of #6, #7, #8 and of any prominent-disclosure flow go
into the submission as attachments — they pre-empt the most common "we couldn't find it"
rejections.

---

## Phase 6 — Submission package

```bash
python3 scripts/oneshot.py notes --path <repo> --out review-notes.md
```

Produce, and hand the user:

- **Notes for Review** (Apple) — filled from the template in
  `assets/review-notes-template.md`, with real navigation paths for every feature,
  permission, paywall, deletion flow, and UGC control
- **App access instructions** (Play) — credentials + steps per gated area
- **Demo account** verified live, no expiry, 2FA disabled
- **Declaration checklist** — `assets/checklist-apple.md` and `assets/checklist-play.md`,
  every box ticked or explicitly waived with a reason
- **Data safety worksheet** — `assets/data-safety-worksheet.md`, filled from the SDK
  inventory the scanner produced
- **Attachments** — licence documents for regulated categories, demo videos for background
  location / all-files / SMS / accessibility, screen recordings for anything non-obvious

---

## Phase 7 — Gate

```bash
python3 scripts/oneshot.py gate --report oneshot-report.json --min-severity HIGH
# exit 0 = GO, exit 1 = NO-GO
```

**GO requires all of:**
- Zero `BLOCKER` findings
- Zero unwaived `HIGH` findings (a waiver is a written justification recorded in
  `.oneshot/waivers.yaml`, not a silence)
- Every declaration box ticked
- Phase 5 evidence captured
- Reviewer notes complete, with a demo account verified within the last 24 hours

Anything less is **NO-GO**. Say so plainly. Do not soften it — a NO-GO you talk the user out
of is a rejection you caused.

Wire the gate into CI:

```yaml
- run: python3 skills/store-compliance/scripts/oneshot.py audit --path . --format json --out report.json
- run: python3 skills/store-compliance/scripts/oneshot.py gate --report report.json
```

---

## If the user was already rejected

Skip to targeted mode:

```bash
python3 scripts/oneshot.py explain --guideline 5.1.1
```

Then follow `references/submission-playbook.md` §6:
1. Get the **exact guideline number** and the reviewer's attached evidence.
2. Reproduce in the **exact configuration named** — device, OS, network, region, account.
3. Decide fix vs. clarification. A clarification is answered **in Resolution Center without
   a new build**; uploading a build resets the queue and loses reviewer context.
4. Reply with the template in the playbook, naming exact navigation paths and attaching a
   screen recording.
5. Then run the full audit anyway — a rejection under one guideline usually means the
   submission wasn't audited under any of them.

---

## Reference files

Load these on demand; don't read them all up front.

| File | Read it when |
|---|---|
| `references/apple-guidelines.md` | Any Apple guideline question; full 1–5 rejection index |
| `references/apple-technical.md` | ITMS errors, plists, entitlements, privacy manifests, SDK floor, assets |
| `references/google-play-policies.md` | Any Play policy question; full policy index |
| `references/google-play-technical.md` | Target API, 16 KB, manifest, Gradle, pre-launch report, per-stack notes |
| `references/privacy-and-data.md` | The four-way reconciliation, ATT, prominent disclosure, deletion, regional law |
| `references/monetization.md` | IAP decision tree, paywall spec, StoreKit/Play Billing checklists, ads |
| `references/metadata-and-assets.md` | Listing specs, naming rules, screenshots, age rating, declarations |
| `references/content-ugc-ai-kids.md` | UGC controls, AI moderation, kids/Families, regulated categories |
| `references/submission-playbook.md` | Reviewer notes, demo accounts, test matrix, appeals |
| `references/deadlines.md` | Version floors and dates — **check the verified-on date** |

## Assets

| File | Use |
|---|---|
| `assets/checklist-apple.md` | Line-by-line pre-submission checklist, Apple |
| `assets/checklist-play.md` | Line-by-line pre-submission checklist, Play |
| `assets/review-notes-template.md` | Notes for Review / App access |
| `assets/data-safety-worksheet.md` | SDK → declaration mapping worksheet |
| `assets/PrivacyInfo.xcprivacy.template` | Starting privacy manifest with every legal reason code |
| `assets/privacy-policy-template.md` | Policy skeleton covering both stores' required sections |
| `assets/prominent-disclosure-snippets.md` | Swift/Kotlin/RN/Flutter disclosure + deletion + report/block patterns |

---

## Honest note on the success rate

This skill is built to drive first-submission approval to **≥ 98%** for the failure modes it
can observe — everything mechanical (config, manifests, declarations, metadata,
version floors) and everything procedural (demo accounts, reviewer notes, evidence). Those
are the large majority of rejections.

It cannot guarantee approval where the rejection is a **judgment call about your product**:
minimum functionality (4.2), spam/low-effort (4.3(b)), content appropriateness (1.1), or a
regulated category where you don't hold the licence. For those the skill tells you the risk
is present and what the bar is — but the answer is to change the product, not the config.
Say that plainly to the user rather than implying the gate can clear it.
