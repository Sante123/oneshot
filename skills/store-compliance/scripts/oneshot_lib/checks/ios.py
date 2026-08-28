"""Apple / iOS deterministic checks."""
from __future__ import annotations

import re
from pathlib import Path

from .. import catalog, util
from ..model import APPLE, Finding, FindingList

# Only real source files justify an entitlement or a background mode. Searching
# plists/entitlements would let a capability justify itself.
CODE_EXTS = {".swift", ".m", ".mm", ".h", ".kt", ".java", ".js", ".jsx", ".ts",
             ".tsx", ".dart", ".cs"}


def _pick_app_plist(proj) -> Path | None:
    """Prefer the built Info.plist, else the app target's source Info.plist."""
    for app in proj.ios_built_apps:
        cand = app / "Info.plist"
        if cand.exists():
            return cand
    candidates = [p for p in proj.ios_info_plists
                  if "Tests" not in str(p) and "Extension" not in str(p)]
    if not candidates:
        candidates = list(proj.ios_info_plists)
    if not candidates:
        return None
    # shortest path is usually the app target
    return sorted(candidates, key=lambda p: len(p.parts))[0]


def _plist_effective(proj) -> dict:
    """Merge every source of Info.plist keys: plist file + Expo/Flutter config."""
    merged: dict = {}
    plist = _pick_app_plist(proj)
    if plist:
        merged.update(util.read_plist(plist))
    if proj.expo_config:
        text = util.read_text(proj.expo_config)
        for key in list(catalog.IOS_PURPOSE_STRINGS) + ["ITSAppUsesNonExemptEncryption"]:
            if re.search(rf'["\']?{re.escape(key)}["\']?\s*:', text):
                merged.setdefault(key, "<from app config>")
        if re.search(r'usesNonExemptEncryption', text):
            merged.setdefault("ITSAppUsesNonExemptEncryption", "<from app config>")
    return merged


def check(proj) -> FindingList:
    out = FindingList()
    root = proj.root
    if not proj.has_ios:
        return out

    plist_path = _pick_app_plist(proj)
    plist_rel = util.rel(plist_path, root) if plist_path else "ios/Info.plist"
    plist = _plist_effective(proj)
    from_built = bool(plist_path and any(str(a) in str(plist_path) for a in proj.ios_built_apps))

    out.extend_from(_purpose_strings(proj, plist, plist_rel))
    out.extend_from(_plist_keys(proj, plist, plist_rel))
    out.extend_from(_background_modes(proj, plist, plist_rel))
    out.extend_from(_privacy_manifest(proj))
    out.extend_from(_entitlements(proj))
    out.extend_from(_binary_hygiene(proj))
    out.extend_from(_sdk_floor(proj, plist, plist_rel, from_built))
    return out


# --------------------------------------------------------------------------
def _purpose_strings(proj, plist, plist_rel):
    root = proj.root
    for key, (pattern, human) in catalog.IOS_PURPOSE_STRINGS.items():
        hits = util.grep(root, pattern)
        if not hits:
            continue
        hit = hits[0]
        value = plist.get(key)
        if key not in plist:
            yield Finding(
                rule_id=f"APPLE-PLIST-{key}",
                severity="BLOCKER",
                store=APPLE,
                guideline="Apple 5.1.1(ii) / ITMS-90683",
                title=f"Missing {key} but the code uses {human}",
                file=util.rel(hit[0], root),
                line=hit[1],
                evidence=f"{util.rel(hit[0], root)}:{hit[1]}: {hit[2]}",
                impact="Upload fails with ITMS-90683, or the app crashes on the reviewer's "
                       "device the moment the permission is requested.",
                fix=f"Add {key} to {plist_rel} (and to every target that triggers the prompt) "
                    f"with text naming the feature and the user benefit.",
                suggested_value=_suggest_purpose(human),
                auto_fixable=True,
            )
            continue
        if isinstance(value, str):
            for vague in catalog.VAGUE_PURPOSE_PATTERNS:
                if re.search(vague, value.strip(), re.IGNORECASE):
                    yield Finding(
                        rule_id=f"APPLE-PLIST-VAGUE-{key}",
                        severity="HIGH",
                        store=APPLE,
                        guideline="Apple 5.1.1(ii)",
                        title=f"{key} is too vague",
                        file=plist_rel,
                        line=util.line_of(Path(proj.root / plist_rel), key) if (proj.root / plist_rel).exists() else 0,
                        evidence=f'{key} = "{value}"',
                        impact="Reviewers reject purpose strings that do not explain what the "
                               "data is used for.",
                        fix="Rewrite as '<App> uses <resource> to <specific user-facing outcome>.' "
                            "and localize it in InfoPlist.strings for every shipped locale.",
                        suggested_value=_suggest_purpose(catalog.IOS_PURPOSE_STRINGS[key][1]),
                        auto_fixable=True,
                    )
                    break


def _suggest_purpose(human: str) -> str:
    templates = {
        "camera": "Take photos of receipts to attach them to an expense.",
        "microphone": "Record voice notes you can attach to an entry.",
        "photo library (read)": "Choose an existing photo to attach to an entry.",
        "photo library (write)": "Save the images you create back to your photo library.",
        "location (when in use)": "Show places near you and tag entries with where they happened.",
        "location (always)": "Send you a reminder when you arrive at a place you saved.",
        "contacts": "Let you pick a contact to share an entry with.",
        "calendar": "Add the events you create to your calendar.",
        "motion & fitness": "Count your steps so your activity summary is accurate.",
        "HealthKit (read)": "Read your workouts so your activity summary is accurate.",
        "HealthKit (write)": "Save the workouts you record to the Health app.",
        "Bluetooth": "Connect to your device so it can sync readings.",
        "local network": "Find your device on the same Wi-Fi network so it can connect.",
        "speech recognition": "Turn your dictated notes into text.",
        "Face ID": "Unlock the app without typing your password.",
        "App Tracking Transparency": "Measure whether the ads that brought you here worked, "
                                     "so we can keep the app free.",
        "media library": "Play your own music alongside a session.",
    }
    body = templates.get(human, f"Provide the feature that requires {human}.")
    return f"[YourApp] uses {human} to {body[0].lower()}{body[1:]}"


# --------------------------------------------------------------------------
def _plist_keys(proj, plist, plist_rel):
    root = proj.root
    if "ITSAppUsesNonExemptEncryption" not in plist:
        yield Finding(
            rule_id="APPLE-5.1-ENCRYPTION",
            severity="HIGH",
            store=APPLE,
            guideline="Apple 5.1 / export compliance",
            title="ITSAppUsesNonExemptEncryption is not set",
            file=plist_rel,
            evidence="Key absent from the effective Info.plist",
            impact="Every submission stalls on a manual export-compliance question, and the "
                   "build cannot be released until it is answered.",
            fix="Add <key>ITSAppUsesNonExemptEncryption</key><false/> if you only use HTTPS/TLS "
                "and Apple-provided cryptography. Set true only if you ship your own non-exempt "
                "crypto, and then attach export documentation.",
            suggested_value="false",
            auto_fixable=True,
        )

    ats = plist.get("NSAppTransportSecurity")
    if isinstance(ats, dict) and ats.get("NSAllowsArbitraryLoads") is True:
        yield Finding(
            rule_id="APPLE-ATS-ARBITRARY",
            severity="MEDIUM",
            store=APPLE,
            guideline="Apple 1.6 Data Security / 2.5.1",
            title="App Transport Security is disabled globally",
            file=plist_rel,
            evidence="NSAllowsArbitraryLoads = true",
            impact="Draws reviewer scrutiny and may be asked to justify; also a security finding "
                   "in Play's equivalent scan.",
            fix="Remove NSAllowsArbitraryLoads and add per-domain NSExceptionDomains entries only "
                "for hosts that genuinely cannot serve TLS.",
            auto_fixable=False,
        )

    schemes = plist.get("LSApplicationQueriesSchemes")
    if isinstance(schemes, list) and len(schemes) > 25:
        yield Finding(
            rule_id="APPLE-5.1.2-QUERYSCHEMES",
            severity="HIGH",
            store=APPLE,
            guideline="Apple 5.1.2(iv)",
            title=f"LSApplicationQueriesSchemes enumerates {len(schemes)} apps",
            file=plist_rel,
            evidence=f"{len(schemes)} schemes declared",
            impact="Collecting information about which apps are installed, for analytics or "
                   "advertising, is prohibited.",
            fix="Keep only the schemes you actually open. Remove any scheme used to detect "
                "whether a competitor or partner app is installed.",
            auto_fixable=False,
        )


# --------------------------------------------------------------------------
def _background_modes(proj, plist, plist_rel):
    root = proj.root
    modes = plist.get("UIBackgroundModes")
    if not isinstance(modes, list):
        return
    for mode in modes:
        pattern = catalog.BACKGROUND_MODE_JUSTIFICATION.get(mode)
        if not pattern:
            continue
        if not util.any_match(root, pattern, CODE_EXTS):
            yield Finding(
                rule_id="APPLE-2.5.4-BGMODES",
                severity="HIGH",
                store=APPLE,
                guideline="Apple 2.5.4",
                title=f"UIBackgroundModes declares '{mode}' but no matching code was found",
                file=plist_rel,
                evidence=f"Declared mode: {mode}; no source match for /{pattern}/",
                impact="Declaring a background mode the app does not use is an explicit "
                       "rejection under 2.5.4.",
                fix=f"Remove '{mode}' from UIBackgroundModes, or implement the corresponding "
                    f"functionality and describe it in Notes for Review.",
                auto_fixable=True,
            )


# --------------------------------------------------------------------------
def _privacy_manifest(proj):
    root = proj.root
    manifests = proj.ios_privacy_manifests
    used = {}
    for category, spec in catalog.REQUIRED_REASON_APIS.items():
        hits = util.grep(root, spec["pattern"], {".swift", ".m", ".mm", ".h", ".dart", ".kt"})
        if hits:
            used[category] = hits[0]

    if not manifests:
        if used:
            first = next(iter(used.values()))
            yield Finding(
                rule_id="APPLE-5.1.3-MANIFEST",
                severity="BLOCKER",
                store=APPLE,
                guideline="Apple privacy manifest requirement / ITMS-91053",
                title="No PrivacyInfo.xcprivacy, but the code uses Required Reason APIs",
                file=util.rel(first[0], root),
                line=first[1],
                evidence="Categories detected: " + ", ".join(sorted(used)),
                impact="Upload is rejected with ITMS-91053.",
                fix="Add PrivacyInfo.xcprivacy to the app target (and to every extension and "
                    "first-party framework) declaring each category with a valid reason code. "
                    "Start from assets/PrivacyInfo.xcprivacy.template.",
                auto_fixable=True,
            )
        else:
            yield Finding(
                rule_id="APPLE-MANIFEST-ABSENT",
                severity="MEDIUM",
                store=APPLE,
                guideline="Apple privacy manifest requirement",
                title="No PrivacyInfo.xcprivacy found",
                file="",
                evidence="No PrivacyInfo.xcprivacy anywhere in the project",
                impact="Required if the app or any first-party framework touches a Required "
                       "Reason API, and needed to declare tracking domains and collected data.",
                fix="Add PrivacyInfo.xcprivacy from assets/PrivacyInfo.xcprivacy.template and "
                    "fill in NSPrivacyTracking, NSPrivacyTrackingDomains and "
                    "NSPrivacyCollectedDataTypes to match your App Privacy label.",
                auto_fixable=True,
            )
        return

    for man in manifests:
        data = util.read_plist(man)
        rel = util.rel(man, root)
        legal = {"NSPrivacyTracking", "NSPrivacyTrackingDomains",
                 "NSPrivacyCollectedDataTypes", "NSPrivacyAccessedAPITypes"}
        for key in data:
            if key not in legal:
                yield Finding(
                    rule_id="APPLE-MANIFEST-BADKEY",
                    severity="BLOCKER",
                    store=APPLE,
                    guideline="ITMS-91056",
                    title=f"Unknown key '{key}' in the privacy manifest",
                    file=rel,
                    evidence=f"Key: {key}",
                    impact="Upload rejected with ITMS-91056 (invalid privacy manifest).",
                    fix="Remove the key. Only NSPrivacyTracking, NSPrivacyTrackingDomains, "
                        "NSPrivacyCollectedDataTypes and NSPrivacyAccessedAPITypes are legal.",
                    auto_fixable=True,
                )

        declared = {}
        for entry in data.get("NSPrivacyAccessedAPITypes") or []:
            if isinstance(entry, dict):
                declared[entry.get("NSPrivacyAccessedAPIType")] = entry.get(
                    "NSPrivacyAccessedAPITypeReasons") or []

        for category, hit in used.items():
            if category not in declared:
                yield Finding(
                    rule_id="APPLE-MANIFEST-MISSINGCAT",
                    severity="BLOCKER",
                    store=APPLE,
                    guideline="ITMS-91053",
                    title=f"Required Reason API used but not declared: {category}",
                    file=util.rel(hit[0], root),
                    line=hit[1],
                    evidence=f"{util.rel(hit[0], root)}:{hit[1]}: {hit[2]}",
                    impact="Upload rejected with ITMS-91053.",
                    fix=f"Add {category} to NSPrivacyAccessedAPITypes in {rel} with reason "
                        f"{catalog.REQUIRED_REASON_APIS[category]['default']} "
                        f"(valid: {', '.join(catalog.REQUIRED_REASON_APIS[category]['reasons'])}).",
                    suggested_value=catalog.REQUIRED_REASON_APIS[category]["default"],
                    auto_fixable=True,
                )

        for category, reasons in declared.items():
            spec = catalog.REQUIRED_REASON_APIS.get(category)
            if not spec:
                continue
            if not reasons:
                yield Finding(
                    rule_id="APPLE-MANIFEST-NOREASON",
                    severity="BLOCKER",
                    store=APPLE,
                    guideline="ITMS-91053",
                    title=f"{category} declared with no reason code",
                    file=rel,
                    evidence=f"{category}: []",
                    impact="Upload rejected.",
                    fix=f"Add a reason code. Valid values: {', '.join(spec['reasons'])}.",
                    suggested_value=spec["default"],
                    auto_fixable=True,
                )
            for reason in reasons:
                if reason not in spec["reasons"]:
                    yield Finding(
                        rule_id="APPLE-MANIFEST-BADREASON",
                        severity="BLOCKER",
                        store=APPLE,
                        guideline="ITMS-91053",
                        title=f"Invalid reason code '{reason}' for {category}",
                        file=rel,
                        evidence=f"{category} -> {reason}",
                        impact="Upload rejected; reason codes are an exact enumerated set.",
                        fix=f"Use one of: {', '.join(spec['reasons'])}.",
                        suggested_value=spec["default"],
                        auto_fixable=True,
                    )

        tracking = data.get("NSPrivacyTracking")
        domains = data.get("NSPrivacyTrackingDomains") or []
        tracking_sdk = None
        for token in catalog.TRACKING_SDK_TOKENS:
            if _dep_present(proj, token):
                tracking_sdk = token
                break
        if tracking_sdk and tracking is not True:
            yield Finding(
                rule_id="APPLE-MANIFEST-TRACKING",
                severity="HIGH",
                store=APPLE,
                guideline="Apple 5.1.2(i)",
                title=f"NSPrivacyTracking is not true, but {tracking_sdk} is linked",
                file=rel,
                evidence=f"Dependency detected: {tracking_sdk}; NSPrivacyTracking = {tracking!r}",
                impact="Inconsistent tracking declaration; the nutrition label, the manifest and "
                       "observed traffic must agree.",
                fix="Set NSPrivacyTracking to true and list every tracking domain in "
                    "NSPrivacyTrackingDomains, or remove the tracking SDK.",
                auto_fixable=False,
            )
        if tracking is True and not domains:
            yield Finding(
                rule_id="APPLE-MANIFEST-NODOMAINS",
                severity="HIGH",
                store=APPLE,
                guideline="Apple 5.1.2(i)",
                title="NSPrivacyTracking is true but NSPrivacyTrackingDomains is empty",
                file=rel,
                evidence="NSPrivacyTrackingDomains = []",
                impact="Tracking domains must be listed so they can be blocked when the user "
                       "denies ATT. An empty list with live tracking traffic is a violation.",
                fix="List every domain that receives tracking traffic.",
                auto_fixable=False,
            )


def _dep_present(proj, token: str) -> bool:
    for path in filter(None, [proj.podfile_lock, proj.package_json, proj.pubspec]):
        if token.lower() in util.read_text(path).lower():
            return True
    for g in proj.gradle_files:
        if token.lower() in util.read_text(g).lower():
            return True
    return False


# --------------------------------------------------------------------------
def _entitlements(proj):
    root = proj.root
    for ent in proj.ios_entitlements:
        data = util.read_plist(ent)
        rel = util.rel(ent, root)
        if data.get("get-task-allow") is True and "Debug" not in rel:
            yield Finding(
                rule_id="APPLE-ENT-TASKALLOW",
                severity="BLOCKER",
                store=APPLE,
                guideline="App Store distribution requirements",
                title="get-task-allow is true in an entitlements file",
                file=rel,
                evidence="get-task-allow = true",
                impact="A debuggable binary cannot be distributed; upload is rejected.",
                fix="Set get-task-allow to false, or use a Release-only entitlements file.",
                auto_fixable=True,
            )
        for key, pattern in catalog.ENTITLEMENT_JUSTIFICATION.items():
            if key not in data:
                continue
            if not util.any_match(root, pattern, CODE_EXTS):
                yield Finding(
                    rule_id="APPLE-2.5.4-ORPHANENT",
                    severity="HIGH",
                    store=APPLE,
                    guideline="Apple 2.5.4",
                    title=f"Entitlement '{key}' is declared but appears unused",
                    file=rel,
                    evidence=f"No source match for /{pattern}/",
                    impact="Orphan entitlements are rejected; they also expand your privacy "
                           "declaration surface for no reason.",
                    fix=f"Remove '{key}' from {rel} and from the App ID capabilities, or "
                        f"implement the feature and describe it in Notes for Review.",
                    auto_fixable=True,
                )
        if "com.apple.developer.associated-domains" in data:
            yield Finding(
                rule_id="APPLE-AASA-VERIFY",
                severity="LOW",
                store=APPLE,
                guideline="Apple 2.5.4 / universal links",
                title="Associated domains declared — verify the AASA file is live",
                file=rel,
                evidence=str(data.get("com.apple.developer.associated-domains"))[:200],
                impact="A missing or misserved apple-app-site-association breaks universal "
                       "links, which reviewers do test.",
                fix="Confirm https://<domain>/.well-known/apple-app-site-association returns "
                    "200 with Content-Type application/json and no redirect.",
                auto_fixable=False,
                confidence="medium",
            )
        if "com.apple.developer.networking.vpn.api" in data:
            yield Finding(
                rule_id="APPLE-5.4-VPN",
                severity="HIGH",
                store=APPLE,
                guideline="Apple 5.4",
                title="VPN entitlement present — organization account required",
                file=rel,
                evidence="com.apple.developer.networking.vpn.api",
                impact="VPN apps must be submitted by a developer enrolled as an organization, "
                       "must use NEVPNManager, and must never sell or disclose user data.",
                fix="Confirm the account is an Organization enrollment, state the data practices "
                    "explicitly in the privacy policy, and be ready to provide a local licence "
                    "where required.",
                auto_fixable=False,
            )


# --------------------------------------------------------------------------
def _binary_hygiene(proj):
    root = proj.root
    for name, pattern, rule, sev, guideline, impact, fix in [
        ("UIWebView", catalog.SIGNALS["uiwebview"], "APPLE-UIWEBVIEW", "BLOCKER",
         "Apple 2.5.1 / ITMS-90809",
         "UIWebView has been removed; upload fails.",
         "Migrate to WKWebView. If the reference comes from a dependency, upgrade it."),
        ("private API access", catalog.SIGNALS["private_api"], "APPLE-2.5.1-PRIVATEAPI",
         "BLOCKER", "Apple 2.5.1 / ITMS-90338",
         "Apple's static analysis flags private selectors; automatic rejection.",
         "Remove the call. If it comes from a dependency, upgrade or replace it."),
        ("hardcoded IPv4 address", catalog.SIGNALS["ipv4_literal"], "APPLE-2.5.5-IPV6",
         "HIGH", "Apple 2.5.5",
         "Apple's review network is IPv6-only (NAT64/DNS64); IPv4 literals fail there.",
         "Use hostnames and verify the backend resolves over IPv6. Test on a NAT64 network."),
    ]:
        hits = util.grep(root, pattern, {".swift", ".m", ".mm", ".h", ".kt", ".java",
                                         ".js", ".ts", ".tsx", ".dart"})
        for hit in hits[:5]:
            yield Finding(
                rule_id=rule, severity=sev, store=APPLE, guideline=guideline,
                title=f"Possible {name}",
                file=util.rel(hit[0], root), line=hit[1],
                evidence=hit[2], impact=impact, fix=fix,
                auto_fixable=False,
                confidence="medium" if rule == "APPLE-2.5.5-IPV6" else "high",
            )

    hits = util.grep(root, catalog.SIGNALS["custom_review_prompt"],
                     {".swift", ".kt", ".dart", ".tsx", ".ts", ".strings", ".xml"})
    if hits and not util.any_match(root, catalog.SIGNALS["review_prompt"]):
        hit = hits[0]
        yield Finding(
            rule_id="APPLE-5.6.1-REVIEWS",
            severity="HIGH",
            store=APPLE,
            guideline="Apple 5.6.1 / Play Ratings policy",
            title="Custom rating prompt without the system review API",
            file=util.rel(hit[0], root), line=hit[1],
            evidence=hit[2],
            impact="Custom or incentivized review prompts, and filtering users toward positive "
                   "reviews, violate the Developer Code of Conduct.",
            fix="Use SKStoreReviewController / AppStore.requestReview (iOS) and the Play "
                "In-App Review API. Never gate functionality on leaving a review.",
            auto_fixable=False,
        )


# --------------------------------------------------------------------------
def _sdk_floor(proj, plist, plist_rel, from_built):
    floor = catalog.FLOORS["apple_build_sdk_major"]
    sdk_name = plist.get("DTSDKName")
    if isinstance(sdk_name, str):
        m = re.search(r"(\d+)", sdk_name)
        if m and int(m.group(1)) < floor:
            yield Finding(
                rule_id="APPLE-SDK-FLOOR",
                severity="BLOCKER",
                store=APPLE,
                guideline=f"Apple minimum SDK requirement (in force {catalog.FLOORS['deadlines']['apple_xcode_26']})",
                title=f"Built with {sdk_name}; iOS {floor} SDK or later is required",
                file=plist_rel,
                evidence=f"DTSDKName = {sdk_name}",
                impact="App Store Connect rejects the upload.",
                fix=f"Build with Xcode {floor}+ using the iOS {floor} SDK. Your deployment "
                    f"target does not need to change. Update the CI image (and the EAS build "
                    f"image for Expo).",
                auto_fixable=False,
            )
    elif not from_built:
        yield Finding(
            rule_id="APPLE-SDK-UNVERIFIED",
            severity="INFO",
            store=APPLE,
            guideline=f"Apple minimum SDK requirement ({catalog.FLOORS['deadlines']['apple_xcode_26']})",
            title="Build SDK version could not be verified from source",
            file="",
            evidence="No built .app found; DTSDKName is only present in a built Info.plist",
            impact="Cannot confirm the Xcode 26 / iOS 26 SDK floor without an archive.",
            fix="Run `xcodebuild -version` (expect 26.x) and check DTSDKName in the built "
                "Info.plist, or re-run this audit against an extracted .ipa.",
            auto_fixable=False,
            confidence="high",
        )
