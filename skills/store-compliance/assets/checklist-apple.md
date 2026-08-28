# Apple App Store — Pre-Submission Checklist

Tick every box or record a waiver with a written reason. Unticked = NO-GO.

## Build & binary
- [ ] Built with **Xcode 26+ / iOS 26 SDK** (`DTSDKName` reads `iphoneos26.x`)
- [ ] `CFBundleShortVersionString` and `CFBundleVersion` both increased
- [ ] Distribution signing; `get-task-allow` = false
- [ ] No `UIWebView` anywhere, including dependencies
- [ ] No private API selectors in source or vendored SDKs
- [ ] App icon 1024×1024 PNG, **no alpha channel**, no baked rounded corners
- [ ] Launch screen configured (storyboard) so the app scales correctly
- [ ] dSYMs uploaded
- [ ] Release build smoke-tested from a clean install on a **physical device**
- [ ] Works on the oldest supported OS **and** the newest
- [ ] Works on an **IPv6-only / NAT64** network
- [ ] No crash on launch, no crash on backgrounding, no crash on low memory

## Info.plist
- [ ] A specific `NS*UsageDescription` for **every** protected resource used
- [ ] Purpose strings name the feature and the benefit (not "required for the app")
- [ ] Purpose strings localized in `InfoPlist.strings` for every shipped locale
- [ ] `ITSAppUsesNonExemptEncryption` set
- [ ] `UIBackgroundModes` contains **only** modes the app actually uses
- [ ] No blanket `NSAllowsArbitraryLoads`
- [ ] `LSApplicationQueriesSchemes` contains only schemes you open
- [ ] `CFBundleDisplayName` matches the App Store name
- [ ] `CFBundleLocalizations` matches the declared localizations

## Privacy manifest & entitlements
- [ ] `PrivacyInfo.xcprivacy` present in the app target and every extension/framework
- [ ] Every Required Reason API declared with a **valid** reason code
- [ ] `NSPrivacyTracking` / `NSPrivacyTrackingDomains` correct and complete
- [ ] `NSPrivacyCollectedDataTypes` matches the App Privacy nutrition label
- [ ] Every linked third-party SDK ships its own manifest + signature (no `ITMS-91061`)
- [ ] Xcode privacy report generated from the archive and compared to the label
- [ ] Every entitlement is exercised by shipping code (no orphans — 2.5.4)
- [ ] Associated domains: `apple-app-site-association` live, JSON, no redirect

## Privacy & accounts
- [ ] Privacy policy at a stable HTTPS URL (HTML, not a PDF), reachable
- [ ] Privacy policy linked **inside the app**
- [ ] Privacy policy names every third party, **including AI providers**
- [ ] **In-app account deletion**, ≤ 3 taps from settings, actually deletes
- [ ] App usable without a login if it has no account-based features (5.1.1(v))
- [ ] Every permission requested **in context**, not at launch
- [ ] Every permission can be **denied** and the app still works
- [ ] ATT implemented if anything tracks; denial honored; no fingerprinting fallback
- [ ] No incentive offered for granting ATT, push, or location
- [ ] Third-party AI disclosed and consented before any user data is sent
- [ ] Health data not written to iCloud; no health data to advertisers

## Monetization
- [ ] Every purchasable item classified correctly (IAP vs. external — 3.1.1/3.1.3)
- [ ] Physical goods and real-world services do **not** use StoreKit
- [ ] Paywall shows title, period, what's provided, price, renewal statement
- [ ] Free-trial terms show the **post-trial price**
- [ ] Tappable **Terms of Use** and **Privacy Policy** links on the paywall
- [ ] **Restore Purchases** present and working **while signed out**
- [ ] `Transaction.updates` listener started at launch (promoted IAP works)
- [ ] All transactions finished; `.pending` (Ask to Buy) handled
- [ ] All IAPs **Ready to Submit** and attached to this version
- [ ] Prices set in every storefront the app ships to
- [ ] Credits/currency do not expire; loot-box odds published
- [ ] Ads only in the main binary; dismissible; reportable; ATT-gated

## Content & design
- [ ] More than a repackaged website (4.2)
- [ ] Meaningfully different from what already exists (4.3(b))
- [ ] No placeholder text anywhere, in any locale
- [ ] No beta/trial/demo language in a production listing
- [ ] UGC: filtering, reporting, blocking, published contact info — all four (1.2)
- [ ] UGC: 24-hour takedown commitment documented
- [ ] AI features moderated; report control on each response
- [ ] Sign in with Apple (or equivalent) offered alongside social login (4.8)
- [ ] No custom or incentivized review prompts (5.6.1)
- [ ] Third-party IP cleared; no media downloading from third-party sources (5.2.3)
- [ ] Dark mode and Dynamic Type correct on every screen
- [ ] iPad layout and multitasking correct if iPad is supported

## App Store Connect
- [ ] **Updated age-rating questionnaire answered** (mandatory since 2026-01-31)
- [ ] Age rating accounts for what any AI feature can produce
- [ ] App Privacy nutrition label complete and consistent
- [ ] Privacy Policy URL entered
- [ ] **Terms of Use (EULA) URL** entered (required for subscriptions)
- [ ] Support URL live and useful
- [ ] Copyright field filled
- [ ] Primary (and secondary) category correct
- [ ] Content rights declaration answered
- [ ] Export compliance answered
- [ ] **EU DSA trader status** submitted (required for EU storefronts)
- [ ] Accessibility Nutrition Label declares only what the app truly supports
- [ ] App name ≤ 30 chars, no trademarks, no pricing, no keyword stuffing
- [ ] Subtitle ≤ 30 chars, no unverifiable claims
- [ ] Keywords ≤ 100 chars, relevant, no competitor names
- [ ] Description discloses IAP, subscriptions, ads, account and hardware requirements
- [ ] "What's New" describes the actual changes
- [ ] Screenshots show the app **in use**, match the current build, are 4+ appropriate
- [ ] Screenshots present for iPhone 6.9" and iPad 13" (if iPad supported), per locale
- [ ] No other-platform imagery or references
- [ ] Pricing and availability set

## App Review Information
- [ ] **Demo account** — live, tested from a fresh device, **2FA disabled**, no expiry
- [ ] Demo account has premium entitlement if needed to see paid features
- [ ] Backend is production, reachable, and will stay up through the weekend
- [ ] **Notes for Review** filled with the real navigation path to every feature,
      permission, paywall, deletion flow, and UGC control
- [ ] New features described **specifically** (generic descriptions are rejected)
- [ ] Attachments: demo video for anything non-obvious; licence documents for
      regulated categories
- [ ] Contact name, email, and phone with country code, monitored during review
- [ ] Not submitting on a Friday or before a holiday
- [ ] Phased release enabled
