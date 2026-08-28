# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Because this project's value is the accuracy of its rules, **every release states the date
the rule catalog was last verified against Apple's and Google's live documentation.**

---

## [1.0.0] — 2026-08-19

Initial release.

**Rule catalog verified: 2026-08-19.** Run `oneshot verify-deadlines` before relying on
any version floor; it exits non-zero once the catalog is more than 30 days old.

### Knowledge base

- Complete Apple App Review Guidelines rejection index, sections 1–5, including the
  June 2026 tightening of 4.3(b) against low-effort and AI-generated apps, the
  November 2025 third-party-AI data-sharing clause in 5.1.2(i), and the Live Activities
  addition to 4.5.3.
- Complete Google Play Developer Program Policy index at the July 15, 2026 version,
  incorporating the April and July 2026 policy announcements — contacts minimum scope,
  the removal of geofencing as an approved foreground-service use case, the `READ_CALL_LOG`
  account-verification ban, and mandatory Play Console app registration.
- Apple technical surface: the ITMS error table, Info.plist keys and purpose strings,
  privacy manifests with the full Required Reason API reason-code tables, entitlement
  orphan rules, binary hygiene, the Xcode 26 / iOS 26 SDK floor, and asset specifications.
- Play technical surface: target API levels through 2027, the 16 KB page-size requirement,
  64-bit and AAB rules, merged-manifest hygiene, Gradle and signing, the pre-launch report
  and Android vitals thresholds, plus per-stack notes for React Native, Expo, Flutter and
  Unity.
- Cross-cutting documents on the four-way privacy reconciliation, monetization and
  paywalls, metadata and assets, UGC / AI / kids / regulated categories, the submission
  playbook, and hard deadlines.

### Tooling

- `oneshot.py` — a CLI with `detect`, `audit`, `fix`, `gate`, `notes`, `explain` and
  `verify-deadlines`. Standard library only, Python 3.9+, **no third-party dependencies**.
- Deterministic checks across iOS, Android, cross-platform concerns and store metadata.
  Every finding carries a rule ID, a severity, an exact guideline citation, `file:line`
  evidence, the review consequence, and a concrete fix.
- An idempotent auto-fixer with a dry-run unified diff, restricted by an explicit
  allow-list to changes that are unambiguous and reversible.
- A six-condition submission gate with a waiver system. `BLOCKER` findings can never be
  waived; waivers require a written reason and an expiry date.

### Agents

- Eight specialist reviewers sharing one finding schema: iOS, Android, privacy/data,
  monetization, metadata/assets, content policy, build config, and a gatekeeper that merges
  the streams and decides GO/NO-GO.

### Distribution

- Installable four ways: as a Claude marketplace, as a local plugin, via `install.py`
  directly into `~/.claude`, or as a standalone Python CLI with no Claude at all.
- `install.py` (with `install.sh` and `install.ps1` wrappers) supports `--check`,
  `--uninstall`, `--project`, `--dest` and `--force`, and records an install manifest so
  uninstall removes exactly what it added.
- `tests/validate_structure.py` verifies the repository is installable all four ways —
  catching nested contents, malformed manifests, unresolvable manifest paths, missing
  `__init__.py`, and skill or agent frontmatter whose `name` does not match its directory
  or filename — and prints the exact fix for each.
- `tests/run_tests.py` audits a deliberately non-compliant fixture and a compliant one,
  asserting both the expected detections and the absence of false positives, and that every
  finding carries a citation and a fix. It additionally guards two invariants: the scanner
  works when the project lives under a directory whose name is on the internal skip list
  (`build/`, `dist/`, `out/`, `venv/` — the skip list applies below the scanned root, never
  to the absolute path leading to it), and no module imports a third-party package unless
  the import is guarded and explicitly marked optional.
- CI runs both suites plus an end-to-end installer round trip on Python 3.9, 3.11 and 3.13.

### Documentation

- `docs/INSTALL.md` — four install routes and troubleshooting.
- `docs/ARCHITECTURE.md` — the three layers, the finding schema, why severity is
  load-bearing, and what the auto-fixer deliberately refuses to do.
- `docs/PUBLISHING.md` — the pre-push checklist, recovering a nested repository, and
  cutting a release.
- `docs/methodology.md` — what the ≥98% target means, the five mechanisms behind it, and
  what would falsify it.

### Known limitations

- The toolkit cannot clear **judgment** rejections: Apple 4.2 minimum functionality,
  4.3(b) spam and low-effort, 1.1 content appropriateness, or a regulated category where
  the developer does not hold the licence. It flags the risk with a confidence level and
  says plainly that a config change will not fix it.
- A source-only scan cannot verify the merged Android manifest, native library alignment,
  ABIs, or the build SDK version. These are reported as `INFO` coverage gaps, never as
  passes.
- Runtime behavior, live URLs, and App Store Connect / Play Console state are outside the
  scanner's reach by construction. Every report ends with an explicit "what this scan could
  not check" section.

[1.0.0]: https://github.com/Sante123/oneshot/releases/tag/v1.0.0
