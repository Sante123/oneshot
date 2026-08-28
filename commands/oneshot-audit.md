---
description: Full App Store + Google Play compliance audit of this app, ending in a GO/NO-GO verdict
argument-hint: "[path] [--store apple|play|both]"
---

## Locate the CLI

Use the first of these that exists. `${CLAUDE_PLUGIN_ROOT}` is only set when oneshot is
installed as a plugin, so never assume it.

```
${CLAUDE_PLUGIN_ROOT}/skills/store-compliance/scripts/oneshot.py
~/.claude/skills/store-compliance/scripts/oneshot.py
./.claude/skills/store-compliance/scripts/oneshot.py
./skills/store-compliance/scripts/oneshot.py
```

If none exist, oneshot is not installed — tell the user to run `python3 install.py` in the
oneshot repo, and stop. Below, `<CLI>` means the path you resolved.

---

Run the complete submission audit on `$ARGUMENTS` (default: the current directory),
following the protocol in the `store-compliance` skill.

### 1. Scope

Ask which stores, whether this is a first release or an update, and which of these apply:
accounts, IAP, ads, UGC, AI features, children, health, financial services, crypto,
gambling, VPN, background location. First releases are reviewed far more strictly.

If the session is unattended, state your assumption plainly and proceed.

### 2. Detect and scan

```bash
python3 <CLI> detect --path <path>
python3 <CLI> audit --path <path> --format json --out oneshot-report.json
python3 <CLI> audit --path <path> --out oneshot-report.md
```

**Build first if you can.** A source-only scan cannot verify the merged Android manifest,
16 KB native alignment, ABIs, or the build SDK version — it will say so as `INFO` findings.

```bash
./gradlew :app:processReleaseManifest && ./gradlew bundleRelease   # Android
```

### 3. Agent review

Dispatch these seven **in parallel**, passing each the scanner report so it doesn't
re-derive what is already known:

`ios-compliance-auditor` · `android-compliance-auditor` · `privacy-data-auditor` ·
`monetization-auditor` · `metadata-asset-auditor` · `content-policy-auditor` ·
`build-config-auditor`

### 4. Merge and decide

Run `submission-gatekeeper` on the combined output. It writes `oneshot-report.md`,
`review-notes.md`, `play-app-access.md`, `submission-checklist.md`, and `data-safety.md`.

### 5. Report

Lead with the verdict. Then blockers in fix order with effort estimates. Then the
judgment-call risks (Apple 4.2 minimum functionality, 4.3(b) low-effort, content) —
separately, with confidence, and noting the gate cannot clear them. Then what could not be
checked.

Be explicit about the difference between "this **will** be rejected" (mechanical, certain)
and "this **may** be rejected" (judgment, uncertain). Conflating them destroys the user's
ability to prioritize.
