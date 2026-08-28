# Contributing to oneshot

The most valuable contribution to this project is **keeping the rules current**. Apple and
Google change their guidelines several times a year, and a stale rule is worse than no
rule — it makes someone confident about the wrong thing.

## Reporting a stale or wrong rule

Use the **Stale or incorrect rule** issue template. It asks for:
- The rule ID or reference document section
- What it currently says
- What it should say
- **A link to the authoritative source** (developer.apple.com or
  support.google.com / developer.android.com — not a blog post)

## Updating a rule

A rule lives in **two places**, and both must change together:

1. The human-readable reference in `skills/store-compliance/references/`
2. The machine catalog in `skills/store-compliance/scripts/oneshot_lib/catalog.py`

Also update:
- `references/deadlines.md` — including the **"Last verified"** date at the top
- `catalog.FLOORS["verified_on"]`
- The Sources list at the bottom of the reference document

## Adding a check

1. Add the knowledge to the relevant reference document first, with a citation. If a rule
   isn't documented, it doesn't get a check.
2. Add any pattern or table entry to `catalog.py`.
3. Implement the check in the right module:
   - `checks/ios.py` — Apple-specific
   - `checks/android.py` — Play-specific
   - `checks/crosscut.py` — applies to both
   - `checks/metadata.py` — store listing and assets
4. Emit a `Finding` with **all** of:
   - a stable `rule_id` (`APPLE-*`, `PLAY-*`, `XPLAT-*`, `META-*`)
   - a `severity` — see the bar below
   - an **exact** `guideline` citation
   - `file` and `line` where the evidence is
   - `evidence` a human can verify without re-running the tool
   - `impact` explaining what happens at review
   - `fix` that is specific and actionable, not "make it compliant"
   - `confidence` if it's anything less than certain
5. Add the rule to `tests/run_tests.py` — to `BAD_EXPECTED` and, where it should not fire,
   to `GOOD_FORBIDDEN`. Extend the fixtures as needed.
6. Run `python3 tests/run_tests.py`.

### The severity bar

| Severity | Means |
|---|---|
| `BLOCKER` | Ship this and rejection is near-certain. Cannot be waived. |
| `HIGH` | Frequently rejected. Blocks the gate unless waived with a written reason. |
| `MEDIUM` | Rejected in some review passes. Warn loudly. |
| `LOW` | Best practice; reduces reviewer friction. |
| `INFO` | Coverage gap — something the scan could not verify. Never a judgment. |

**Do not inflate severity to get attention.** A `BLOCKER` that isn't one teaches users to
ignore blockers, and that is how someone ships a real one.

## Adding an auto-fix

Auto-fixes go in `scripts/oneshot_lib/fixer.py` and must be:

- **Idempotent** — running twice changes nothing the second time
- **Unambiguous** — no guessing at intent
- **Reviewable** — the dry run shows a readable unified diff
- **Reversible** — no deletions the user cannot reconstruct

Add the `rule_id` to `FIXABLE` only if all four hold. Things that require a product,
pricing, licensing, or content decision are reported, never fixed. Things that require a
change outside the repo (App ID capabilities, Console declarations, provisioning profiles)
are reported, never fixed.

## Adding or changing an agent

Agents live in `agents/*.md`. Keep the shared output schema — the gatekeeper merges on it.
Each agent must instruct its model to cite a guideline for every finding and to report a
`coverage` object naming what it could not check.

## Before you push

Two checks, both fast:

```bash
python3 tests/validate_structure.py   # installability
python3 tests/run_tests.py            # scanner behavior
```

`validate_structure.py` exists because of a real failure: the repository contents ended up
nested one level deep, so `.claude-plugin/marketplace.json` was not at the root, and every
installer rejected the repo with "not a marketplace". The symptom gave no hint of the
cause. The validator catches that and prints the exact `git mv` commands to fix it.

**Never move `.claude-plugin/` out of the repository root.** It is where the plugin loader,
the marketplace loader, and `install.py` all look. `docs/ARCHITECTURE.md` § Distribution
explains why the layout is strict.

## Style

- Python: standard library only, 4-space indent, ~95 column soft limit, type hints where
  they clarify.
- **No new runtime dependencies.** The scanner must run anywhere Python 3.9 does.
- Markdown: reference documents are written to be read by both a model and a person. Lead
  with the rule, then what gets rejected, then the fix.

## Not accepted

- Rules without an authoritative citation (a blog post is not a citation)
- Checks that produce false positives on the `good-app` fixture
- Auto-fixes that make a decision the user should make
- Claims that the tool guarantees approval — it does not, and saying so would be
  dishonest to the people relying on it
