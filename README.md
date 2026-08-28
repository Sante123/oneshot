# oneshot

**Catch the issues that get iOS and Android apps rejected before you submit.**

`oneshot` is an open-source compliance toolkit for the Apple App Store and Google Play. It
combines a deterministic scanner, a researched knowledge base of every rejection-causing
rule on both stores, and eight specialist AI review agents into one workflow that ends in a
hard **GO / NO-GO** gate.

It works standalone (a Python CLI, no dependencies) and as a plugin for Claude Code and
Claude Cowork.

```bash
git clone https://github.com/Sante123/oneshot.git
python3 oneshot/skills/store-compliance/scripts/oneshot.py audit --path /path/to/your/app
```

---

## Why this exists

An App Store rejection costs 1–7 days. A Google Play policy violation can cost an account
strike, and three strikes can end the account. Almost all of it is preventable: the large
majority of rejections are **mechanical** — a missing plist key, an undeclared permission,
a paywall without a renewal statement, a target API level below the floor — or
**procedural** — a demo account that doesn't work, reviewer notes that don't say where the
feature is.

Those are exactly the things a machine can check. `oneshot` checks them, fixes what it
safely can, and refuses to say "ready" until they're all clear.

---

## What's in the box

```
oneshot/                             <- repo root IS the plugin root
├── .claude-plugin/
│   ├── plugin.json                  plugin manifest (must be at the root)
│   └── marketplace.json             marketplace manifest (must be at the root)
├── skills/store-compliance/
│   ├── SKILL.md                     the 7-phase protocol
│   ├── references/                  the researched knowledge base (10 documents)
│   ├── assets/                      checklists, templates, reference implementations
│   └── scripts/oneshot.py           the scanner, fixer, and gate (stdlib only)
├── agents/                          8 specialist reviewer agents
├── commands/                        /oneshot-audit, /oneshot-fix, /oneshot-gate, …
├── install.py                       direct installer (+ install.sh, install.ps1)
├── docs/                            INSTALL, ARCHITECTURE, PUBLISHING, methodology
├── tests/                           fixtures, scanner self-test, structure validator
└── .github/workflows/               CI
```

**The root layout is load-bearing.** `.claude-plugin/` must sit at the repository root —
if the contents end up nested one level deep, every installer fails with "no
marketplace.json". `tests/validate_structure.py` enforces this and CI runs it.

### The knowledge base

| Document | Covers |
|---|---|
| `references/apple-guidelines.md` | Every App Review Guideline 1–5, indexed by rejection |
| `references/apple-technical.md` | ITMS errors, plists, entitlements, privacy manifests, SDK floors, assets |
| `references/google-play-policies.md` | The full Play Developer Program Policy, indexed by rejection |
| `references/google-play-technical.md` | Target API, 16 KB pages, manifests, Gradle, per-stack notes |
| `references/privacy-and-data.md` | The four-way reconciliation: code ↔ disclosure ↔ declarations ↔ policy |
| `references/monetization.md` | The IAP-vs-external decision tree, paywall spec, StoreKit/Play Billing |
| `references/metadata-and-assets.md` | Listing specs, naming rules, screenshots, age rating |
| `references/content-ugc-ai-kids.md` | UGC controls, AI moderation, kids/Families, regulated categories |
| `references/submission-playbook.md` | Reviewer notes, demo accounts, the test matrix, appeals |
| `references/deadlines.md` | Hard deadlines and version floors, with a verified-on date |

### The agents

| Agent | Owns |
|---|---|
| `ios-compliance-auditor` | Apple guidelines against the iOS codebase; plists, entitlements, manifests, StoreKit |
| `android-compliance-auditor` | Play policies against the Android codebase; merged manifest, permissions, Billing |
| `privacy-data-auditor` | Reconciles code, in-app disclosure, store declarations, and the privacy policy |
| `monetization-auditor` | IAP classification, paywall completeness, restore, ads placement |
| `metadata-asset-auditor` | Listing text, names, keywords, screenshots, icons, age rating, declarations |
| `content-policy-auditor` | UGC, AI safety, kids/Families, IP, regulated categories, 4.2/4.3 judgment |
| `build-config-auditor` | SDK floors, target API, 16 KB, R8, signing, debug artifacts, integrity gates |
| `submission-gatekeeper` | Merges everything, decides GO/NO-GO, writes the reviewer notes |

---

## Install

Full guide, including troubleshooting: **[docs/INSTALL.md](docs/INSTALL.md)**.

### Direct install — always works

No marketplace, no manifest validation, no network. Python 3.8+.

```bash
git clone https://github.com/Sante123/oneshot.git
cd oneshot
python3 install.py           # copies into ~/.claude/{skills,agents,commands}
```

Windows:

```powershell
.\install.ps1                # or: python install.py
```

Then restart your Claude session and run `/oneshot-audit`.

```bash
python3 install.py --check       # what's installed
python3 install.py --project     # install into ./.claude instead of ~/.claude
python3 install.py --uninstall   # remove exactly what was installed
```

### As a Claude Code / Cowork plugin

```
/plugin marketplace add Sante123/oneshot
/plugin install oneshot@oneshot
```

Or from a local clone:

```
/plugin marketplace add /absolute/path/to/oneshot
/plugin install oneshot@oneshot
```

If the installer says **"not a marketplace — no `marketplace.json`"**, the repository
contents are almost certainly nested one level deep. Run the validator, which reports the
problem and the exact fix:

```bash
python3 tests/validate_structure.py
```

### Standalone — no Claude at all

The scanner is a plain Python program with **no third-party dependencies**:

```bash
python3 skills/store-compliance/scripts/oneshot.py audit --path ~/code/my-app
```

Python 3.9+. The `skills/store-compliance/scripts/` directory is self-contained — copy it
anywhere.

---

## Usage

```bash
ONESHOT=skills/store-compliance/scripts/oneshot.py

# What kind of project is this?
python3 $ONESHOT detect --path ~/code/my-app

# Full audit, both stores, markdown report
python3 $ONESHOT audit --path ~/code/my-app --out oneshot-report.md

# Apple only, JSON for tooling
python3 $ONESHOT audit --path ~/code/my-app --store apple --format json --out report.json

# See what would be fixed (dry run shows a unified diff)
python3 $ONESHOT fix --path ~/code/my-app

# Apply the safe fixes
python3 $ONESHOT fix --path ~/code/my-app --apply

# GO / NO-GO — exits 1 on NO-GO
python3 $ONESHOT gate --path ~/code/my-app

# Generate reviewer notes seeded from what's in the repo
python3 $ONESHOT notes --path ~/code/my-app --out review-notes.md

# What does guideline 5.1.1 actually say?
python3 $ONESHOT explain --guideline 5.1.1

# Are the version floors still current?
python3 $ONESHOT verify-deadlines
```

### In CI

```yaml
- name: App store compliance gate
  run: |
    python3 oneshot/skills/store-compliance/scripts/oneshot.py \
      audit --path . --format json --out oneshot-report.json --fail-on-findings
```

---

## What it checks

**Apple** — purpose strings (presence *and* quality), export compliance, background modes,
ATS, privacy manifest structure and Required Reason API reason codes, orphan entitlements,
`get-task-allow`, private API usage, `UIWebView`, IPv6 readiness, ATT, Sign in with Apple,
account deletion, paywall disclosures, Restore Purchases, IAP-vs-external classification,
review-prompt abuse, build SDK floor, icon alpha, name/keyword/description rules.

**Google Play** — target API level, Play Billing version, 16 KB page alignment, 64-bit
ABIs, `debuggable`, `allowBackup`, cleartext traffic, foreground service types, the full
restricted-permission set mapped to required Console declarations, prominent disclosure,
Data safety consistency, account deletion, UGC controls, AI reporting, lending-app
permission bans, listing specs, integrity checks that block review devices.

**Both** — placeholder text in every locale, staging endpoints in release, committed
secrets, the SDK-to-declaration data map, third-party AI disclosure, minimum-functionality
risk.

Findings carry a `rule_id`, a severity, an **exact guideline citation**, `file:line`
evidence, why it matters, and a concrete fix.

---

## The gate

`GO` requires **all** of:

1. Zero `BLOCKER` findings
2. Zero unwaived `HIGH` findings
3. Every declaration box ticked (`assets/checklist-apple.md`, `assets/checklist-play.md`)
4. Behavioral evidence captured (`references/submission-playbook.md` §4)
5. Reviewer notes complete, demo account verified within 24 hours
6. Version floors met for the target date

Waivers live in `.oneshot/waivers.yaml` and require a written reason:

```yaml
- rule_id: APPLE-2.5.4-BGMODES
  reason: "audio background mode is used by the podcast player at Player/AudioSession.swift:120"
  approved_by: patrick
  date: "2026-08-19"
  expires: "2026-11-19"
```

**`BLOCKER` findings cannot be waived.** Silence is not a waiver, and an expired waiver is
not a waiver.

---

## Supported stacks

Native iOS (Swift/Objective-C), native Android (Kotlin/Java), React Native, Expo, Flutter,
Unity, Capacitor/Cordova. The scanner detects the stack and adapts.

For stacks that generate their native projects (Expo, Flutter, Unity), audit the
**generated output** after a build — `expo prebuild`, `flutter build`, Unity export — not
just the config that generates it. The scanner tells you when it's only seeing source.

---

## Honest limits

`oneshot` is built to drive first-submission approval to **≥ 98%** for the failure modes it
can observe — everything mechanical and everything procedural. Those are the large majority
of rejections.

It **cannot** guarantee approval where the rejection is a judgment call about your product:

- **Apple 4.2** — minimum functionality. Is it more than a repackaged website?
- **Apple 4.3(b)** — spam and low-effort apps. Tightened in June 2026 specifically against
  AI-assisted submissions. If your app is a thin wrapper around a model API, no config
  change saves it.
- **Apple 1.1 / Play I** — content appropriateness.
- **Regulated categories** — if you don't hold the licence, you don't ship.

For those, the toolkit tells you the risk is present and what the bar is. The answer is to
change the product, not the config. It will say so plainly rather than implying the gate
can clear it.

It also cannot check what it cannot see: runtime behavior, live URLs, and the state of your
App Store Connect and Play Console accounts. Every report ends with an explicit
"what this scan could not check" section for exactly that reason.

---

## Keeping it current

Store rules change. `references/deadlines.md` carries a **last-verified date**, and
`verify-deadlines` warns when the rule catalog is more than 30 days old.

If you spot a stale rule, please open a PR — update **both** the reference document and
`scripts/oneshot_lib/catalog.py`, and cite the source. See `CONTRIBUTING.md`.

---

## Development

```bash
python3 tests/run_tests.py            # scanner behavior
python3 tests/validate_structure.py   # installability
```

`run_tests.py` audits two fixtures: `tests/fixtures/bad-app` (deliberately non-compliant,
must produce every expected rule and a NO-GO) and `tests/fixtures/good-app` (compliant,
must produce no false positives and a GO). It also asserts every finding carries a
guideline citation and a fix.

`validate_structure.py` checks that the repo is installable three ways — as a plugin, as a
marketplace, and by `install.py` — and reports the exact command to fix anything broken.
Run it before every push.

See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for how the layers fit together and
where to change things, and **[CONTRIBUTING.md](CONTRIBUTING.md)** for the bar a new rule
or check has to clear.

---

## License

MIT — see [LICENSE](LICENSE).

Not affiliated with Apple or Google. Guideline text is summarized, not reproduced; the
authoritative sources are linked throughout. **This is not legal advice.**
