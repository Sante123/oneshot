# Google Play — Pre-Submission Checklist

Tick every box or record a waiver with a written reason. Unticked = NO-GO.

Remember: Play enforcement is often **post-publication and account-level**. A violation
can cost a strike, and three strikes can terminate the account.

## Version floors (deadline **2026-08-31**, extension to 2026-11-01)
- [ ] `targetSdk` ≥ **36** (Android 16); `compileSdk` ≥ 36
- [ ] Behavior changes for the new API level re-tested: runtime permissions, scoped
      storage, foreground service types, exact alarms, `POST_NOTIFICATIONS`,
      `PendingIntent` mutability, predictive back
- [ ] **Play Billing Library ≥ 8.0.0** (if the app has IAP)
- [ ] `com.google.android.play.billingclient.version` present in the merged manifest
- [ ] All native `.so` files **16 KB aligned** (`p_align` ≥ 0x4000)
- [ ] `arm64-v8a` present
- [ ] `android:extractNativeLibs="false"` / `useLegacyPackaging = false`
- [ ] Published as an **AAB**, not an APK

## Merged manifest (`./gradlew :app:processReleaseManifest`)
- [ ] `android:debuggable` absent or false
- [ ] `android:usesCleartextTraffic` false (Network Security Config for exceptions)
- [ ] `android:allowBackup` false, or `dataExtractionRules` excludes credentials
- [ ] `android:exported` explicit on every component with an intent filter
- [ ] `android:foregroundServiceType` on every foreground service, each mapped to an
      approved use case
- [ ] **No location foreground service used for geofencing** (use the Geofence API)
- [ ] Every `<uses-permission>` maps to a shipped, user-visible feature
- [ ] `<queries>` used instead of `QUERY_ALL_PACKAGES` where possible
- [ ] No over-declared `<uses-feature android:required="true">`

## Restricted permissions — declaration required
- [ ] `ACCESS_BACKGROUND_LOCATION` — Location declaration + **demo video**, or removed
- [ ] `ACCESS_FINE_LOCATION` — justified, or downgraded to coarse / the location button
- [ ] `READ_SMS` / `RECEIVE_SMS` — default SMS handler, or replaced by SMS Retriever API
- [ ] `READ_CALL_LOG` — default dialer only; **not used for account verification**
- [ ] `MANAGE_EXTERNAL_STORAGE` — one of the six approved app types, declared
- [ ] `READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` — Photo Picker, or declared broad access
- [ ] `READ_CONTACTS` — Contact Picker, or declared (mandatory from Jan 2027)
- [ ] `QUERY_ALL_PACKAGES` — declared with an approved use case
- [ ] `BIND_ACCESSIBILITY_SERVICE` — genuine accessibility, disclosed in-app and in the
      listing
- [ ] `AD_ID` permission declared and the Advertising ID declaration completed
- [ ] `USE_EXACT_ALARM` only in an alarm clock / calendar app
- [ ] `REQUEST_INSTALL_PACKAGES`, `SYSTEM_ALERT_WINDOW`, `PACKAGE_USAGE_STATS` justified
- [ ] **Lending apps request none of**: contacts, storage, photos/video, precise
      location, call log

## Privacy & data
- [ ] **Prominent disclosure** screen shown **before** every non-obvious sensitive
      permission request, requiring an affirmative tap
- [ ] Privacy policy at a stable, public, non-PDF, non-editable HTTPS URL
- [ ] Privacy policy linked in Play Console **and** inside the app
- [ ] Privacy policy names every third party, **including AI providers**
- [ ] **Data safety form** complete, accurate, and matching every embedded SDK
- [ ] Data safety declares encryption in transit and deletion support truthfully
- [ ] **In-app account deletion** *and* a **web deletion URL** declared in Console
- [ ] Deletion removes all account data, not just deactivates
- [ ] App Set ID not used for ads or linked to PII
- [ ] Health Connect data treated as sensitive; declaration completed

## Content & policy
- [ ] UGC: moderation, in-app reporting, user blocking, ToS acceptance
- [ ] Social/dating apps: **Child Safety Standards** published, in-app CSAE reporting,
      safety contact declared
- [ ] AI content: **in-app report control in context**, reports inform filtering,
      moderation applied
- [ ] Families: accurate target-audience declaration, **Families-certified ad SDKs only**,
      no AAID from children, non-personalized ads
- [ ] No deceptive behavior: no fake system UI, no alarmist prompts, no hidden features
- [ ] No impersonation in name, icon, or developer name
- [ ] No incentivized installs, reviews, or rating manipulation
- [ ] Third-party IP cleared; no stream-ripping functionality
- [ ] Regulated categories (loans, crypto, gambling, health, news, government, VPN,
      prediction markets) declared with licence documentation attached

## Build & release config
- [ ] `minifyEnabled true` for release, **and the release variant smoke-tested**
      (R8 stripping reflection is the classic review-time crash)
- [ ] No staging/test endpoints in the release build type
- [ ] `google-services.json` points at the **production** Firebase project
- [ ] No API keys or secrets in the binary
- [ ] No known-vulnerable SDK versions (Play Console ▸ SDKs)
- [ ] Play App Signing enabled; upload key backed up
- [ ] `versionCode` increased
- [ ] **Play Integrity / root / emulator checks do not block Play's test devices**

## Play Console ▸ App content
- [ ] Privacy policy URL
- [ ] **App access** — working credentials and steps for every gated area
- [ ] Ads declaration
- [ ] **Content rating (IARC)** — unrated apps are not permitted
- [ ] **Target audience and content**
- [ ] Data safety (incl. account-deletion URL)
- [ ] Government apps declaration (if applicable)
- [ ] Financial features declaration (if applicable)
- [ ] Health apps declaration (if applicable)
- [ ] News app declaration (if applicable)
- [ ] Sensitive app permissions declarations
- [ ] Advertising ID declaration

## Store listing
- [ ] Title ≤ 30 chars; no emoji, promo text, or trademarks
- [ ] Short description ≤ 80 chars
- [ ] Full description ≤ 4,000 chars; no keyword stuffing or CTA spam
- [ ] Description discloses IAP, subscriptions, ads, account and hardware requirements
- [ ] Icon 512×512 PNG; no badges, ratings, price, or "Sale" flashes
- [ ] Feature graphic 1024×500; no device frames, cropped text, or fake buttons
- [ ] 2–8 screenshots; 16:9 or 9:16; sides 320–3840 px; long side ≤ 2× short side
- [ ] Screenshots depict the actual in-app experience and match the current build
- [ ] Tablet / Wear / TV screenshots if those form factors are supported
- [ ] Localizations genuinely translated (machine translation is a violation)

## Account & process
- [ ] **App registered in Play Console** (required since July 2026)
- [ ] **Developer verification complete** — identity, or D-U-N-S for organizations
      (enforcement in BR/ID/SG/TH from **2026-09-30**; D-U-N-S can take 28 days)
- [ ] New personal account: **12 testers opted in for 14 continuous days**, production
      access granted
- [ ] Ownership transfers done via the Console "Transfer ownership" workflow
- [ ] **Pre-launch report clean** — zero crashes/ANRs; accessibility and security items
      addressed
- [ ] Android vitals within thresholds for live apps (crash < 1.09%, ANR < 0.47%)
- [ ] Staged rollout configured
