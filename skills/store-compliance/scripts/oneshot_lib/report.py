"""Report rendering and the submission gate."""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

from . import util
from .model import APPLE, BOTH, PLAY, SEVERITY_RANK, FindingList

BADGE = {
    "BLOCKER": "🛑", "HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡", "INFO": "ℹ️",
}


def load_waivers(root: Path) -> dict:
    path = root / ".oneshot" / "waivers.yaml"
    if not path.exists():
        return {}
    items = util.parse_simple_yaml_list(util.read_text(path))
    today = _dt.date.today().isoformat()
    out = {}
    for item in items:
        rule = item.get("rule_id")
        if not rule:
            continue
        expires = str(item.get("expires") or "")
        if expires and expires < today:
            continue
        if not item.get("reason"):
            continue
        out[rule] = item
    return out


def gate(findings: FindingList, waivers: dict, min_severity: str = "HIGH") -> dict:
    """Return the GO/NO-GO decision. BLOCKERs can never be waived."""
    limit = SEVERITY_RANK[min_severity]
    blocking, waived = [], []
    for f in findings:
        if SEVERITY_RANK[f.severity] > limit:
            continue
        if f.severity == "BLOCKER":
            blocking.append(f)
            continue
        if f.rule_id in waivers:
            waived.append(f)
            continue
        blocking.append(f)

    verdict = "GO" if not blocking else "NO-GO"
    if verdict == "GO":
        reason = ("No blocking findings at or above %s. Behavioral verification and the "
                  "declaration checklists still have to be completed by hand." % min_severity)
    else:
        top = blocking[0]
        reason = (f"{len(blocking)} blocking finding(s). Most severe: "
                  f"[{top.severity}] {top.title} ({top.guideline}).")
    return {
        "verdict": verdict,
        "reason": reason,
        "blocking": blocking,
        "waived": waived,
        "min_severity": min_severity,
    }


def render_markdown(findings: FindingList, meta: dict, decision: dict | None = None) -> str:
    findings = findings.ranked()
    counts = findings.counts()
    lines = []
    ap = len(findings.by_store(APPLE))
    gp = len(findings.by_store(PLAY))

    lines.append("# oneshot — App Store & Play submission audit\n")
    lines.append(f"**Project:** `{meta.get('root','')}`  ")
    lines.append(f"**Stacks:** {', '.join(meta.get('stacks', [])) or 'unknown'}  ")
    lines.append(f"**Scanned:** {meta.get('timestamp','')}  ")
    lines.append(f"**Rule catalog verified:** {meta.get('rules_verified_on','')}\n")

    if decision:
        mark = "✅ **GO**" if decision["verdict"] == "GO" else "⛔ **NO-GO**"
        lines.append(f"## Verdict: {mark}\n")
        lines.append(f"{decision['reason']}\n")
        if decision["verdict"] == "GO":
            lines.append(
                "> A GO from the scanner means the *mechanical* checks pass. You still owe the "
                "behavioral test matrix (`references/submission-playbook.md` §4), the "
                "declaration checklists, and reviewer notes with a demo account verified in the "
                "last 24 hours.\n"
            )

    lines.append("## Summary\n")
    lines.append("| Severity | Count |")
    lines.append("|---|---|")
    for sev in ("BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"):
        if counts[sev]:
            lines.append(f"| {BADGE[sev]} {sev} | {counts[sev]} |")
    lines.append(f"| — Apple-relevant | {ap} |")
    lines.append(f"| — Play-relevant | {gp} |")
    lines.append("")

    for sev in ("BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"):
        group = [f for f in findings if f.severity == sev]
        if not group:
            continue
        lines.append(f"## {BADGE[sev]} {sev} ({len(group)})\n")
        for f in group:
            store = {APPLE: "Apple", PLAY: "Google Play", BOTH: "Apple + Google Play"}[f.store]
            lines.append(f"### `{f.rule_id}` — {f.title}\n")
            lines.append(f"- **Store:** {store}")
            lines.append(f"- **Guideline:** {f.guideline}")
            lines.append(f"- **Location:** `{f.location}`")
            if f.confidence != "high":
                lines.append(f"- **Confidence:** {f.confidence}")
            if f.evidence:
                ev = f.evidence.strip()
                if "\n" in ev:
                    lines.append("- **Evidence:**\n")
                    lines.append("```\n" + ev + "\n```")
                else:
                    lines.append(f"- **Evidence:** `{ev}`")
            if f.impact:
                lines.append(f"- **Why it matters:** {f.impact}")
            lines.append(f"- **Fix:** {f.fix}")
            if f.suggested_value:
                lines.append(f"- **Suggested value:** `{f.suggested_value}`")
            if f.auto_fixable:
                lines.append("- **Auto-fixable:** yes — `oneshot.py fix --apply`")
            lines.append("")

    if decision and decision.get("waived"):
        lines.append("## Waived\n")
        for f in decision["waived"]:
            lines.append(f"- `{f.rule_id}` — {f.title}")
        lines.append("")

    lines.append("## What this scan could not check\n")
    lines.append(
        "- Runtime behavior: crashes, IPv6-only networking, permission-denied paths, "
        "purchase and restore flows, account deletion actually deleting.\n"
        "- Content judgment: guideline 1.1 appropriateness, 4.2 minimum functionality, "
        "4.3(b) low-effort/spam. Run the `content-policy-auditor` agent.\n"
        "- Store Console state: declarations, age rating, Data safety, demo account, trader "
        "status. Work the checklists in `assets/`.\n"
        "- Live URLs: privacy policy, terms, AASA file, account-deletion page.\n"
    )
    return "\n".join(lines)


def render_text(findings: FindingList, decision: dict | None = None) -> str:
    findings = findings.ranked()
    out = []
    if decision:
        out.append(f"VERDICT: {decision['verdict']} — {decision['reason']}\n")
    for f in findings:
        out.append(f"[{f.severity:7}] {f.rule_id:28} {f.location}")
        out.append(f"           {f.title}")
        out.append(f"           {f.guideline}")
        out.append(f"           fix: {f.fix[:160]}")
        out.append("")
    counts = findings.counts()
    out.append("  ".join(f"{k}={v}" for k, v in counts.items() if v))
    return "\n".join(out)
