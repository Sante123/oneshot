"""Google Play / Android deterministic checks."""
from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from .. import catalog, util
from ..model import Finding, FindingList, PLAY

ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def check(proj) -> FindingList:
    out = FindingList()
    if not proj.has_android:
        return out
    manifest_path, merged = _best_manifest(proj)
    out.extend_from(_manifest_checks(proj, manifest_path, merged))
    out.extend_from(_permission_checks(proj, manifest_path, merged))
    out.extend_from(_gradle_checks(proj))
    out.extend_from(_native_checks(proj))
    return out


def _best_manifest(proj):
    """Prefer a merged manifest; fall back to the app module's source manifest."""
    if proj.android_merged_manifests:
        return proj.android_merged_manifests[0], True
    candidates = [m for m in proj.android_manifests if "src/main" in str(m).replace("\\", "/")]
    candidates = candidates or proj.android_manifests
    if not candidates:
        return None, False
    app = [m for m in candidates if "/app/" in str(m).replace("\\", "/")]
    return (app or candidates)[0], False


def _parse_manifest(path: Path):
    try:
        return ElementTree.parse(path).getroot()
    except Exception:
        return None


def _manifest_permissions(root_el, text: str) -> set:
    perms = set()
    if root_el is not None:
        for el in root_el.iter("uses-permission"):
            name = el.get(ANDROID_NS + "name")
            if name:
                perms.add(name)
        for el in root_el.iter("uses-permission-sdk-23"):
            name = el.get(ANDROID_NS + "name")
            if name:
                perms.add(name)
    perms.update(re.findall(r'android:name="(android\.permission\.[A-Z_0-9]+)"', text))
    return perms


def _manifest_checks(proj, manifest_path, merged):
    if not manifest_path:
        return
    root = proj.root
    rel = util.rel(manifest_path, root)
    text = util.read_text(manifest_path)
    el = _parse_manifest(manifest_path)

    if not merged:
        yield Finding(
            rule_id="PLAY-MANIFEST-UNMERGED",
            severity="INFO",
            store=PLAY,
            guideline="Audit coverage",
            title="Audited the source manifest, not the merged manifest",
            file=rel,
            evidence="No merged manifest found under build/intermediates/",
            impact="Library manifests merge in additional permissions and components that this "
                   "audit cannot see. Play reviews the merged result.",
            fix="Run `./gradlew :app:processReleaseManifest` (or "
                "`bundletool dump manifest --bundle=app-release.aab`) and re-run the audit.",
            auto_fixable=False,
        )

    app_el = el.find("application") if el is not None else None

    def attr(name):
        if app_el is not None:
            return app_el.get(ANDROID_NS + name)
        m = re.search(rf'android:{name}="([^"]+)"', text)
        return m.group(1) if m else None

    if str(attr("debuggable")).lower() == "true":
        yield Finding(
            rule_id="PLAY-DEBUGGABLE",
            severity="BLOCKER",
            store=PLAY,
            guideline="Play Device and Network Abuse / release requirements",
            title='android:debuggable="true" in the manifest',
            file=rel,
            line=util.line_of(manifest_path, "debuggable"),
            evidence='android:debuggable="true"',
            impact="Play rejects debuggable release builds; it also exposes app internals.",
            fix="Remove android:debuggable from the manifest and let the release build type "
                "control it.",
            auto_fixable=True,
        )

    if str(attr("usesCleartextTraffic")).lower() == "true":
        yield Finding(
            rule_id="PLAY-CLEARTEXT",
            severity="HIGH",
            store=PLAY,
            guideline="Play Device and Network Abuse / security scan",
            title='android:usesCleartextTraffic="true"',
            file=rel,
            line=util.line_of(manifest_path, "usesCleartextTraffic"),
            evidence='android:usesCleartextTraffic="true"',
            impact="Triggers a Play security warning and contradicts a Data safety declaration "
                   "of 'encrypted in transit'.",
            fix="Set it to false and add a Network Security Config with per-domain exceptions "
                "only for hosts that genuinely cannot serve TLS.",
            auto_fixable=True,
        )

    if str(attr("allowBackup")).lower() == "true" or attr("allowBackup") is None:
        sensitive = util.any_match(root, catalog.SIGNALS["accounts"]) or \
            util.any_match(root, r"EncryptedSharedPreferences|Keystore|token|password")
        if sensitive:
            yield Finding(
                rule_id="PLAY-BACKUP",
                severity="MEDIUM",
                store=PLAY,
                guideline="Play XI User Data / Data security",
                title="android:allowBackup is enabled while the app stores credentials",
                file=rel,
                evidence=f'android:allowBackup="{attr("allowBackup")}" (default is true)',
                impact="Auth tokens and user data can be extracted from cloud/adb backups.",
                fix='Set android:allowBackup="false", or configure dataExtractionRules / '
                    "fullBackupContent to exclude credential storage.",
                auto_fixable=True,
            )

    # Foreground service types
    if el is not None:
        for svc in el.iter("service"):
            name = svc.get(ANDROID_NS + "name") or "?"
            fst = svc.get(ANDROID_NS + "foregroundServiceType")
            if fst is None:
                continue
            if "location" in fst and util.any_match(root, r"[Gg]eofenc"):
                yield Finding(
                    rule_id="PLAY-FGS-GEOFENCE",
                    severity="HIGH",
                    store=PLAY,
                    guideline="Play Foreground services (April 2026 update)",
                    title=f"Location foreground service used for geofencing ({name})",
                    file=rel,
                    evidence=f"{name}: foregroundServiceType={fst}; geofencing code detected",
                    impact="Geofencing was removed as an approved foreground-service use case.",
                    fix="Use the Geofence API (GeofencingClient) instead of a location foreground "
                        "service.",
                    auto_fixable=False,
                )

    # Play Billing metadata
    if util.any_match(proj.root, catalog.SIGNALS["iap"]) and \
            "com.google.android.play.billingclient.version" not in text and merged:
        yield Finding(
            rule_id="PLAY-BILLING-META",
            severity="HIGH",
            store=PLAY,
            guideline="Play Billing requirements",
            title="Billing library version metadata missing from the merged manifest",
            file=rel,
            evidence="com.google.android.play.billingclient.version not present",
            impact="Play cannot determine your Billing Library version and flags the release.",
            fix="Add the Play Billing Library dependency properly (the plugin injects this "
                "metadata) rather than shading or vendoring it.",
            auto_fixable=False,
        )


def _permission_checks(proj, manifest_path, merged):
    if not manifest_path:
        return
    root = proj.root
    rel = util.rel(manifest_path, root)
    text = util.read_text(manifest_path)
    perms = _manifest_permissions(_parse_manifest(manifest_path), text)

    is_lending = bool(util.grep(root, catalog.SIGNALS["lending"],
                                {".strings", ".xml", ".json", ".md", ".kt", ".swift"})[:3])

    for perm in sorted(perms):
        spec = catalog.ANDROID_RESTRICTED_PERMISSIONS.get(perm)
        if not spec:
            continue
        severity, policy, fix = spec
        yield Finding(
            rule_id=f"PLAY-PERM-{perm.rsplit('.', 1)[-1]}",
            severity=severity,
            store=PLAY,
            guideline=policy,
            title=f"Restricted permission declared: {perm.rsplit('.', 1)[-1]}",
            file=rel,
            line=util.line_of(manifest_path, perm),
            evidence=f"<uses-permission android:name=\"{perm}\" />",
            impact="Restricted permissions require an approved Play Console declaration and a "
                   "core use case. Unjustified use blocks the release or removes the app.",
            fix=fix,
            auto_fixable=False,
        )

    if is_lending:
        bad = perms & catalog.LENDING_FORBIDDEN_PERMISSIONS
        if bad:
            yield Finding(
                rule_id="PLAY-LOAN-PERMS",
                severity="BLOCKER",
                store=PLAY,
                guideline="Play III.B Personal Loans",
                title="Lending app requests prohibited sensitive permissions",
                file=rel,
                evidence="Prohibited: " + ", ".join(sorted(bad)),
                impact="Automatic removal. Personal-loan apps may not access contacts, storage, "
                       "photos/video, precise location, or call log.",
                fix="Remove these permissions entirely. There is no declaration that permits "
                    "them for a lending app.",
                auto_fixable=False,
                confidence="medium",
            )

    # Prominent disclosure for sensitive access
    sensitive = perms & {
        "android.permission.ACCESS_BACKGROUND_LOCATION",
        "android.permission.READ_CONTACTS",
        "android.permission.READ_SMS",
        "android.permission.READ_CALL_LOG",
        "android.permission.RECORD_AUDIO",
        "android.permission.QUERY_ALL_PACKAGES",
        "android.permission.PACKAGE_USAGE_STATS",
        "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE",
    }
    if sensitive and not util.any_match(root, catalog.SIGNALS["prominent_disclosure"]):
        yield Finding(
            rule_id="PLAY-DISCLOSURE",
            severity="BLOCKER",
            store=PLAY,
            guideline="Play XI.C Prominent Disclosure and Consent",
            title="Sensitive data access with no prominent disclosure found",
            file=rel,
            evidence="Sensitive permissions: " + ", ".join(sorted(sensitive)) +
                     "; no disclosure/consent UI matched in source",
            impact="The most common Play rejection for permission-using apps. The runtime "
                   "permission dialog and the privacy policy do NOT satisfy this requirement.",
            fix="Add a dedicated in-app screen or dialog shown BEFORE the runtime permission "
                "request that names the data, states the use, makes clear this app collects it, "
                "and requires an affirmative tap. See "
                "assets/prominent-disclosure-snippets.md.",
            auto_fixable=True,
        )

    if "android.permission.AD_ID" not in {p for p in perms} and \
            "com.google.android.gms.permission.AD_ID" not in text and \
            util.any_match(root, catalog.SIGNALS["idfa"]):
        yield Finding(
            rule_id="PLAY-PERM-ADID",
            severity="HIGH",
            store=PLAY,
            guideline="Play Advertising ID policy",
            title="Advertising ID used without declaring com.google.android.gms.permission.AD_ID",
            file=rel,
            evidence="Advertising-ID code detected; AD_ID permission not in the manifest",
            impact="Apps targeting API 33+ must declare the permission; the Advertising ID "
                   "declaration in Play Console must also be completed.",
            fix='Add <uses-permission android:name="com.google.android.gms.permission.AD_ID" /> '
                "and complete the Advertising ID declaration, or remove the advertising-ID use.",
            auto_fixable=True,
        )


def _gradle_checks(proj):
    root = proj.root
    floors = catalog.FLOORS
    target_found = False

    for g in proj.gradle_files:
        text = util.read_text(g)
        rel = util.rel(g, root)

        for m in re.finditer(r"targetSdk(?:Version)?\s*[= ]\s*['\"]?(\d{2})", text):
            target_found = True
            value = int(m.group(1))
            if value < floors["play_target_sdk"]:
                yield Finding(
                    rule_id="PLAY-TARGETSDK",
                    severity="BLOCKER",
                    store=PLAY,
                    guideline=f"Play target API level requirement (deadline {floors['deadlines']['play_target_sdk_36']})",
                    title=f"targetSdk is {value}; Play requires {floors['play_target_sdk']}",
                    file=rel,
                    line=text[:m.start()].count("\n") + 1,
                    evidence=m.group(0),
                    impact="Play Console rejects the upload for new apps and updates.",
                    fix=f"Set targetSdk = {floors['play_target_sdk']} and compileSdk = "
                        f"{floors['play_target_sdk']}, then re-test runtime permissions, scoped "
                        f"storage, foreground service types, exact alarms, POST_NOTIFICATIONS, "
                        f"and PendingIntent mutability. An extension to "
                        f"{floors['deadlines']['play_extension']} can be requested in Play "
                        f"Console > Policy status before the deadline.",
                    suggested_value=str(floors["play_target_sdk"]),
                    auto_fixable=True,
                )

        for m in re.finditer(r"billing(?:-ktx)?[:'\"]{1,2}(\d+)\.(\d+)\.(\d+)", text):
            major = int(m.group(1))
            if major < floors["play_billing_major"]:
                yield Finding(
                    rule_id="PLAY-BILLING-VER",
                    severity="BLOCKER",
                    store=PLAY,
                    guideline=f"Play Billing Library deprecation (deadline {floors['deadlines']['play_billing_8']})",
                    title=f"Play Billing Library {m.group(1)}.{m.group(2)}.{m.group(3)}; "
                          f"version {floors['play_billing_major']}+ is required",
                    file=rel,
                    line=text[:m.start()].count("\n") + 1,
                    evidence=m.group(0),
                    impact="New apps and updates are rejected after the deadline.",
                    fix=f"Upgrade to com.android.billingclient:billing:{floors['play_billing_major']}.x "
                        f"and follow the migration guide. Re-test purchase, acknowledgement, and "
                        f"restore flows.",
                    suggested_value=f"{floors['play_billing_major']}.0.0",
                    auto_fixable=True,
                )

        if re.search(r"minifyEnabled\s+false", text) and "release" in text:
            yield Finding(
                rule_id="PLAY-MINIFY-OFF",
                severity="LOW",
                store=PLAY,
                guideline="Best practice",
                title="minifyEnabled is false for a release build type",
                file=rel,
                line=util.line_of(g, "minifyEnabled"),
                evidence="minifyEnabled false",
                impact="Larger binary and un-obfuscated code. Not a rejection, but enabling R8 "
                       "later is a common source of review-time crashes — do it now and test.",
                fix="Enable minifyEnabled and shrinkResources for release, then smoke-test the "
                    "release variant end to end.",
                auto_fixable=False,
            )

    if not target_found and proj.has_android:
        yield Finding(
            rule_id="PLAY-TARGETSDK-UNKNOWN",
            severity="HIGH",
            store=PLAY,
            guideline=f"Play target API level requirement (deadline {catalog.FLOORS['deadlines']['play_target_sdk_36']})",
            title="Could not determine targetSdk",
            file="",
            evidence="No targetSdk / targetSdkVersion found in any Gradle file",
            impact=f"The {catalog.FLOORS['play_target_sdk']} floor is days away; an unverified "
                   f"target level is a release risk.",
            fix=f"Set targetSdk explicitly to {catalog.FLOORS['play_target_sdk']} in the app "
                f"module (for Expo use expo-build-properties; for Flutter, "
                f"android/app/build.gradle).",
            auto_fixable=False,
        )


def _native_checks(proj):
    root = proj.root
    floors = catalog.FLOORS
    for artifact in proj.artifacts:
        if artifact.suffix not in (".aab", ".apk"):
            continue
        rel = util.rel(artifact, root)
        try:
            with zipfile.ZipFile(artifact) as zf:
                names = zf.namelist()
                sos = [n for n in names if n.endswith(".so")]
                abis = {n.split("/")[-2] for n in sos if "/" in n}
                if sos and not any("arm64" in a for a in abis):
                    yield Finding(
                        rule_id="PLAY-64BIT",
                        severity="BLOCKER",
                        store=PLAY,
                        guideline="Play 64-bit requirement",
                        title="No arm64-v8a native libraries in the artifact",
                        file=rel,
                        evidence=f"ABIs present: {sorted(abis) or 'none'}",
                        impact="32-bit-only uploads are rejected.",
                        fix="Add arm64-v8a to abiFilters / ndk.abiFilters and rebuild.",
                        auto_fixable=False,
                    )
                bad = []
                for name in sos[:400]:
                    with zf.open(name) as fh:
                        align = _elf_load_align(fh.read(65536))
                    if align is not None and align < floors["so_page_align"]:
                        bad.append((name, align))
                if bad:
                    yield Finding(
                        rule_id="PLAY-16KB",
                        severity="BLOCKER",
                        store=PLAY,
                        guideline="Play 16 KB page size requirement (in force 2025-11-01)",
                        title=f"{len(bad)} native libraries are not 16 KB aligned",
                        file=rel,
                        evidence="; ".join(f"{n} p_align=0x{a:x}" for n, a in bad[:8]),
                        impact="Required for apps with native code targeting API 35+; upload "
                               "is rejected.",
                        fix="Rebuild first-party native code with NDK r27+, AGP 8.5.1+ and "
                            "-Wl,-z,max-page-size=16384. Third-party .so files must be upgraded "
                            "to a 16 KB-aligned release — they cannot be realigned locally. Also "
                            'set android:extractNativeLibs="false" and useLegacyPackaging = false.',
                        auto_fixable=False,
                    )
        except (zipfile.BadZipFile, OSError, KeyError):
            continue

    if not proj.artifacts and proj.has_android:
        yield Finding(
            rule_id="PLAY-ARTIFACT-MISSING",
            severity="INFO",
            store=PLAY,
            guideline="Audit coverage",
            title="No .aab/.apk found — 16 KB alignment and ABIs unverified",
            file="",
            evidence="No build artifact in the project tree",
            impact="Two blocking requirements cannot be checked from source.",
            fix="Run `./gradlew bundleRelease` and re-run the audit against the project, or "
                "point --path at a directory containing the artifact.",
            auto_fixable=False,
        )


def _elf_load_align(data: bytes):
    """Return the p_align of the first PT_LOAD segment of an ELF64 image."""
    if len(data) < 64 or data[:4] != b"\x7fELF":
        return None
    if data[4] != 2:  # not ELF64
        return None
    little = data[5] == 1
    order = "little" if little else "big"

    def u(off, size):
        return int.from_bytes(data[off:off + size], order)

    e_phoff = u(0x20, 8)
    e_phentsize = u(0x36, 2)
    e_phnum = u(0x38, 2)
    if not e_phentsize or not e_phnum:
        return None
    for i in range(min(e_phnum, 64)):
        off = e_phoff + i * e_phentsize
        if off + 56 > len(data):
            return None
        if u(off, 4) == 1:  # PT_LOAD
            return u(off + 48, 8)
    return None
