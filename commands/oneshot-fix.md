---
description: Fix the App Store / Play compliance issues found by the audit, in severity order
argument-hint: "[path]"
---

## Locate the CLI

Use the first of these that exists; `${CLAUDE_PLUGIN_ROOT}` is only set under a plugin
install.

```
${CLAUDE_PLUGIN_ROOT}/skills/store-compliance/scripts/oneshot.py
~/.claude/skills/store-compliance/scripts/oneshot.py
./.claude/skills/store-compliance/scripts/oneshot.py
./skills/store-compliance/scripts/oneshot.py
```

Below, `<CLI>` means the path you resolved.

---

Fix the compliance findings for `$ARGUMENTS` (default: the current directory).

### 1. Have a report

If `oneshot-report.json` doesn't exist, run `/oneshot-audit` first.

### 2. Apply the mechanical fixes

Show the diff before writing anything:

```bash
python3 <CLI> fix --path <path>            # dry run — prints a unified diff
python3 <CLI> fix --path <path> --apply    # write it
```

### 3. Work the rest in severity order

`BLOCKER` → `HIGH` → `MEDIUM`. For each finding, read its `fix` field, make the change, and
verify the change **satisfies the guideline** rather than merely silencing the check.

The common ones the scanner flags but cannot fix — reference implementations are in
`skills/store-compliance/assets/prominent-disclosure-snippets.md`:

- In-app account deletion — Apple 5.1.1(v), Play XI.F
- Prominent disclosure before a sensitive permission — Play XI.C
- UGC report and block controls — Apple 1.2, Play VI
- Third-party AI disclosure and consent — Apple 5.1.2(i)
- Paywall disclosures and Restore Purchases — Apple 3.1.2(c), 3.1.1

### 4. Do not decide product questions

Replacing an external payment flow with IAP, changing pricing, removing a feature for
content policy, or restructuring an app to clear the 4.2/4.3 bar are the user's decisions.
Present the trade-off and ask.

### 5. Re-audit and iterate

```bash
python3 <CLI> audit --path <path> --format json --out oneshot-report.json
python3 <CLI> gate --report oneshot-report.json
```

Never mark a finding resolved because the scanner stopped reporting it. Confirm the
underlying requirement is genuinely met.
