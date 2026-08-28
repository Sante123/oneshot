"""Checks that apply to both stores: privacy, accounts, monetization, UGC, AI, hygiene."""
from __future__ import annotations

import re
from pathlib import Path

from .. import catalog, util
from ..model import APPLE, BOTH, Finding, FindingList, PLAY


def check(proj) -> FindingList:
    out = FindingList()
    out.extend_from(_accounts(proj))
    out.extend_from(_privacy_policy(proj))
    out.extend_from(_att(proj))
    out.extend_from(_ai(proj))
    out.extend_from(_ugc(proj))
    out.extend_from(_monetization(proj))
    out.extend_from(_login(proj))
    out.extend_from(_hygiene(proj))
    out.extend_from(_sdk_inventory(proj))
    return out


CODE_EXTS = {".swift", ".m", ".mm", ".h", ".kt", ".java", ".js", ".jsx", ".ts",
             ".tsx", ".dart", ".cs"}


def _sig(proj, key):
    """Matches for a signal, with real source files ranked ahead of build config."""
    hits = util.grep(proj.root, catalog.SIGNALS[key])
    return sorted(hits, key=lambda h: (h[0].suffix not in CODE_EXTS, str(h[0])))


def _has(proj, key):
    return bool(_sig(proj, key)[:1])


# --------------------------------------------------------------------------
def _accounts(proj):
    root = proj.root
    acc = _sig(proj, "accounts")
    if not acc:
        return
    if not _has(proj, "account_deletion"):
        hit = acc[0]
        yield Finding(
            rule_id="XPLAT-ACCOUNT-DELETE",
            severity="BLOCKER",
            store=BOTH,
            guideline="Apple 5.1.1(v) / Play XI.F Account Deletion",
            title="Account creation exists with no in-app account deletion",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence=f"Account creation at {util.rel(hit[0], root)}:{hit[1]}; no match for "
                     f"/{catalog.SIGNALS['account_deletion']}/ anywhere in the project",
            impact="Guaranteed rejection on both stores. Apple requires an in-app deletion path; "
                   "Play additionally requires a web deletion URL declared in Console.",
            fix="Add Settings > Account > Delete Account, reachable in <= 3 taps, that confirms "
                "and then actually deletes server-side (not deactivates). Also publish a web "
                "deletion URL and declare it in Play Console > App content > Data safety. "
                "See assets/prominent-disclosure-snippets.md for reference implementations.",
            auto_fixable=True,
        )
    else:
        yield Finding(
            rule_id="PLAY-DELETE-WEBURL",
            severity="MEDIUM",
            store=PLAY,
            guideline="Play XI.F Account Deletion",
            title="Verify the web account-deletion URL is published and declared",
            file="",
            evidence="In-app deletion found; the separate web URL cannot be verified from code",
            impact="Play requires a deletion request URL that works without installing the app.",
            fix="Publish a deletion request page at a stable HTTPS URL and enter it in "
                "Play Console > App content > Data safety > Account deletion.",
            auto_fixable=False,
            confidence="medium",
        )


# --------------------------------------------------------------------------
def _privacy_policy(proj):
    if not _has(proj, "privacy_policy"):
        yield Finding(
            rule_id="XPLAT-PRIVACY-POLICY",
            severity="BLOCKER",
            store=BOTH,
            guideline="Apple 5.1.1(i) / Play XI.E Privacy Policy",
            title="No in-app privacy policy link found",
            file="",
            evidence=f"No match for /{catalog.SIGNALS['privacy_policy']}/ in the project",
            impact="Both stores require a privacy policy linked in the store listing AND "
                   "accessible inside the app.",
            fix="Publish the policy at a stable HTTPS URL (HTML, not a PDF, not editable), link "
                "it from Settings/About in the app, and enter the URL in App Store Connect and "
                "Play Console. Start from assets/privacy-policy-template.md.",
            auto_fixable=True,
        )


# --------------------------------------------------------------------------
def _att(proj):
    root = proj.root
    idfa = _sig(proj, "idfa")
    tracking_sdk = [t for t in catalog.TRACKING_SDK_TOKENS if _dep(proj, t)]
    if not idfa and not tracking_sdk:
        return
    if not _has(proj, "att"):
        where = idfa[0] if idfa else None
        yield Finding(
            rule_id="APPLE-5.1.2-ATT",
            severity="BLOCKER",
            store=APPLE,
            guideline="Apple 5.1.2(i) App Tracking Transparency",
            title="Tracking/IDFA usage without an App Tracking Transparency request",
            file=util.rel(where[0], root) if where else "",
            line=where[1] if where else 0,
            evidence=(f"{util.rel(where[0], root)}:{where[1]}: {where[2]}" if where else "") +
                     (f" | tracking SDKs: {', '.join(tracking_sdk)}" if tracking_sdk else ""),
            impact="Reading the IDFA or linking user data with third-party data for advertising "
                   "without ATT authorization is an automatic rejection.",
            fix="Add NSUserTrackingUsageDescription, call "
                "ATTrackingManager.requestTrackingAuthorization before any IDFA read or ad-SDK "
                "initialization that uses it, gate the read on .authorized, and implement no "
                "fingerprinting fallback. Declare NSPrivacyTracking = true with every tracking "
                "domain listed.",
            auto_fixable=False,
        )


# --------------------------------------------------------------------------
def _ai(proj):
    root = proj.root
    hits = util.grep(root, catalog.AI_ENDPOINT_PATTERN)
    if not hits:
        return
    hit = hits[0]
    disclosed = util.any_match(
        root,
        r"(?i)(sent to|processed by|shared with|third[- ]party).{0,60}(AI|model|OpenAI|Anthropic|Gemini|LLM)"
        r"|AIDisclosure|ai_consent|aiConsent|modelDisclosure",
    )
    if not disclosed:
        yield Finding(
            rule_id="XPLAT-AI-DISCLOSURE",
            severity="BLOCKER",
            store=BOTH,
            guideline="Apple 5.1.2(i) (Nov 2025) / Play XI.A User Data (July 2026)",
            title="User content sent to a third-party AI provider with no disclosure or consent",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence=f"{util.rel(hit[0], root)}:{hit[1]}: {hit[2]}",
            impact="Apple added an explicit clause in November 2025 requiring disclosure and "
                   "consent before sharing personal data with third-party AI. Play clarified the "
                   "same in July 2026.",
            fix="Add a first-run disclosure naming the provider and exactly what is sent, record "
                "affirmative consent before the first request, name the provider in the privacy "
                "policy, and declare User Content as collected AND shared in both the App "
                "Privacy label and the Data safety form.",
            auto_fixable=False,
        )

    reportable = util.any_match(
        root, r"reportResponse|reportMessage|flagResponse|report_ai|thumbs?[_ ]?down|feedbackNegative")
    if not reportable:
        yield Finding(
            rule_id="PLAY-AI-REPORT",
            severity="HIGH",
            store=PLAY,
            guideline="Play IX AI-Generated Content",
            title="AI-generated content with no in-app reporting mechanism",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence="AI endpoint detected; no report/flag control matched in source",
            impact="Play requires an in-app reporting mechanism in the context where AI content "
                   "appears, and requires those reports to inform filtering.",
            fix="Add a 'Report this response' control on each AI message that files into a real "
                "moderation queue, and apply the reports to your filtering.",
            auto_fixable=True,
        )

    moderated = util.any_match(root, r"moderation|/moderations|safetySettings|contentFilter|blocklist")
    if not moderated:
        yield Finding(
            rule_id="XPLAT-AI-MODERATION",
            severity="HIGH",
            store=BOTH,
            guideline="Play IX / Apple 1.1, 1.2",
            title="No input/output moderation detected around AI generation",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence="AI endpoint detected; no moderation call, safety settings, or blocklist found",
            impact="Both stores hold you responsible for what the model produces, including "
                   "restricted content categories.",
            fix="Call the provider's moderation endpoint (or your own classifier) on inputs and "
                "outputs, and add a policy layer for self-harm, weapons, CSAE, medical/legal "
                "advice, and real-person likenesses.",
            auto_fixable=False,
            confidence="medium",
        )


# --------------------------------------------------------------------------
def _ugc(proj):
    root = proj.root
    ugc = _sig(proj, "ugc")
    if not ugc:
        return
    hit = ugc[0]
    missing = []
    if not _has(proj, "ugc_report"):
        missing.append("report content/user")
    if not _has(proj, "ugc_block"):
        missing.append("block user")
    if not util.any_match(root, r"moderat|profanity|blocklist|contentFilter|badWords|toxicity"):
        missing.append("objectionable-content filtering")
    if not util.any_match(root, r"terms|community ?guidelines|acceptable ?use"):
        missing.append("terms of service acceptance")

    if missing:
        yield Finding(
            rule_id="XPLAT-UGC-CONTROLS",
            severity="BLOCKER",
            store=BOTH,
            guideline="Apple 1.2 / Play VI User Generated Content",
            title="User-generated content without the required moderation controls",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence=f"UGC detected at {util.rel(hit[0], root)}:{hit[1]}; missing: "
                     + ", ".join(missing),
            impact="Apple requires filtering, reporting with timely responses, user blocking, and "
                   "published contact info — all four. Play requires the same plus ToS "
                   "acceptance. Missing any one is a rejection.",
            fix="Add the missing controls. Report and block must be reachable in <= 2 taps from "
                "both the content and the profile, filtering must run before content is publicly "
                "visible, and you must commit to removing violating content and ejecting the "
                "user within 24 hours. Document all of it in Notes for Review.",
            auto_fixable=True,
        )


# --------------------------------------------------------------------------
def _monetization(proj):
    root = proj.root
    iap = _sig(proj, "iap")
    external = _sig(proj, "external_payment")

    if iap and not _has(proj, "restore"):
        hit = iap[0]
        yield Finding(
            rule_id="APPLE-3.1.1-RESTORE",
            severity="BLOCKER",
            store=BOTH,
            guideline="Apple 3.1.1 / Play Billing",
            title="In-app purchases without a Restore Purchases path",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence=f"IAP code at {util.rel(hit[0], root)}:{hit[1]}; no restore/sync call found",
            impact="A restore mechanism is mandatory for non-consumables and subscriptions, and "
                   "must work without being signed in.",
            fix="Add a 'Restore Purchases' action on the paywall and in Settings that calls "
                "AppStore.sync() / restoreCompletedTransactions on iOS and "
                "queryPurchasesAsync on Android, and that works signed out.",
            auto_fixable=True,
        )

    paywall = _sig(proj, "paywall")
    if paywall:
        pw_files = {h[0] for h in paywall}
        blob = "\n".join(util.read_text(p) for p in list(pw_files)[:12])
        needs = {
            "auto-renewal statement": r"(?i)renew|auto-?renew",
            "Terms of Use link": r"(?i)terms of (use|service)|EULA",
            "Privacy Policy link": r"(?i)privacy policy",
        }
        missing = [label for label, rx in needs.items() if not re.search(rx, blob)]
        if missing:
            hit = paywall[0]
            yield Finding(
                rule_id="APPLE-3.1.2-PAYWALL",
                severity="BLOCKER",
                store=APPLE,
                guideline="Apple 3.1.2(c)",
                title="Paywall is missing required subscription disclosures",
                file=util.rel(hit[0], root),
                line=hit[1],
                evidence="Missing from the paywall source: " + ", ".join(missing),
                impact="The most commonly cited subscription rejection. Title, period, price, "
                       "renewal terms, and tappable Terms + Privacy links must all be visible "
                       "without scrolling, next to the buy button.",
                fix="Add the missing elements to the paywall view, and fill the Terms of Use "
                    "(EULA) URL in App Store Connect.",
                auto_fixable=True,
            )

    if external and iap:
        hit = external[0]
        yield Finding(
            rule_id="APPLE-3.1.1-EXTPAY",
            severity="HIGH",
            store=BOTH,
            guideline="Apple 3.1.1 / 3.1.3 / Play Monetization",
            title="External payment processor alongside in-app purchase",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence=f"{util.rel(hit[0], root)}:{hit[1]}: {hit[2]}",
            impact="Digital content consumed in the app must use IAP / Play Billing. Physical "
                   "goods and real-world services must NOT use them. Getting either direction "
                   "wrong is a rejection.",
            fix="Classify every purchasable item against the decision tree in "
                "references/monetization.md section 1, and route each through the correct rail. "
                "Remove any in-app steering to external purchase outside the US storefront and "
                "the External Purchase Link / Reader entitlements.",
            auto_fixable=False,
            confidence="medium",
        )
    elif external and not iap:
        hit = external[0]
        yield Finding(
            rule_id="APPLE-3.1.1-IAP",
            severity="HIGH",
            store=BOTH,
            guideline="Apple 3.1.1 / Play Monetization",
            title="External payment processor with no store billing integration",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence=f"{util.rel(hit[0], root)}:{hit[1]}: {hit[2]}",
            impact="If anything sold here is digital content unlocked inside the app, this is a "
                   "certain rejection on both stores.",
            fix="If you sell physical goods or real-world services, this is fine — note it in "
                "Notes for Review. If you sell digital content or features, migrate to StoreKit "
                "and Play Billing.",
            auto_fixable=False,
            confidence="medium",
        )


# --------------------------------------------------------------------------
def _login(proj):
    root = proj.root
    social = _sig(proj, "social_login")
    if not social:
        return
    if not _has(proj, "sign_in_with_apple") and proj.has_ios:
        hit = social[0]
        yield Finding(
            rule_id="APPLE-4.8-SIWA",
            severity="BLOCKER",
            store=APPLE,
            guideline="Apple 4.8 Login Services",
            title="Third-party social login without a privacy-preserving alternative",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence=f"{util.rel(hit[0], root)}:{hit[1]}: {hit[2]}; no Sign in with Apple found",
            impact="Apps using a third-party or social login as the primary account mechanism "
                   "must also offer an equivalent option limited to name and email, with a "
                   "private-email option and no ad tracking without consent.",
            fix="Add Sign in with Apple (or an equivalent privacy-preserving login). Exempt if "
                "you use only your own account system, are an education/enterprise app requiring "
                "an existing institutional account, use a government citizen ID, or are a client "
                "for that specific third-party service — if an exemption applies, record it as a "
                "waiver with the reason.",
            auto_fixable=False,
        )


# --------------------------------------------------------------------------
def _hygiene(proj):
    root = proj.root

    text_exts = {".strings", ".xcstrings", ".xml", ".json", ".md", ".txt", ".swift",
                 ".kt", ".dart", ".tsx", ".ts", ".js"}
    for hit in util.grep(root, catalog.PLACEHOLDER_PATTERN, text_exts)[:12]:
        yield Finding(
            rule_id="XPLAT-PLACEHOLDER",
            severity="HIGH",
            store=BOTH,
            guideline="Apple 2.3.1 / Play XIII Deceptive Behavior",
            title="Placeholder text in shipped content",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence=hit[2],
            impact="Placeholder content is an explicit incompleteness rejection under Apple 2.1 "
                   "and 2.3.1.",
            fix="Replace with final copy. Check every localization, not just the default one.",
            auto_fixable=True,
        )

    for hit in util.grep(root, catalog.STAGING_PATTERN)[:10]:
        relpath = util.rel(hit[0], root).lower()
        if "test" in relpath or "spec" in relpath or "mock" in relpath:
            continue  # fixtures and test doubles may legitimately name staging hosts
        yield Finding(
            rule_id="XPLAT-STAGING-URL",
            severity="HIGH",
            store=BOTH,
            guideline="Apple 2.1 App Completeness",
            title="Non-production endpoint referenced in shipped code",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence=hit[2],
            impact="If the release build reaches a staging host, the reviewer sees a broken or "
                   "unreachable backend — the most common 2.1 rejection.",
            fix="Move the endpoint behind a build-type/scheme configuration and confirm the "
                "release variant points at production. Verify the production backend is "
                "reachable without a VPN, IP allowlist, or geofence during review.",
            auto_fixable=False,
        )

    for label, pattern in catalog.SECRET_PATTERNS.items():
        for hit in util.grep(root, pattern, None, 0)[:3]:
            yield Finding(
                rule_id="XPLAT-SECRET",
                severity="HIGH",
                store=BOTH,
                guideline="Play security scan / Apple 1.6 Data Security",
                title=f"Possible {label} committed in the source tree",
                file=util.rel(hit[0], root),
                line=hit[1],
                evidence=hit[2][:120],
                impact="Play's automated scan blocks releases containing known secret formats, "
                       "and anything in the binary is extractable.",
                fix="Rotate the credential, move it server-side or into a secrets manager, and "
                    "purge it from git history.",
                auto_fixable=False,
                confidence="medium",
            )

    integ = _sig(proj, "integrity_gate")
    if integ:
        hit = integ[0]
        yield Finding(
            rule_id="XPLAT-INTEGRITY-GATE",
            severity="HIGH",
            store=BOTH,
            guideline="Apple 2.1 / Play pre-launch report",
            title="Root/jailbreak/emulator/integrity gating detected",
            file=util.rel(hit[0], root),
            line=hit[1],
            evidence=f"{util.rel(hit[0], root)}:{hit[1]}: {hit[2]}",
            impact="These checks routinely block Google's pre-launch report devices and Apple's "
                   "review lab devices, producing an inexplicable 'app doesn't work' rejection.",
            fix="Make the check degrade gracefully (warn, don't block), or provide a documented "
                "bypass for review and state it in Notes for Review / App access instructions.",
            auto_fixable=False,
            confidence="medium",
        )

    if _has(proj, "webview_shell"):
        native_signals = sum(
            1 for key in ("iap", "ugc", "att", "accounts")
            if _has(proj, key)
        )
        source_files = len(list(util.walk(root, {".swift", ".kt", ".java", ".dart", ".tsx", ".ts"})))
        if native_signals <= 1 and source_files < 40:
            hit = _sig(proj, "webview_shell")[0]
            yield Finding(
                rule_id="XPLAT-4.2-WEBVIEW",
                severity="HIGH",
                store=BOTH,
                guideline="Apple 4.2 Minimum Functionality / Play XV Spam and Minimum Functionality",
                title="App appears to be a WebView wrapper with little native functionality",
                file=util.rel(hit[0], root),
                line=hit[1],
                evidence=f"WebView usage at {util.rel(hit[0], root)}:{hit[1]}; only "
                         f"{source_files} native source files and {native_signals} native "
                         f"capability signals detected",
                impact="A repackaged website is the canonical 4.2 rejection, and Apple tightened "
                       "4.3(b) against low-effort apps in June 2026.",
                fix="Add functionality a website cannot provide: offline access, push, widgets, "
                    "Shortcuts/App Intents, share extensions, background sync, native navigation, "
                    "or a local data layer. This is a product change, not a config change — "
                    "review it with the team before submitting.",
                auto_fixable=False,
                confidence="low",
            )


# --------------------------------------------------------------------------
def _dep(proj, token: str) -> bool:
    for path in filter(None, [proj.podfile_lock, proj.package_json, proj.pubspec]):
        if token.lower() in util.read_text(path).lower():
            return True
    for g in proj.gradle_files:
        if token.lower() in util.read_text(g).lower():
            return True
    return False


def _sdk_inventory(proj):
    """Report the data-collecting SDKs found, so the user can reconcile declarations."""
    found = []
    for token, (name, types, tracking) in catalog.SDK_DATA_MAP.items():
        if _dep(proj, token):
            found.append((name, types, tracking))
    if not found:
        return
    seen = {}
    for name, types, tracking in found:
        seen.setdefault(name, (types, tracking))
    lines = [
        f"- {name}: {', '.join(types)}" + ("  [TRACKING]" if tracking else "")
        for name, (types, tracking) in sorted(seen.items())
    ]
    yield Finding(
        rule_id="XPLAT-SDK-INVENTORY",
        severity="MEDIUM",
        store=BOTH,
        guideline="Apple 5.1.1 App Privacy / Play XI.D Data safety",
        title=f"{len(seen)} data-collecting SDKs detected — reconcile every declaration",
        file="",
        evidence="\n".join(lines),
        impact="Every one of these must appear in the App Privacy nutrition label, the privacy "
               "manifest, the Play Data safety form, and the privacy policy. A mismatch with "
               "observed traffic is the classic privacy rejection on both stores.",
        fix="Fill assets/data-safety-worksheet.md from this list, then verify each entry against "
            "the App Privacy label, PrivacyInfo.xcprivacy, the Data safety form, and the policy "
            "text. Any SDK marked [TRACKING] requires ATT on iOS and NSPrivacyTracking = true "
            "with its domains listed.",
        auto_fixable=False,
    )
