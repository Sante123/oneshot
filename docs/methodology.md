# How oneshot targets a ≥98% first-submission approval rate

This document is the honest version of the claim on the README. It explains what the
target means, how the design gets there, and where it stops.

---

## 1. The claim, stated precisely

> For apps that pass the `oneshot` gate — all six conditions, not just a clean scan —
> **≥ 98% are approved on the first submission**, counting only rejections whose cause is
> observable before submission.

Two qualifiers do real work there:

- **"Pass the gate"** is not "the scanner returned zero findings". It includes the
  behavioral test matrix, the declaration checklists, and verified reviewer notes. A clean
  scan alone is roughly a third of the work.
- **"Observable before submission"** excludes rejections that are a judgment about your
  product — minimum functionality, spam/low-effort, content appropriateness, missing
  licences. Those are real, and the toolkit flags the risk, but no config change fixes them.

Anyone who tells you they can guarantee approval, without those qualifiers, is selling
something.

---

## 2. Where rejections actually come from

Rejections cluster into four kinds, and they need four different defenses:

| Kind | Examples | Defense | Coverage |
|---|---|---|---|
| **Mechanical** | Missing purpose string, no privacy manifest, targetSdk too low, unaligned `.so`, icon with alpha, name too long | Deterministic scanner | Near-total — these are decidable from the artifact |
| **Procedural** | Demo account with 2FA, backend behind an allowlist, reviewer can't find the feature, missing Console declaration | Checklists + generated reviewer notes + explicit verification steps | High — if the user works the checklist |
| **Behavioral** | Crash on launch, breaks on IPv6, breaks when a permission is denied, R8 strips reflection, integrity check blocks the review device | Test matrix + scanner detection of the *risk* | Partial — the scanner flags the risk; a human must run the test |
| **Judgment** | 4.2 minimum functionality, 4.3(b) low-effort, 1.1 content, unlicensed regulated category | Agent review with explicit confidence levels | Advisory only |

The first two are the large majority of rejections. That is why a tool like this can move
the number at all.

---

## 3. The five mechanisms

### 3.1 Cite, don't paraphrase
Every finding carries an exact guideline number. This is not decoration — it is what makes
a finding verifiable and a fix targeted. Reviewers cite numbers; a remediation that doesn't
map 1:1 to the number bounces again. It also means a wrong rule can be caught and corrected
by anyone reading the report.

### 3.2 Audit the artifact, not the intent
The merged `AndroidManifest.xml`, not `src/main/AndroidManifest.xml`. The built
`Info.plist`, not the source one. Library manifests merge in; build settings substitute
values; the thing that ships is not the thing you wrote. When the scanner can only see
source, it says so as an `INFO` finding rather than pretending.

### 3.3 Treat absence as evidence
Most compliance failures are *missing* things: no Restore Purchases, no account deletion,
no report control, no prominent disclosure. A checker that only validates what's present
finds none of them. Every one of those has an explicit "searched for X, found nothing"
check, and the evidence field names the search so the user can verify the negative.

### 3.4 Flag over-declaration as hard as under-declaration
An unused permission, an orphan entitlement, a background mode with no matching code, a
nutrition-label entry with no traffic — each is its own rejection. Developers instinctively
add rather than remove, so the tool pushes the other way.

### 3.5 Separate certainty from judgment, and never blur them
`BLOCKER`/`HIGH` findings are mechanical and near-certain. Judgment risks are reported
separately, with a confidence level, and the gate explicitly cannot clear them. Blurring
these destroys prioritization: if a maybe looks like a certainty, users learn to discount
certainties.

---

## 4. Why the gate has six conditions, not one

A scanner-only gate would be dishonest, because the scanner cannot see:

- whether the app crashes on the reviewer's device
- whether the demo account works
- whether the privacy policy URL resolves
- whether the Console declarations are filled
- whether the backend is reachable from Apple's network

So `GO` requires all six:

1. Zero `BLOCKER` findings
2. Zero unwaived `HIGH` findings
3. Every declaration box ticked
4. Behavioral evidence captured
5. Reviewer notes complete, demo account verified within 24 hours
6. Version floors met for the target date

Conditions 3–6 are human attestations. That's the point. The tool's job is to make the
attestation specific enough that lying to yourself is difficult.

---

## 5. Waivers, and why `BLOCKER`s can't be waived

Any static analyzer produces some false positives. Without an escape hatch, users disable
the tool. With too easy an escape hatch, users waive everything.

So: `HIGH` findings can be waived, but only with a written reason, an approver, and an
expiry date recorded in `.oneshot/waivers.yaml`. Silence is not a waiver. An expired waiver
is not a waiver. And `BLOCKER` findings — the ones where rejection is near-certain — cannot
be waived at all. If a `BLOCKER` is genuinely wrong, that's a bug in the rule, and the fix
is a PR, not a waiver.

---

## 6. Staleness is the main failure mode

The single most likely way this toolkit hurts someone is by being confidently out of date.
Store rules change several times a year, and some changes have hard cutover dates.

Mitigations:
- `references/deadlines.md` carries a **last-verified date** at the top.
- `catalog.FLOORS["verified_on"]` carries the same date in machine-readable form.
- `oneshot verify-deadlines` prints every floor and deadline with its status, and **exits
  non-zero when the catalog is more than 30 days old**.
- Every reference document ends with the sources it was built from.
- `CONTRIBUTING.md` requires reference and catalog to be updated together, with a citation.

If you are reading a report and the verified-on date is old, verify before you trust it.

---

## 7. What would falsify the claim

Honest work should say what would prove it wrong. This would:

- An app that passes all six gate conditions and is rejected for a **mechanical** cause the
  scanner could have detected. That's a missing rule — please open an issue with the
  rejection text.
- A `good-app`-style compliant project producing `BLOCKER` or `HIGH` findings. That's a
  false positive — the test suite exists to catch these, and the fixture should grow.

The project tracks both as bugs, not as acceptable noise.
