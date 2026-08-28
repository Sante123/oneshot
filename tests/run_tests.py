#!/usr/bin/env python3
"""Self-test for the oneshot scanner.

Runs the audit against two fixtures and asserts the expected rules fire (and do not
fire). Exits non-zero on failure so CI can gate on it.

    python3 tests/run_tests.py
"""
from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "skills" / "store-compliance" / "scripts" / "oneshot.py"
FIXTURES = REPO / "tests" / "fixtures"

# Rules that MUST be reported for the deliberately non-compliant fixture.
BAD_EXPECTED = [
    "APPLE-PLIST-NSCameraUsageDescription",
    "APPLE-PLIST-NSUserTrackingUsageDescription",
    "APPLE-PLIST-VAGUE-NSLocationWhenInUseUsageDescription",
    "APPLE-5.1-ENCRYPTION",
    "APPLE-5.1.3-MANIFEST",
    "APPLE-5.1.2-ATT",
    "APPLE-2.5.4-BGMODES",
    "APPLE-2.5.4-ORPHANENT",
    "APPLE-ENT-TASKALLOW",
    "APPLE-3.1.1-RESTORE",
    "APPLE-3.1.2-PAYWALL",
    "APPLE-2.5.5-IPV6",
    "APPLE-ATS-ARBITRARY",
    "PLAY-TARGETSDK",
    "PLAY-BILLING-VER",
    "PLAY-DEBUGGABLE",
    "PLAY-CLEARTEXT",
    "PLAY-DISCLOSURE",
    "PLAY-PERM-ACCESS_BACKGROUND_LOCATION",
    "PLAY-PERM-READ_SMS",
    "PLAY-PERM-READ_CONTACTS",
    "PLAY-PERM-QUERY_ALL_PACKAGES",
    "XPLAT-ACCOUNT-DELETE",
    "XPLAT-PRIVACY-POLICY",
    "XPLAT-UGC-CONTROLS",
    "XPLAT-AI-DISCLOSURE",
    "XPLAT-AI-MODERATION",
    "XPLAT-STAGING-URL",
    "XPLAT-PLACEHOLDER",
    "XPLAT-INTEGRITY-GATE",
    "XPLAT-SDK-INVENTORY",
    "META-LEN-NAME",
    "META-NAME-PROMO",
    "META-NAME-STUFFING",
    "META-DESC-OTHERPLATFORM",
]

# Rules that MUST NOT be reported for the compliant fixture.
GOOD_FORBIDDEN = [
    "APPLE-5.1-ENCRYPTION",
    "APPLE-5.1.3-MANIFEST",
    "APPLE-5.1.2-ATT",
    "APPLE-ENT-TASKALLOW",
    "APPLE-3.1.1-RESTORE",
    "APPLE-3.1.2-PAYWALL",
    "PLAY-TARGETSDK",
    "PLAY-BILLING-VER",
    "PLAY-DEBUGGABLE",
    "PLAY-CLEARTEXT",
    "XPLAT-ACCOUNT-DELETE",
    "XPLAT-PRIVACY-POLICY",
    "XPLAT-UGC-CONTROLS",
    "XPLAT-STAGING-URL",
    "XPLAT-PLACEHOLDER",
    "META-LEN-NAME",
    "META-NAME-PROMO",
]


def audit(path: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(CLI), "audit", "--path", str(path), "--format", "json"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode not in (0, 1):
        raise SystemExit(f"audit crashed on {path}:\n{proc.stderr}")
    return json.loads(proc.stdout)


def audit_in_skiplisted_parent() -> list:
    """Regression: a project living under a directory named build/ (or dist/, out/,
    venv/ ...) must still scan. The skip list applies to directories BELOW the scanned
    root, never to the absolute path that leads to it."""
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        for parent in ("build", "dist", "out", "venv"):
            dest = Path(tmp) / parent / "bad-app"
            shutil.copytree(FIXTURES / "bad-app", dest)
            result = audit(dest)
            rules = {f["rule_id"] for f in result["findings"]}
            for expected in ("APPLE-PLIST-NSCameraUsageDescription", "PLAY-TARGETSDK"):
                if expected not in rules:
                    problems.append(
                        f"skiplisted parent '{parent}/': {expected} was not reported "
                        f"(only {len(rules)} rules fired) — the skip list is being applied "
                        f"to the absolute path"
                    )
    return problems


def no_third_party_imports() -> list:
    """The scanner must run on a bare interpreter. Optional imports are allowed only
    when guarded by try/except and marked `# optional-dependency`."""
    stdlib = getattr(sys, "stdlib_module_names", None)
    if stdlib is None:          # Python < 3.10 has no stdlib_module_names
        return []
    problems = []
    scripts = REPO / "skills" / "store-compliance" / "scripts"
    for path in scripts.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        lines = source.splitlines()
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                if name in stdlib or name == "oneshot_lib":
                    continue
                line = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                if "optional-dependency" in line:
                    continue
                problems.append(
                    f"{path.relative_to(REPO)}:{node.lineno} imports third-party "
                    f"module '{name}'; the scanner must be standard library only"
                )
    return problems


def main() -> int:
    failures = []

    bad = audit(FIXTURES / "bad-app")
    bad_rules = {f["rule_id"] for f in bad["findings"]}
    for rule in BAD_EXPECTED:
        if rule not in bad_rules:
            failures.append(f"bad-app: expected {rule} but it was not reported")
    if bad["decision"]["verdict"] != "NO-GO":
        failures.append("bad-app: verdict should be NO-GO")

    good = audit(FIXTURES / "good-app")
    good_rules = {f["rule_id"] for f in good["findings"]}
    for rule in GOOD_FORBIDDEN:
        if rule in good_rules:
            detail = next(f for f in good["findings"] if f["rule_id"] == rule)
            failures.append(
                f"good-app: false positive {rule} at {detail['file']}:{detail['line']} "
                f"— {detail['evidence'][:120]}"
            )

    # Every finding must carry a citation and a fix.
    for label, payload in (("bad-app", bad), ("good-app", good)):
        for f in payload["findings"]:
            if not f.get("guideline"):
                failures.append(f"{label}: {f['rule_id']} has no guideline citation")
            if not f.get("fix"):
                failures.append(f"{label}: {f['rule_id']} has no fix")
            if f.get("severity") not in ("BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"):
                failures.append(f"{label}: {f['rule_id']} has a bad severity")

    failures += audit_in_skiplisted_parent()
    failures += no_third_party_imports()

    print(f"bad-app  : {len(bad['findings'])} findings, verdict {bad['decision']['verdict']}")
    print(f"good-app : {len(good['findings'])} findings, verdict {good['decision']['verdict']}")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
