"""Safe auto-fixes. Every fix is idempotent and shows a diff before applying."""
from __future__ import annotations

import difflib
import plistlib
import re
from pathlib import Path

from . import catalog, util
from .model import Finding

# Rules the fixer will actually touch. Anything not listed here is reported only,
# even if the finding is marked auto_fixable (agents can still apply those by hand).
FIXABLE = {
    "APPLE-5.1-ENCRYPTION",
    "APPLE-2.5.4-BGMODES",
    "APPLE-ENT-TASKALLOW",
    "APPLE-MANIFEST-BADKEY",
    "APPLE-MANIFEST-MISSINGCAT",
    "APPLE-MANIFEST-NOREASON",
    "APPLE-MANIFEST-BADREASON",
    "PLAY-DEBUGGABLE",
    "PLAY-CLEARTEXT",
    "PLAY-BACKUP",
    "PLAY-TARGETSDK",
    "PLAY-BILLING-VER",
    "PLAY-PERM-ADID",
}
# Deliberately NOT auto-fixed: APPLE-2.5.4-ORPHANENT (removing an entitlement also
# requires changing the App ID capabilities and provisioning profile), and META-LEN-* (truncating a name or description is a
# branding decision, and a machine trim reads as broken copy). The finding carries a
# word-boundary-safe suggested_value for a human to accept or rewrite.
# Purpose-string additions are handled generically (rule ids are dynamic).
PURPOSE_PREFIX = "APPLE-PLIST-"


class Change:
    def __init__(self, path: Path, before: str, after: str, note: str):
        self.path, self.before, self.after, self.note = path, before, after, note

    def diff(self, root: Path) -> str:
        return "".join(difflib.unified_diff(
            self.before.splitlines(keepends=True),
            self.after.splitlines(keepends=True),
            fromfile=f"a/{util.rel(self.path, root)}",
            tofile=f"b/{util.rel(self.path, root)}",
        )) or f"(binary or no textual change) {util.rel(self.path, root)}\n"


def plan(proj, findings) -> list:
    """Return a list of Change objects for the findings we can safely fix."""
    root = proj.root
    changes: list[Change] = []
    buffers: dict[Path, str] = {}

    def buf(path: Path) -> str:
        if path not in buffers:
            buffers[path] = util.read_text(path)
        return buffers[path]

    def put(path: Path, text: str, note: str):
        buffers[path] = text
        changes.append(Change(path, util.read_text(path), text, note))

    for f in findings:
        fixable = f.rule_id in FIXABLE or f.rule_id.startswith(PURPOSE_PREFIX)
        if not (f.auto_fixable and fixable):
            continue

        if f.rule_id.startswith(PURPOSE_PREFIX) and not f.rule_id.startswith(PURPOSE_PREFIX + "VAGUE"):
            key = f.rule_id[len(PURPOSE_PREFIX):]
            for path in _app_plists(proj):
                text = buf(path)
                if f"<key>{key}</key>" in text:
                    continue
                value = f.suggested_value or f"[Describe why the app needs {key}]"
                new = _insert_plist_string(text, key, value)
                if new != text:
                    put(path, new, f"add {key}")
                break

        elif f.rule_id == "APPLE-5.1-ENCRYPTION":
            for path in _app_plists(proj):
                text = buf(path)
                if "ITSAppUsesNonExemptEncryption" in text:
                    continue
                new = _insert_plist_bool(text, "ITSAppUsesNonExemptEncryption", False)
                if new != text:
                    put(path, new, "add ITSAppUsesNonExemptEncryption=false")
                break

        elif f.rule_id in ("PLAY-DEBUGGABLE", "PLAY-CLEARTEXT", "PLAY-BACKUP"):
            attr = {"PLAY-DEBUGGABLE": "debuggable",
                    "PLAY-CLEARTEXT": "usesCleartextTraffic",
                    "PLAY-BACKUP": "allowBackup"}[f.rule_id]
            path = root / f.file
            if not path.exists():
                continue
            text = buf(path)
            if attr == "debuggable":
                new = re.sub(r'\s*android:debuggable="true"', "", text)
            else:
                if f'android:{attr}=' in text:
                    new = re.sub(rf'android:{attr}="true"', f'android:{attr}="false"', text)
                else:
                    new = re.sub(r"(<application\b)", rf'\1\n        android:{attr}="false"',
                                 text, count=1)
            if new != text:
                put(path, new, f"set android:{attr} safely")

        elif f.rule_id == "PLAY-TARGETSDK":
            path = root / f.file
            if not path.exists():
                continue
            text = buf(path)
            target = catalog.FLOORS["play_target_sdk"]
            new = re.sub(r"(targetSdk(?:Version)?\s*[= ]\s*['\"]?)(\d{2})",
                         rf"\g<1>{target}", text)
            new = re.sub(r"(compileSdk(?:Version)?\s*[= ]\s*['\"]?)(\d{2})",
                         rf"\g<1>{target}", new)
            if new != text:
                put(path, new, f"targetSdk/compileSdk -> {target}")

        elif f.rule_id == "PLAY-BILLING-VER":
            path = root / f.file
            if not path.exists():
                continue
            text = buf(path)
            major = catalog.FLOORS["play_billing_major"]
            new = re.sub(r"(billing(?:-ktx)?[:'\"]{1,2})\d+\.\d+\.\d+",
                         rf"\g<1>{major}.0.0", text)
            if new != text:
                put(path, new, f"Play Billing -> {major}.0.0")

        elif f.rule_id == "PLAY-PERM-ADID":
            path = root / f.file
            if not path.exists():
                continue
            text = buf(path)
            perm = '<uses-permission android:name="com.google.android.gms.permission.AD_ID" />'
            if perm in text:
                continue
            new = re.sub(r"(<manifest\b[^>]*>)", rf"\1\n    {perm}", text, count=1)
            if new != text:
                put(path, new, "declare AD_ID permission")

        elif f.rule_id == "APPLE-2.5.4-BGMODES":
            path = root / f.file
            if not path.exists():
                continue
            mode = re.search(r"declares '([^']+)'", f.title)
            if not mode:
                continue
            text = buf(path)
            new = re.sub(rf"\s*<string>{re.escape(mode.group(1))}</string>", "", text, count=1)
            if new != text:
                put(path, new, f"remove unused background mode '{mode.group(1)}'")

        elif f.rule_id == "APPLE-ENT-TASKALLOW":
            path = root / f.file
            if not path.exists():
                continue
            text = buf(path)
            new = re.sub(r"(<key>get-task-allow</key>\s*)<true\s*/>", r"\1<false/>", text)
            if new != text:
                put(path, new, "get-task-allow -> false")

        elif f.rule_id in ("APPLE-MANIFEST-MISSINGCAT", "APPLE-MANIFEST-NOREASON",
                           "APPLE-MANIFEST-BADREASON", "APPLE-MANIFEST-BADKEY"):
            for man in proj.ios_privacy_manifests:
                new = _fix_privacy_manifest(man, proj)
                old = util.read_text(man)
                if new and new != old:
                    put(man, new, "normalize PrivacyInfo.xcprivacy")
                break

    # collapse multiple changes to the same file into one
    merged: dict[Path, Change] = {}
    for c in changes:
        if c.path in merged:
            merged[c.path].after = buffers[c.path]
            merged[c.path].note += "; " + c.note
        else:
            c.after = buffers[c.path]
            merged[c.path] = c
    return list(merged.values())


def apply(changes: list) -> int:
    n = 0
    for c in changes:
        try:
            c.path.write_text(c.after, encoding="utf-8")
            n += 1
        except OSError:
            continue
    return n


# --------------------------------------------------------------------------
def _app_plists(proj):
    out = [p for p in proj.ios_info_plists if "Tests" not in str(p)]
    return sorted(out, key=lambda p: len(p.parts))


def _insert_plist_string(text: str, key: str, value: str) -> str:
    esc = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    entry = f"\t<key>{key}</key>\n\t<string>{esc}</string>\n"
    idx = text.rfind("</dict>")
    if idx == -1:
        return text
    return text[:idx] + entry + text[idx:]


def _insert_plist_bool(text: str, key: str, value: bool) -> str:
    entry = f"\t<key>{key}</key>\n\t<{'true' if value else 'false'}/>\n"
    idx = text.rfind("</dict>")
    if idx == -1:
        return text
    return text[:idx] + entry + text[idx:]


def _fix_privacy_manifest(path: Path, proj) -> str | None:
    """Rewrite PrivacyInfo.xcprivacy with only legal keys and valid reason codes."""
    data = util.read_plist(path)
    legal = {"NSPrivacyTracking", "NSPrivacyTrackingDomains",
             "NSPrivacyCollectedDataTypes", "NSPrivacyAccessedAPITypes"}
    out = {k: v for k, v in data.items() if k in legal}
    out.setdefault("NSPrivacyTracking", False)
    out.setdefault("NSPrivacyTrackingDomains", [])
    out.setdefault("NSPrivacyCollectedDataTypes", [])

    declared = {}
    for entry in out.get("NSPrivacyAccessedAPITypes") or []:
        if isinstance(entry, dict) and entry.get("NSPrivacyAccessedAPIType"):
            declared[entry["NSPrivacyAccessedAPIType"]] = list(
                entry.get("NSPrivacyAccessedAPITypeReasons") or [])

    for category, spec in catalog.REQUIRED_REASON_APIS.items():
        used = util.any_match(proj.root, spec["pattern"],
                              {".swift", ".m", ".mm", ".h", ".dart", ".kt"})
        if used and category not in declared:
            declared[category] = [spec["default"]]
        if category in declared:
            valid = [r for r in declared[category] if r in spec["reasons"]]
            declared[category] = valid or [spec["default"]]

    out["NSPrivacyAccessedAPITypes"] = [
        {"NSPrivacyAccessedAPIType": cat, "NSPrivacyAccessedAPITypeReasons": reasons}
        for cat, reasons in sorted(declared.items())
    ]
    try:
        return plistlib.dumps(out).decode("utf-8")
    except Exception:
        return None
