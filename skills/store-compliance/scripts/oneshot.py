#!/usr/bin/env python3
"""oneshot — get your mobile app approved on the first submission.

Commands
--------
  detect             Identify the project stack and the files that matter
  audit              Run every deterministic App Store / Play compliance check
  fix                Apply the safe subset of fixes (dry-run unless --apply)
  gate               Exit non-zero if the project is not submission-ready
  notes              Generate Notes for Review / Play App access instructions
  explain            Print what a guideline number means and how to satisfy it
  verify-deadlines   Re-check the version floors in references/deadlines.md

Standard library only. Python 3.9+.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from oneshot_lib import catalog, detect, fixer, report, util   # noqa: E402
from oneshot_lib.checks import android as android_checks       # noqa: E402
from oneshot_lib.checks import crosscut as crosscut_checks     # noqa: E402
from oneshot_lib.checks import ios as ios_checks               # noqa: E402
from oneshot_lib.checks import metadata as metadata_checks     # noqa: E402
from oneshot_lib.model import APPLE, BOTH, PLAY, FindingList   # noqa: E402

SKILL_ROOT = HERE.parent


# --------------------------------------------------------------------------
def run_audit(root: Path, store: str = "both") -> tuple:
    proj = detect.detect(root)
    findings = FindingList()
    if store in ("both", "apple"):
        findings.extend_from(ios_checks.check(proj))
    if store in ("both", "play", "google", "google_play"):
        findings.extend_from(android_checks.check(proj))
    findings.extend_from(crosscut_checks.check(proj))
    findings.extend_from(metadata_checks.check(proj))

    if store == "apple":
        findings = FindingList(f for f in findings if f.store in (APPLE, BOTH))
    elif store in ("play", "google", "google_play"):
        findings = FindingList(f for f in findings if f.store in (PLAY, BOTH))

    findings = findings.dedupe().ranked()
    meta = {
        "root": str(proj.root),
        "stacks": proj.stacks,
        "timestamp": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "rules_verified_on": catalog.FLOORS["verified_on"],
        "store": store,
        "detected": proj.summary(),
    }
    return proj, findings, meta


# --------------------------------------------------------------------------
def cmd_detect(args) -> int:
    proj = detect.detect(Path(args.path))
    print(json.dumps(proj.summary(), indent=2))
    return 0


def cmd_audit(args) -> int:
    root = Path(args.path).resolve()
    proj, findings, meta = run_audit(root, args.store)
    waivers = report.load_waivers(root)
    decision = report.gate(findings, waivers, args.min_severity)

    if args.format == "json":
        payload = json.loads(findings.to_json(meta))
        payload["decision"] = {
            "verdict": decision["verdict"],
            "reason": decision["reason"],
            "blocking": [f.rule_id for f in decision["blocking"]],
            "waived": [f.rule_id for f in decision["waived"]],
        }
        text = json.dumps(payload, indent=2)
    elif args.format == "text":
        text = report.render_text(findings, decision)
    else:
        text = report.render_markdown(findings, meta, decision)

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
        counts = findings.counts()
        print("  ".join(f"{k}={v}" for k, v in counts.items() if v))
        print(f"Verdict: {decision['verdict']} — {decision['reason']}")
    else:
        print(text)

    if args.fail_on_findings and decision["verdict"] == "NO-GO":
        return 1
    return 0


def cmd_fix(args) -> int:
    root = Path(args.path).resolve()
    proj, findings, _ = run_audit(root, args.store)
    if args.report and Path(args.report).exists():
        # Prefer the rule set from a saved report so fix matches what the user reviewed.
        saved = json.loads(Path(args.report).read_text())
        wanted = {f["rule_id"] for f in saved.get("findings", [])}
        findings = FindingList(f for f in findings if f.rule_id in wanted)

    changes = fixer.plan(proj, findings)
    if not changes:
        print("Nothing to auto-fix. Remaining findings need a human decision — "
              "see the report's Fix field for each.")
        return 0

    for c in changes:
        print(f"--- {util.rel(c.path, root)}  ({c.note})")
        print(c.diff(root))

    if args.apply:
        n = fixer.apply(changes)
        print(f"\nApplied {n} file change(s). Re-run `audit` to confirm.")
    else:
        print("\nDry run. Re-run with --apply to write these changes.")
    return 0


def cmd_gate(args) -> int:
    root = Path(args.path).resolve()
    if args.report and Path(args.report).exists():
        saved = json.loads(Path(args.report).read_text())
        decision = saved.get("decision") or {}
        verdict = decision.get("verdict")
        reason = decision.get("reason", "")
        if not verdict:
            counts = saved.get("counts", {})
            verdict = "NO-GO" if counts.get("BLOCKER") or counts.get("HIGH") else "GO"
            reason = f"derived from counts: {counts}"
    else:
        _, findings, _ = run_audit(root, args.store)
        d = report.gate(findings, report.load_waivers(root), args.min_severity)
        verdict, reason = d["verdict"], d["reason"]

    print(f"{verdict}: {reason}")
    if verdict == "GO":
        print("\nThe mechanical checks pass. Still required before submitting:")
        print("  1. The behavioral test matrix (references/submission-playbook.md §4)")
        print("  2. Every box in assets/checklist-apple.md / checklist-play.md")
        print("  3. Reviewer notes with a demo account verified in the last 24 hours")
        return 0
    return 1


def cmd_notes(args) -> int:
    root = Path(args.path).resolve()
    proj = detect.detect(root)
    template = SKILL_ROOT / "assets" / "review-notes-template.md"
    text = util.read_text(template)
    if not text:
        print("review-notes-template.md not found", file=sys.stderr)
        return 2

    hints = []
    def has(key):
        return util.any_match(root, catalog.SIGNALS[key])

    if has("accounts"):
        hints.append("Login detected — a working demo account is MANDATORY (Apple 2.1) and "
                     "App access instructions are MANDATORY (Play).")
    if has("iap"):
        hints.append("In-app purchases detected — document the sandbox flow and where Restore "
                     "Purchases lives.")
    if has("ugc"):
        hints.append("User-generated content detected — document filtering, reporting, blocking, "
                     "contact info, and your 24-hour takedown commitment (Apple 1.2 / Play VI).")
    if util.any_match(root, catalog.AI_ENDPOINT_PATTERN):
        hints.append("Third-party AI detected — document the provider, exactly what is sent, and "
                     "where consent is captured (Apple 5.1.2(i)).")
    if has("location_bg"):
        hints.append("Background location detected — Play requires a demo video showing the "
                     "prominent disclosure and the feature in use.")
    if has("integrity_gate"):
        hints.append("Integrity/root/emulator checks detected — document the review bypass, or "
                     "the reviewer's device will be blocked.")

    header = ["<!-- generated by oneshot notes — fill every [bracket] before submitting -->", ""]
    if hints:
        header.append("## Detected in this project — do not skip these\n")
        header += [f"- {h}" for h in hints]
        header.append("")
    output = "\n".join(header) + text

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(output)
    return 0


GUIDELINE_FILES = [
    ("apple", "references/apple-guidelines.md"),
    ("apple", "references/apple-technical.md"),
    ("play", "references/google-play-policies.md"),
    ("play", "references/google-play-technical.md"),
    ("both", "references/privacy-and-data.md"),
    ("both", "references/monetization.md"),
    ("both", "references/metadata-and-assets.md"),
    ("both", "references/content-ugc-ai-kids.md"),
]


def cmd_explain(args) -> int:
    needle = args.guideline.strip()
    found = False
    for _, relpath in GUIDELINE_FILES:
        path = SKILL_ROOT / relpath
        text = util.read_text(path)
        if not text:
            continue
        lines = text.splitlines()
        # Anchor so "4.3" doesn't match "1.4.3" and "2.1" doesn't match "12.1".
        rx = re.compile(r"(?<![\d.])" + re.escape(needle) + r"(?![\d])", re.IGNORECASE)
        matches = [i for i, line in enumerate(lines) if rx.search(line)]
        if not matches:
            continue
        # Prefer prose (headings, rule bullets) over index-table rows, which are terse.
        prose = [i for i in matches if not lines[i].lstrip().startswith("|")]
        headings = [i for i in prose if lines[i].lstrip().startswith(("#", "**", "- **"))]
        i = (headings or prose or matches)[0]
        start = max(0, i - 2)
        end = min(len(lines), i + 20)
        print(f"\n=== {relpath}:{i+1} ===")
        print("\n".join(lines[start:end]))
        found = True
    if not found:
        print(f"No entry for '{needle}'. Try a guideline number like 5.1.1, 3.1.2, 4.3, "
              f"or a policy name like 'Data safety'.")
        return 1
    return 0


DEADLINE_SOURCES = {
    "Apple upcoming requirements": "https://developer.apple.com/news/upcoming-requirements/",
    "Play target API level": "https://support.google.com/googleplay/android-developer/answer/11926878",
    "Play Billing deprecation": "https://developer.android.com/google/play/billing/deprecation-faq",
    "Android 16 KB page sizes": "https://developer.android.com/guide/practices/page-sizes",
    "Play Developer Program Policy": "https://support.google.com/googleplay/android-developer/answer/16944162",
    "Android developer verification": "https://support.google.com/android-developer-console/answer/16561738",
}


def cmd_verify_deadlines(args) -> int:
    verified = catalog.FLOORS["verified_on"]
    age = (_dt.date.today() - _dt.date.fromisoformat(verified)).days
    print(f"Rule catalog last verified: {verified} ({age} days ago)\n")
    print("Current floors:")
    for key, value in catalog.FLOORS.items():
        if key in ("verified_on", "deadlines"):
            continue
        print(f"  {key:32} {value}")
    print("\nDeadlines:")
    for key, value in catalog.FLOORS["deadlines"].items():
        today = _dt.date.today().isoformat()
        status = "PASSED" if value < today else "upcoming"
        print(f"  {key:32} {value}  [{status}]")
    print("\nRe-check these sources by hand (or have the agent fetch them):")
    for name, url in DEADLINE_SOURCES.items():
        print(f"  {name:32} {url}")
    if age > 30:
        print(f"\n!! The catalog is {age} days old. Verify before trusting any floor above.")
        return 1
    return 0


# --------------------------------------------------------------------------
def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="oneshot",
        description="Get your app approved on the first submission.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp, store_default="both"):
        sp.add_argument("--path", default=".", help="project root (default: .)")
        sp.add_argument("--store", default=store_default,
                        choices=["both", "apple", "play"], help="which store to check")

    sp = sub.add_parser("detect", help="identify the project stack")
    sp.add_argument("--path", default=".")
    sp.set_defaults(func=cmd_detect)

    sp = sub.add_parser("audit", help="run every deterministic compliance check")
    add_common(sp)
    sp.add_argument("--format", default="markdown", choices=["markdown", "json", "text"])
    sp.add_argument("--out", help="write the report to this file")
    sp.add_argument("--min-severity", default="HIGH",
                    choices=["BLOCKER", "HIGH", "MEDIUM", "LOW"],
                    help="severity at or above which a finding blocks the gate")
    sp.add_argument("--fail-on-findings", action="store_true",
                    help="exit 1 when the verdict is NO-GO (for CI)")
    sp.set_defaults(func=cmd_audit)

    sp = sub.add_parser("fix", help="apply the safe subset of fixes")
    add_common(sp)
    sp.add_argument("--report", help="only fix rules present in this JSON report")
    sp.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    sp.set_defaults(func=cmd_fix)

    sp = sub.add_parser("gate", help="GO / NO-GO decision; exits 1 on NO-GO")
    add_common(sp)
    sp.add_argument("--report", help="use a saved JSON report instead of re-scanning")
    sp.add_argument("--min-severity", default="HIGH",
                    choices=["BLOCKER", "HIGH", "MEDIUM", "LOW"])
    sp.set_defaults(func=cmd_gate)

    sp = sub.add_parser("notes", help="generate reviewer notes")
    sp.add_argument("--path", default=".")
    sp.add_argument("--out")
    sp.set_defaults(func=cmd_notes)

    sp = sub.add_parser("explain", help="explain a guideline number")
    sp.add_argument("--guideline", required=True)
    sp.set_defaults(func=cmd_explain)

    sp = sub.add_parser("verify-deadlines", help="check the rule catalog's freshness")
    sp.set_defaults(func=cmd_verify_deadlines)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
