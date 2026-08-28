# Architecture

How the pieces fit, and where to change things.

```
                        ┌───────────────────────────────┐
   /oneshot-audit ─────►│  SKILL.md — the 7-phase       │
   "audit my app"       │  protocol Claude follows      │
                        └───────────┬───────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
   ┌──────────────────┐  ┌────────────────────┐  ┌──────────────────┐
   │  scripts/        │  │  agents/           │  │  references/     │
   │  oneshot.py      │  │  8 specialists     │  │  the rulebook    │
   │  (deterministic) │  │  (judgment)        │  │  (10 documents)  │
   └────────┬─────────┘  └─────────┬──────────┘  └──────────────────┘
            │                      │                      ▲
            │  findings            │  findings            │ cited by both
            └──────────┬───────────┘                      │
                       ▼                                  │
            ┌──────────────────────┐                      │
            │ submission-gatekeeper│──────────────────────┘
            │  merge → GO / NO-GO  │
            └──────────┬───────────┘
                       ▼
      oneshot-report.md · review-notes.md · submission-checklist.md
```

---

## The three layers

### 1. The rulebook — `skills/store-compliance/references/`

Ten markdown documents, ~21,000 words, written to be read by **both a model and a
person**. Every rule states what gets rejected and how to fix it, and every document ends
with the authoritative sources it was built from.

This layer is the product. The scanner and the agents are both ways of applying it.

**Changing a rule means changing this layer first**, then mirroring the machine-readable
part into `catalog.py`. A check without a documented rule is not accepted — see
`CONTRIBUTING.md`.

### 2. The scanner — `skills/store-compliance/scripts/`

Standard library only, Python 3.9+, no third-party dependencies. Deliberately dumb and
deliberately fast: it decides only what is decidable from files on disk.

```
scripts/
├── oneshot.py                  CLI: detect, audit, fix, gate, notes, explain,
│                               verify-deadlines
└── oneshot_lib/
    ├── model.py                Finding dataclass, FindingList, severity ranking
    ├── util.py                 filesystem, plist parsing, grep, minimal YAML
    ├── detect.py               stack detection → Project descriptor
    ├── catalog.py              the machine-readable rule tables + version floors
    ├── fixer.py                idempotent auto-fixes with a unified diff
    ├── report.py               markdown/text rendering + the gate
    └── checks/
        ├── ios.py              Apple: plists, manifests, entitlements, StoreKit
        ├── android.py          Play: merged manifest, permissions, Gradle, .so
        ├── crosscut.py         both: privacy, accounts, UGC, AI, hygiene
        └── metadata.py         listing text, icons, screenshots, declarations
```

**Data flow:** `detect()` builds a `Project` describing where everything lives → each
`checks/*.check(proj)` yields `Finding` objects → `dedupe()` and `ranked()` →
`report.gate()` decides → `report.render_*()` prints.

Every `Finding` carries `rule_id`, `severity`, `store`, an **exact guideline citation**,
`file:line`, `evidence`, `impact`, `fix`, and `confidence`. Nothing else is a finding.

### 3. The agents — `agents/`

Eight markdown agent definitions. They read code, not just config, and handle everything
the scanner can't decide: whether a purpose string is honest, whether an app clears the
minimum-functionality bar, whether the AI feature is moderated.

They emit **the same finding schema** as the scanner, which is what lets
`submission-gatekeeper` merge the two streams and de-duplicate.

---

## Severity, and why it is load-bearing

| Severity | Means | Gate behavior |
|---|---|---|
| `BLOCKER` | Rejection near-certain | Fails the gate. **Cannot be waived.** |
| `HIGH` | Frequently rejected | Fails the gate unless waived with a written reason |
| `MEDIUM` | Rejected in some review passes | Reported, does not fail |
| `LOW` | Best practice | Reported |
| `INFO` | **A coverage gap** — something the scan could not verify | Never a judgment |

`INFO` is the honest one. `PLAY-ARTIFACT-MISSING` doesn't mean the app is fine; it means
nobody checked. Every report ends with a "what this scan could not check" section for the
same reason.

Inflating severity to get attention teaches users to ignore blockers, which is how
somebody ships a real one.

---

## The gate

`GO` requires six conditions. Only the first two are mechanical:

1. Zero `BLOCKER` findings — *scanner*
2. Zero unwaived `HIGH` findings — *scanner*
3. Every declaration box ticked — *human*
4. Behavioral evidence captured — *human*
5. Reviewer notes complete, demo account verified within 24h — *human*
6. Version floors met for the target date — *scanner + `verify-deadlines`*

A scanner-only gate would be dishonest: it cannot see whether the app crashes on the
reviewer's device, whether the demo account works, or whether the Console declarations are
filled. Conditions 3–5 are human attestations, and the checklists exist to make lying to
yourself difficult.

**Waivers** live in `.oneshot/waivers.yaml` and need a reason, an approver, and an expiry.
Silence is not a waiver. An expired waiver is not a waiver. `BLOCKER`s can never be
waived — if one is genuinely wrong, that's a bug in the rule, and the fix is a PR.

---

## The auto-fixer

`fixer.py` applies only changes that are **idempotent, unambiguous, reviewable, and
reversible**. `FIXABLE` is an explicit allow-list; a finding marked `auto_fixable` that
isn't on it is reported but never touched.

Deliberately excluded, with the reasoning in the code:

- `META-LEN-*` — truncating a name or description is a branding decision, and a machine
  trim reads as broken copy. The finding carries a word-boundary-safe suggestion instead.
- `APPLE-2.5.4-ORPHANENT` — removing an entitlement also requires changing the App ID
  capabilities and the provisioning profile, which the fixer can't do.
- Anything touching pricing, business model, content, or licensing.

---

## Staleness is the main failure mode

The most likely way this project hurts someone is by being confidently out of date.

- `references/deadlines.md` carries a human-readable **last-verified date**.
- `catalog.FLOORS["verified_on"]` carries the same date machine-readably.
- `oneshot verify-deadlines` prints every floor and deadline with its status and **exits
  non-zero past 30 days**.
- CI runs it on every push.

`CONTRIBUTING.md` requires the reference document and `catalog.py` to be updated together,
with a citation to an authoritative source.

---

## Distribution

The repository is simultaneously three things, which is why the root layout is strict:

| It is a… | Because of | Entry point |
|---|---|---|
| Claude **plugin** | `.claude-plugin/plugin.json` at the root | auto-discovery of `skills/`, `agents/`, `commands/` |
| Claude **marketplace** | `.claude-plugin/marketplace.json` at the root, `"source": "./"` | `/plugin marketplace add` |
| Plain **Python tool** | `skills/store-compliance/scripts/` being self-contained | `python3 oneshot.py` |
| Directly **installable** | `install.py` at the root | copies into `~/.claude/` |

`tests/validate_structure.py` enforces all four, and CI runs it. It exists because the
failure it catches — contents nested one level deep — is silent, and the only symptom is
an installer saying "no marketplace.json".

---

## Test strategy

| Test | Catches |
|---|---|
| `tests/run_tests.py` | Missing detections (`bad-app` must produce 35 named rules and NO-GO) and false positives (`good-app` must produce none and GO). Also asserts every finding has a citation and a fix. |
| `tests/validate_structure.py` | Broken install layout, malformed manifests, mismatched agent/skill names |
| CI `compileall` | Syntax errors across Python 3.9 / 3.11 / 3.13 |

Two fixtures, both deliberate:

- `tests/fixtures/bad-app` — a small project that violates ~35 rules on purpose
- `tests/fixtures/good-app` — a compliant project of the same shape

A new check must extend both. **A false positive on `good-app` is a bug, not noise.**
