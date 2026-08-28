# Privacy & Data — The Cross-Platform Reconciliation Problem

Privacy is where most "surprise" rejections come from, because the failure isn't a bug —
it's a **disagreement between four artifacts that must all say the same thing**:

```
        ┌─────────────────────────┐
        │  1. What the code does  │  ← SDKs, network calls, permissions
        └───────────┬─────────────┘
                    │  must match
        ┌───────────┴─────────────┐
        │  2. In-app disclosure   │  ← purpose strings, prominent disclosure, consent UI
        └───────────┬─────────────┘
                    │  must match
        ┌───────────┴─────────────┐
        │  3. Store declarations  │  ← App Privacy label / Data safety form / manifests
        └───────────┬─────────────┘
                    │  must match
        ┌───────────┴─────────────┐
        │  4. The privacy policy  │  ← public URL, named third parties, retention, deletion
        └─────────────────────────┘
```

**The audit procedure is always the same: enumerate (1), then verify (2), (3), (4) each
cover it exactly — no more, no less.** Over-declaring is nearly as bad as under-declaring,
because it contradicts observable traffic.

---

## Step 1 — Enumerate what the code actually does

### Find every SDK

```bash
# iOS
cat Podfile.lock | sed -n '/^PODS:/,/^DEPENDENCIES:/p'
xcodebuild -showBuildSettings 2>/dev/null | grep -i FRAMEWORK_SEARCH
# SPM
cat *.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved

# Android
./gradlew :app:dependencies --configuration releaseRuntimeClasspath

# React Native / Expo
cat package.json | jq '.dependencies'

# Flutter
cat pubspec.lock
```

### Map each SDK to the data it collects

| SDK family | Collects | Declare as |
|---|---|---|
| Google Analytics / Firebase Analytics | App Set ID/AAID, usage, device info, IP | Analytics; Device or Other IDs; Product Interaction |
| Firebase Crashlytics | Crash logs, device, installation ID | Diagnostics / Crash Data |
| Google AdMob / Ad Manager | AAID/IDFA, coarse location, usage | Third-Party Advertising; **tracking = true** |
| Meta / Facebook SDK | IDFA/AAID, app events, user ID | Third-Party Advertising; **tracking = true** |
| AppsFlyer / Adjust / Branch / Singular | IDFA/AAID, IP, install referrer | Third-Party Advertising; **tracking = true** |
| Amplitude / Mixpanel / PostHog | Device ID, usage, user ID | Analytics |
| Sentry / Bugsnag / Datadog RUM | Crash + device + optional user | Diagnostics |
| RevenueCat / Adapty / Superwall | Purchase history, app user ID | Purchases |
| OneSignal / Braze / Iterable / CleverTap | Push token, device ID, user ID, behavior | Analytics + Product Personalization |
| Intercom / Zendesk / Freshchat | Email, name, messages | Contact Info; User Content |
| Stripe / Braintree / Adyen | Payment info (usually tokenized) | Financial Info |
| Google Maps / Mapbox | Location | Location (precise or coarse) |
| Any LLM API (OpenAI, Anthropic, Google, self-hosted) | **Whatever the user typed or uploaded** | User Content, shared with a third party — **requires explicit disclosure and consent** (Apple 5.1.2(i), Nov 2025; Play User Data ▸ AI clarification, July 2026) |

**The third-party AI clause is the newest and most-missed requirement on both stores.**
If you send user text, images, audio, or documents to a model you don't run, you must:
1. Name the practice in your privacy policy (and ideally the provider).
2. Disclose it in-app before the first send.
3. Declare the data type as collected **and shared**.
4. Not send more than the feature needs.

### Enumerate permissions actually requested

```bash
# Android — the MERGED manifest, not the source one
./gradlew :app:processReleaseManifest && \
  grep -o 'android:name="android\.permission\.[^"]*"' \
  app/build/intermediates/merged_manifest/release/AndroidManifest.xml | sort -u

# iOS — the BUILT Info.plist
plutil -p "$(find . -name '*.app' -maxdepth 4 | head -1)/Info.plist" | grep UsageDescription
```

Anything in that list that you can't tie to a user-visible feature must be **removed**, not
justified.

---

## Step 2 — In-app disclosure

### Apple: purpose strings (5.1.1(ii))
Every `NS*UsageDescription` must name the feature and the benefit. Reviewers read these.
Localize them via `InfoPlist.strings` for every shipped locale.

**Template:** `"{App} uses {resource} to {specific user-facing outcome}."`

### Apple: App Tracking Transparency (5.1.2(i))
Required before you read the IDFA or link user/device data with third-party data for
advertising or measurement.

```swift
import AppTrackingTransparency
// Only after the app is in .active state, and after a context screen if you use one.
ATTrackingManager.requestTrackingAuthorization { status in
    // Only initialize ad/attribution SDKs with IDFA if .authorized
}
```

Requirements the scanner checks:
- `NSUserTrackingUsageDescription` present and specific.
- ATT is requested **before** any attribution/ad SDK initializes with IDFA.
- Denial is honored — no fallback fingerprinting (IP + device model + boot time + storage
  size composites are explicitly treated as tracking).
- No incentive for granting ATT (no "allow tracking for 100 coins") — that's 5.1.2(i).
- Privacy manifest `NSPrivacyTracking = true` with all `NSPrivacyTrackingDomains` listed.

### Google: Prominent Disclosure & Consent
A **separate in-app screen** shown **before** the runtime permission dialog, that:
- Names the data ("your location", "your contacts").
- States what it's used for, in the app's own words.
- Makes clear it's this app collecting it.
- Requires an affirmative tap ("Accept"/"Allow"). A "Got it" that auto-dismisses does not
  count. A toast does not count.

Required whenever the collection isn't obvious from the UI context — background location,
contacts, SMS, call log, background microphone/camera, accessibility service, installed-app
list, and anything sent to a third party.

**Play reviewers ask for a video demonstrating this flow** for background location. Record
it before you submit.

---

## Step 3 — Store declarations

### Apple: App Privacy "nutrition label" (App Store Connect ▸ App Privacy)
For each data type: collected? linked to identity? used for tracking? purposes?

Data categories: Contact Info · Health & Fitness · Financial Info · Location · Sensitive
Info · Contacts · User Content · Browsing History · Search History · Identifiers · Purchases
· Usage Data · Diagnostics · Surroundings · Body · Other Data.

Must match `NSPrivacyCollectedDataTypes` in the privacy manifest **and** the SDKs' own
manifests, which Xcode aggregates. Generate the report before submitting:
**Product ▸ Archive ▸ (select archive) ▸ Generate Privacy Report**.

### Google: Data safety form (Play Console ▸ App content ▸ Data safety)
For each of ~40 data types you declare: collected / shared / ephemeral / required or
optional / purposes. You also declare:
- Whether data is encrypted in transit.
- Whether users can request deletion.
- **The account-deletion web URL.**
- Whether you follow the Families policy.
- Independent security review (optional badge).

Play cross-checks this against automated network analysis. An undeclared analytics endpoint
is a common suspension.

### Both: the privacy policy
One policy can serve both stores, but it must:
- Live at a stable **HTTPS URL** (not a PDF, not a Google Doc, not editable by visitors).
- Name the developer/company entity.
- List **every** category of data collected, why, and with whom it's shared —
  **naming the third parties or at least their categories, including AI providers**.
- Explain retention periods and deletion.
- Give a working contact method for deletion requests.
- Cover children's data if applicable.
- Be linked **inside the app** (Settings/About) *and* in both stores' metadata.

---

## Step 4 — Account deletion (both stores, both mandatory)

| Requirement | Apple 5.1.1(v) | Google Play XI.F |
|---|---|---|
| In-app deletion path | **Required** | **Required** |
| Web deletion URL | Not required | **Required**, declared in Console |
| Must delete all account data | Yes | Yes — "not merely freeze" |
| May offer "deactivate" | Only *in addition to* delete | Only *in addition to* delete |
| Legal retention | Allowed, must be disclosed | Allowed, must be disclosed |

**Implementation checklist:**
- Reachable in ≤ 3 taps from the main settings screen, labelled "Delete Account".
- Does not require emailing support, calling, or filling a web form *instead of* the in-app
  flow.
- Confirms, then actually deletes server-side (or schedules with a stated window).
- If the account is shared/team-owned, explain the path clearly.
- The web URL works without the app installed and without being logged into the app.

---

## Step 5 — Region-specific overlays

| Regime | Trigger | Requirement |
|---|---|---|
| **GDPR / UK GDPR** | Any EU/UK user | Lawful basis, consent for non-essential tracking (a **CMP** for ads), DSAR handling, DPO/representative if applicable, breach notification |
| **EU DSA** | EU distribution | **Trader status** declared in App Store Connect and Play Console. Missing → removed from EU storefronts |
| **EU DMA** | Gatekeeper-adjacent features | Alternative browser engines/marketplaces need entitlements |
| **COPPA** | US users under 13 | Verifiable parental consent, no behavioral ads, data minimization |
| **CCPA/CPRA** | California | "Do Not Sell or Share My Personal Information", opt-out link, disclosure of sale/share |
| **HIPAA** | US covered entities | BAA with vendors; **do not put PHI in iCloud** (Apple 5.1.3(ii)) |
| **India DPDP Act** | Indian users | Consent notice, data-principal rights, children's data restrictions |
| **Brazil LGPD** | Brazilian users | Similar to GDPR |
| **China** | Chinese storefront | ICP filing/licence required; separate content review; PIPL compliance |
| **Korea** | Korean storefront | Alternative payment allowances; local privacy law |
| **VPN apps** | Any | Apple 5.4 requires an **organization** account; no data sale, ever |
| **Kids Category / Families** | Child audience | See `content-ugc-ai-kids.md` |

---

## Common privacy rejection patterns and their fixes

| Pattern | Guideline | Fix |
|---|---|---|
| Sign-up wall on launch for an app with no account-based features | Apple 5.1.1(v) | Let users browse first; gate sign-in at the moment an account is genuinely needed |
| "Delete account" only via email to support | Apple 5.1.1(v), Play XI.F | Build the in-app flow |
| Privacy policy URL 404s or is a PDF | Apple 5.1.1(i), Play XI.E | Host an HTML page at a stable URL |
| Nutrition label says "no data collected" but Firebase Analytics is linked | Apple 5.1.1 | Declare Analytics + Identifiers |
| ATT prompt shown but IDFA read regardless of the answer | Apple 5.1.2(i) | Gate the read on `.authorized` |
| Background location requested at first launch with no context | Play XII, Apple 5.1.5 | Request When-In-Use first; upgrade in-context with prominent disclosure |
| Contacts uploaded for "friend finding" without disclosure | Apple 5.1.2(iv)(v), Play XI.C | Use the picker; disclose; never bulk-upload |
| User prompts sent to an LLM with no mention anywhere | Apple 5.1.2(i), Play IX/XI.A | Disclose in-app + policy + declarations; add consent |
| Permission requested at launch instead of at point of use | Apple 5.1.1(iv), Play XI.C | Request in context |
| Purpose string says "Required for app to work" | Apple 5.1.1(ii) | Rewrite naming the feature |
| App requires push permission to continue | Apple 4.5.4 / 5.1.2(i) | Make it skippable |

---

## Sources
- [App Review Guidelines §5.1 — Apple Developer](https://developer.apple.com/app-store/review/guidelines/#privacy)
- [Privacy manifest files — Apple Developer Documentation](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Developer Program Policy §XI Privacy, Deception and Device Abuse — Play Console Help](https://support.google.com/googleplay/android-developer/answer/16944162?hl=en)
- [Policy announcement: July 15, 2026 — Play Console Help](https://support.google.com/googleplay/android-developer/answer/17134731?hl=en)
