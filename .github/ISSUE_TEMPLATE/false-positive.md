---
name: False positive
about: The scanner reported a finding that does not apply
title: "[false positive] "
labels: false-positive
---

A false positive is a bug, not noise. If the tool cries wolf, people stop reading it — and
that is how someone ships a real blocker.

### Rule ID

### What was reported

Paste the finding from `oneshot-report.md`, including the evidence line:

```

```

### Why it does not apply

### Minimal reproduction

The smallest project shape that triggers it. If you can, mirror it into
`tests/fixtures/good-app` — a compliant fixture that provokes the finding is the ideal bug
report, because the fix then comes with a regression test for free.

### Environment

- oneshot version:
- Python version:
- Stack: native iOS / native Android / React Native / Expo / Flutter / Unity / other
- Did you audit source only, or a built artifact?
