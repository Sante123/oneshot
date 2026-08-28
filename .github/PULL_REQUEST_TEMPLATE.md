## What this changes

<!-- One or two sentences. -->

## Type

- [ ] New or corrected **store rule**
- [ ] New or corrected **check**
- [ ] Auto-fix
- [ ] Agent
- [ ] Tooling / docs / CI

## If this touches a store rule

A rule lives in two places and **both must change together**:

- [ ] The reference document in `skills/store-compliance/references/`
- [ ] The machine catalog in `skills/store-compliance/scripts/oneshot_lib/catalog.py`
- [ ] `references/deadlines.md` — including the **Last verified** date
- [ ] `catalog.FLOORS["verified_on"]`
- [ ] The Sources list at the bottom of the reference document

**Authoritative source:**
<!-- developer.apple.com / support.google.com / developer.android.com. Not a blog post. -->

## If this adds a check

- [ ] The rule is documented in a reference file first, with a citation
- [ ] The finding carries a stable `rule_id`, a `severity`, an **exact** guideline
      citation, `file`/`line`, verifiable `evidence`, `impact`, and an actionable `fix`
- [ ] Severity is honest — see the bar in `CONTRIBUTING.md`. A `BLOCKER` that isn't one
      teaches people to ignore blockers
- [ ] Added to `BAD_EXPECTED` in `tests/run_tests.py`, and to `GOOD_FORBIDDEN` where it
      must not fire
- [ ] Fixtures extended if needed

## If this adds an auto-fix

- [ ] Idempotent — running twice changes nothing the second time
- [ ] Unambiguous — no guessing at intent
- [ ] Reviewable — the dry run shows a readable diff
- [ ] Reversible — nothing the user cannot reconstruct
- [ ] Makes no product, pricing, licensing, or content decision

## Checks

- [ ] `python3 tests/validate_structure.py` passes
- [ ] `python3 tests/run_tests.py` passes
- [ ] No new runtime dependencies
