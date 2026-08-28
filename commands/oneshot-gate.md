---
description: Final GO/NO-GO decision before submitting to the App Store or Google Play
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

Decide whether `$ARGUMENTS` (default: the current directory) is ready to submit.

```bash
python3 <CLI> gate --path <path>
```

That covers conditions 1, 2 and 6. **All six must hold for a GO:**

1. Zero `BLOCKER` findings — *scanner*
2. Zero unwaived `HIGH` findings — *scanner*. Waivers live in `.oneshot/waivers.yaml` and
   need a written reason and an unexpired date. `BLOCKER`s can never be waived.
3. Every box ticked in `assets/checklist-apple.md` and `assets/checklist-play.md` — *ask*
4. Behavioral evidence captured — *ask*. At minimum: clean install on a physical device,
   permission-denied paths, demo account login from a fresh device, Restore Purchases from
   a signed-out fresh install, account creation → deletion, UGC report/block
5. Reviewer notes complete, demo account **verified within the last 24 hours** — *ask*
6. Version floors met for the target submission date — *scanner*. Check
   `references/deadlines.md` and its verified-on date; run `verify-deadlines` if stale

Ask the user to confirm 3–5 explicitly. Do not assume them.

**Your decision has asymmetric costs.** A false GO costs days and possibly a Play account
strike. A false NO-GO costs an hour. Bias toward NO-GO, and never soften one because the
user is in a hurry — say plainly what must change to flip it.
