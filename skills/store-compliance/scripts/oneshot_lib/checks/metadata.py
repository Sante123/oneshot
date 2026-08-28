"""Store listing metadata and asset checks."""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path

from .. import util
from ..model import APPLE, BOTH, Finding, FindingList, PLAY

BANNED_NAME_TOKENS = [
    "free", "sale", "off", "best", "#1", "no.1", "top ", "new!", "download",
    "cheap", "discount", "premium free", "unlimited free",
]
TRADEMARKS = [
    "whatsapp", "instagram", "facebook", "tiktok", "youtube", "netflix", "spotify",
    "chatgpt", "openai", "google", "apple", "android", "iphone", "ios", "play store",
    "app store", "snapchat", "twitter", " x ", "telegram", "discord", "roblox",
    "minecraft", "pinterest", "linkedin", "amazon", "disney",
]


def check(proj) -> FindingList:
    out = FindingList()
    out.extend_from(_listing_text(proj))
    out.extend_from(_icons(proj))
    out.extend_from(_screenshots(proj))
    out.extend_from(_declarations_reminder(proj))
    return out


def _listing_sources(proj):
    """Yield (label, store, path, text) for every listing field we can find."""
    root = proj.root
    for d in proj.metadata_dirs:
        android = "android" in str(d).replace("\\", "/")
        store = PLAY if android else APPLE
        for name, label in (
            ("name.txt", "name"), ("title.txt", "name"),
            ("subtitle.txt", "subtitle"),
            ("short_description.txt", "short_description"),
            ("description.txt", "description"),
            ("full_description.txt", "description"),
            ("keywords.txt", "keywords"),
            ("release_notes.txt", "release_notes"),
            ("promotional_text.txt", "promotional_text"),
        ):
            for p in d.rglob(name):
                yield label, store, p, util.read_text(p).strip()

    if proj.expo_config and proj.expo_config.suffix == ".json":
        try:
            data = json.loads(util.read_text(proj.expo_config) or "{}")
        except json.JSONDecodeError:
            data = {}
        expo = data.get("expo", data)
        if isinstance(expo, dict):
            if expo.get("name"):
                yield "name", BOTH, proj.expo_config, str(expo["name"])
            if expo.get("description"):
                yield "description", BOTH, proj.expo_config, str(expo["description"])


def _trim(text: str, limit: int) -> str:
    """Trim to the limit at a word boundary, so the suggestion reads as real copy."""
    if len(text) <= limit:
        return text
    cut = text[:limit].rstrip()
    if " " in cut and len(cut) - cut.rfind(" ") < 15:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip(" -,&|:;")


LIMITS = {
    ("name", APPLE): 30, ("name", PLAY): 30, ("name", BOTH): 30,
    ("subtitle", APPLE): 30,
    ("short_description", PLAY): 80,
    ("description", APPLE): 4000, ("description", PLAY): 4000, ("description", BOTH): 4000,
    ("keywords", APPLE): 100,
    ("release_notes", PLAY): 500, ("release_notes", APPLE): 4000,
    ("promotional_text", APPLE): 170,
}


def _listing_text(proj):
    root = proj.root
    sources = list(_listing_sources(proj))
    if not sources:
        yield Finding(
            rule_id="META-NO-LISTING",
            severity="INFO",
            store=BOTH,
            guideline="Audit coverage",
            title="No store listing files found — listing not audited",
            file="",
            evidence="Looked for fastlane/metadata, store/, listing/, .appstore/, app.json",
            impact="Name length, keyword rules, description disclosures, and screenshot specs "
                   "could not be checked.",
            fix="Put the listing under fastlane/metadata (Apple) and "
                "fastlane/metadata/android (Play), or paste the current listing so it can be "
                "reviewed against references/metadata-and-assets.md.",
            auto_fixable=False,
        )
        return

    for label, store, path, text in sources:
        rel = util.rel(path, root)
        if not text:
            continue
        limit = LIMITS.get((label, store)) or LIMITS.get((label, BOTH))
        if limit and len(text) > limit:
            yield Finding(
                rule_id=f"META-LEN-{label.upper()}",
                severity="BLOCKER" if label in ("name", "subtitle", "short_description") else "HIGH",
                store=store,
                guideline="Apple 2.3.7 / Play XIV Store Listing",
                title=f"{label.replace('_', ' ')} is {len(text)} characters; the limit is {limit}",
                file=rel,
                line=1,
                evidence=text[:120] + ("…" if len(text) > 120 else ""),
                impact="Rejected at metadata review, or silently truncated in the listing.",
                fix=f"Trim to {limit} characters.",
                suggested_value=_trim(text, limit),
                auto_fixable=False,
            )

        low = text.lower()
        if label in ("name", "subtitle"):
            for token in BANNED_NAME_TOKENS:
                if token in low:
                    yield Finding(
                        rule_id="META-NAME-PROMO",
                        severity="BLOCKER",
                        store=store,
                        guideline="Apple 2.3.7 / Play XIV",
                        title=f"Promotional or pricing language in the {label}: '{token.strip()}'",
                        file=rel, line=1, evidence=text[:120],
                        impact="Pricing and promotional terms are prohibited in the app name.",
                        fix="Remove the promotional language; use a brand-first name.",
                        auto_fixable=False,
                    )
                    break
            for tm in TRADEMARKS:
                if tm in low:
                    yield Finding(
                        rule_id="META-NAME-TRADEMARK",
                        severity="BLOCKER",
                        store=store,
                        guideline="Apple 5.2.1 / Play X.C Trademark Infringement",
                        title=f"Third-party trademark in the {label}: '{tm.strip()}'",
                        file=rel, line=1, evidence=text[:120],
                        impact="Using another company's mark in the name is a rejection unless "
                               "you hold a licence.",
                        fix="Remove the mark. If you are licensed, keep the documentation ready "
                            "to attach to the submission.",
                        auto_fixable=False,
                        confidence="medium",
                    )
                    break
            if label == "name" and text.count(" - ") + text.count(",") >= 2:
                yield Finding(
                    rule_id="META-NAME-STUFFING",
                    severity="HIGH",
                    store=store,
                    guideline="Apple 2.3.7 / Play XIV",
                    title="App name looks keyword-stuffed",
                    file=rel, line=1, evidence=text[:120],
                    impact="Keyword stuffing in the name is explicitly prohibited.",
                    fix="Use a brand-first name and move feature terms into the keyword field "
                        "(Apple) or the description (Play).",
                    auto_fixable=False,
                    confidence="medium",
                )
            if re.search(r"for kids|for children", low):
                yield Finding(
                    rule_id="META-NAME-KIDS",
                    severity="HIGH",
                    store=APPLE,
                    guideline="Apple 2.3.8 / 5.1.4(b)",
                    title="'For Kids'/'For Children' is reserved for the Kids Category",
                    file=rel, line=1, evidence=text[:120],
                    impact="Apps outside the Kids Category must not imply a child audience.",
                    fix="Remove the phrase, or enter the Kids Category and meet all of "
                        "guideline 1.3 and 5.1.4.",
                    auto_fixable=False,
                )

        if label == "description":
            iap = util.any_match(root, r"StoreKit|BillingClient|RevenueCat|in_app_purchase")
            if iap and not re.search(r"(?i)in-?app purchase|subscription|subscribe|premium|upgrade", text):
                yield Finding(
                    rule_id="META-DESC-IAP",
                    severity="HIGH",
                    store=BOTH,
                    guideline="Apple 2.3.2",
                    title="Description does not disclose in-app purchases",
                    file=rel, line=1,
                    evidence="IAP code detected; no purchase/subscription language in the description",
                    impact="IAP features, levels, and subscriptions must be clearly indicated in "
                           "the description, screenshots, and previews.",
                    fix="Add an explicit line, e.g. 'Some features require a subscription. "
                        "<Plan> is $X/month or $Y/year.'",
                    auto_fixable=True,
                )
            if re.search(r"(?i)\b(android|google play|play store)\b", text) and store == APPLE:
                yield Finding(
                    rule_id="META-DESC-OTHERPLATFORM",
                    severity="HIGH",
                    store=APPLE,
                    guideline="Apple 2.3.10",
                    title="Description references another mobile platform",
                    file=rel, line=1, evidence=text[:160],
                    impact="Metadata must focus on the Apple platform; naming Android or Google "
                           "Play is a rejection.",
                    fix="Remove the reference.",
                    auto_fixable=True,
                )


def _png_size(path: Path):
    """Return (width, height, has_alpha) for a PNG without Pillow."""
    try:
        data = path.open("rb").read(64)
    except OSError:
        return None
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", data[16:24])
    color_type = data[25]
    return width, height, color_type in (4, 6)


def _icons(proj):
    root = proj.root
    for p in util.find_files(root, "*.png", limit=4000):
        name = p.name.lower()
        info = _png_size(p)
        if not info:
            continue
        w, h, alpha = info
        rel = util.rel(p, root)
        is_marketing = (w, h) == (1024, 1024) or "appicon" in name or "marketing" in name
        if is_marketing and (w, h) == (1024, 1024) and alpha:
            yield Finding(
                rule_id="APPLE-ICON-ALPHA",
                severity="BLOCKER",
                store=APPLE,
                guideline="Apple asset requirements / ITMS-90717",
                title="1024x1024 app icon has an alpha channel",
                file=rel,
                evidence=f"{w}x{h}, color type includes alpha",
                impact="Upload fails with ITMS-90717.",
                fix="Flatten the icon to opaque RGB (no transparency, no baked rounded corners). "
                    "`sips -g hasAlpha` must report 'no'.",
                auto_fixable=True,
            )
        if "feature" in name and "graphic" in name and (w, h) != (1024, 500):
            yield Finding(
                rule_id="PLAY-FEATUREGRAPHIC",
                severity="HIGH",
                store=PLAY,
                guideline="Play XIV Store Listing",
                title=f"Feature graphic is {w}x{h}; Play requires 1024x500",
                file=rel, evidence=f"{w}x{h}",
                impact="The listing cannot be published without a valid feature graphic.",
                fix="Export at exactly 1024x500 with no device frames, cropped text, fake "
                    "buttons, or store badges.",
                auto_fixable=False,
            )


def _screenshots(proj):
    root = proj.root
    shot_dirs = [d for d in util.find_files(root, "screenshots", limit=40) if d.is_dir()]
    for d in shot_dirs:
        android = "android" in str(d).replace("\\", "/")
        for p in list(d.rglob("*.png"))[:60]:
            info = _png_size(p)
            if not info:
                continue
            w, h, _ = info
            lo, hi = sorted((w, h))
            rel = util.rel(p, root)
            if android:
                if lo < 320 or hi > 3840 or hi > 2 * lo:
                    yield Finding(
                        rule_id="PLAY-SHOT-DIM",
                        severity="HIGH",
                        store=PLAY,
                        guideline="Play XIV Store Listing",
                        title=f"Screenshot {w}x{h} violates Play dimension rules",
                        file=rel, evidence=f"{w}x{h}",
                        impact="The listing cannot be published with out-of-spec screenshots.",
                        fix="Each side must be 320-3840 px and the long side no more than twice "
                            "the short side.",
                        auto_fixable=False,
                    )


def _declarations_reminder(proj):
    """Declarations live in the Console, not the repo — surface them as INFO tasks."""
    root = proj.root
    items = []
    if util.any_match(root, r"StoreKit|BillingClient|RevenueCat|in_app_purchase"):
        items.append("Terms of Use (EULA) URL in App Store Connect (required for subscriptions)")
    if util.any_match(root, r"GADBannerView|AdView|InterstitialAd|admob|AppLovin|IronSource"):
        items.append("Play 'Contains ads' declaration; Apple ad-related age-rating answers")
    if util.any_match(root, r"HealthKit|HealthConnect"):
        items.append("Play Health apps declaration; Apple health-data disclosures")
    if util.any_match(root, r"ACCESS_BACKGROUND_LOCATION|allowsBackgroundLocationUpdates"):
        items.append("Play Location permissions declaration + demo video")
    if util.any_match(root, r"\bloan\b|lending|APR"):
        items.append("Play Financial features declaration + country licensing documents")
    if util.any_match(root, r"web3|wallet_?connect|blockchain|erc20"):
        items.append("Play Financial features declaration (tokenized digital assets)")
    if util.any_match(root, r"NEVPNManager|VpnService"):
        items.append("Apple 5.4 organization account; Play VPN service declaration")

    items += [
        "Apple: updated age-rating questionnaire (mandatory since 2026-01-31)",
        "Apple: EU DSA trader status (required for EU storefronts)",
        "Play: IARC content rating (unrated apps are not permitted)",
        "Play: Target audience and content declaration",
        "Play: Data safety form, including the account-deletion URL",
        "Play: App access instructions with working credentials for gated features",
    ]
    yield Finding(
        rule_id="META-DECLARATIONS",
        severity="MEDIUM",
        store=BOTH,
        guideline="App Store Connect / Play Console App content",
        title=f"{len(items)} store declarations must be completed outside the repo",
        file="",
        evidence="\n".join(f"- {i}" for i in items),
        impact="Missing declarations block submission or cause a policy rejection even when the "
               "binary is perfect.",
        fix="Work through assets/checklist-apple.md and assets/checklist-play.md and tick every "
            "box before submitting.",
        auto_fixable=False,
    )
