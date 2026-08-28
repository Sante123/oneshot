# Data Declaration Worksheet

One row per data type. Fill it from the **SDK inventory** the scanner produced
(`XPLAT-SDK-INVENTORY`) plus your own first-party collection. Then copy each column into
the matching store form.

**Rule: every row must be true in all five columns.** If a row is declared in one place
and not another, that is the privacy rejection.

---

## 1. Inventory — what actually leaves the device

| # | Data | Collected by (SDK / our code) | Sent to (host) | Linked to identity? | Tracking? | Purpose(s) | Required or optional |
|---|---|---|---|---|---|---|---|
| 1 | Email address | our API | api.example.com | yes | no | App Functionality, Account Management | Required |
| 2 | Device ID | Firebase Analytics | firebase-settings.crashlytics.com | yes | no | Analytics | Optional |
| 3 | IDFA / AAID | AdMob | googleads.g.doubleclick.net | yes | **yes** | Third-Party Advertising | Optional |
| 4 | Crash logs | Crashlytics | crashlytics.com | no | no | Diagnostics | Required |
| 5 | User content (prompts) | our code → OpenAI | api.openai.com | yes | no | App Functionality | Required for the AI feature |
| … | | | | | | | |

> Anything you cannot trace to a row here must be **removed**, not declared.

---

## 2. Apple — App Privacy nutrition label

For each row above, tick the Apple category and answer three questions.

| Apple category | Used? | Linked to the user? | Used for tracking? | Purposes |
|---|---|---|---|---|
| Contact Info (name, email, phone, address) | | | | |
| Health & Fitness | | | | |
| Financial Info (payment, credit, other) | | | | |
| Location (precise, coarse) | | | | |
| Sensitive Info | | | | |
| Contacts | | | | |
| User Content (photos, audio, gameplay, messages, other) | | | | |
| Browsing History | | | | |
| Search History | | | | |
| Identifiers (user ID, device ID) | | | | |
| Purchases | | | | |
| Usage Data (product interaction, ad data, other) | | | | |
| Diagnostics (crash, performance, other) | | | | |
| Surroundings / Body | | | | |
| Other Data | | | | |

Apple purposes: `Third-Party Advertising`, `Developer's Advertising or Marketing`,
`Analytics`, `Product Personalization`, `App Functionality`, `Other Purposes`.

---

## 3. Apple — `PrivacyInfo.xcprivacy`

```xml
<key>NSPrivacyCollectedDataTypes</key>
<array>
  <dict>
    <key>NSPrivacyCollectedDataType</key>
    <string>NSPrivacyCollectedDataTypeEmailAddress</string>
    <key>NSPrivacyCollectedDataTypeLinked</key><true/>
    <key>NSPrivacyCollectedDataTypeTracking</key><false/>
    <key>NSPrivacyCollectedDataTypePurposes</key>
    <array><string>NSPrivacyCollectedDataTypePurposeAppFunctionality</string></array>
  </dict>
</array>
<key>NSPrivacyTracking</key><true/>
<key>NSPrivacyTrackingDomains</key>
<array>
  <string>googleads.g.doubleclick.net</string>
</array>
```

- [ ] Every row above with `Tracking = yes` appears in `NSPrivacyTrackingDomains`
- [ ] `NSPrivacyTracking` is `true` if any row tracks
- [ ] Xcode's privacy report (Archive ▸ Generate Privacy Report) matches this table

---

## 4. Google Play — Data safety form

For each row: *Collected* and/or *Shared*, *Processed ephemerally*,
*Required or optional*, and purposes.

| Play category | Data type | Collected | Shared | Ephemeral | Required | Purposes |
|---|---|---|---|---|---|---|
| Personal info | Name / Email / User IDs / Address / Phone | | | | | |
| Financial info | Payment info / Purchase history / Credit score | | | | | |
| Location | Approximate / Precise | | | | | |
| Health and fitness | Health info / Fitness info | | | | | |
| Messages | Emails / SMS / Other in-app messages | | | | | |
| Photos and videos | | | | | | |
| Audio files | Voice/sound recordings / Music files | | | | | |
| Files and docs | | | | | | |
| Calendar / Contacts | | | | | | |
| App activity | Interactions / Search history / Installed apps / Other actions | | | | | |
| Web browsing | | | | | | |
| App info and performance | Crash logs / Diagnostics / Other | | | | | |
| Device or other IDs | | | | | | |

Play purposes: `App functionality`, `Analytics`, `Developer communications`,
`Advertising or marketing`, `Fraud prevention/security/compliance`,
`Personalization`, `Account management`.

Also answer:
- [ ] Is all data **encrypted in transit**? (Must be true — check
      `usesCleartextTraffic` and ATS)
- [ ] Can users **request data deletion**? → **Account deletion URL:**
      `https://______________________`
- [ ] Does the app follow the **Families policy**?
- [ ] Independent security review? (optional badge)

---

## 5. Privacy policy — required sections

- [ ] Who we are (legal entity name, address, contact)
- [ ] What we collect — **every row in §1**
- [ ] Why we collect it (purposes, matching the tables above)
- [ ] Legal basis (GDPR) / notice at collection (CCPA)
- [ ] Who we share it with — **named third parties, including AI providers**
- [ ] International transfers
- [ ] How long we keep it, and how we delete it
- [ ] How users request deletion, and the **in-app path + web URL**
- [ ] Children's data
- [ ] Cookies / SDK identifiers
- [ ] User rights (access, correction, deletion, portability, objection)
- [ ] How we notify users of policy changes
- [ ] Effective date

---

## Sign-off

- [ ] §1 verified against the merged manifest, the built Info.plist, and the SDK list
- [ ] §2 entered in App Store Connect
- [ ] §3 committed in `PrivacyInfo.xcprivacy` and matches the Xcode privacy report
- [ ] §4 entered in Play Console
- [ ] §5 published and linked in-app and in both listings
- [ ] Network traffic captured on a real run and compared to §1 (Charles/mitmproxy)

Verified by: ______________________  Date: ____________
