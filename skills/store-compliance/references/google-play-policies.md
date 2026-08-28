# Google Play — Developer Program Policy Rejection Index

Authoritative sources:
<https://play.google/developer-content-policy/> · <https://support.google.com/googleplay/android-developer>
Policy version in force: **July 15, 2026**. Last verified: **2026-08-19**.

Google differs from Apple in one important way: **Play enforcement is often
post-publication and account-level.** A policy violation can mean app removal *and* a strike
against the developer account; three strikes can terminate the account permanently. Play
also runs pre-launch automated review plus human review for sensitive categories, and
"app rejected" and "app suspended" are separate outcomes with separate appeal paths.

---

## I. Restricted Content

### A. Child Endangerment — `BLOCKER` / account termination
No content that sexualizes minors, facilitates exploitation, grooming, sextortion, or
trafficking. No apps with excessive violence/gore that appeal to children.

### B. Child Safety Standards Policy — `BLOCKER` for social & dating apps
Social and dating apps **must**:
1. Publish written anti-CSAE (child sexual abuse & exploitation) standards.
2. Provide **in-app reporting** mechanisms for CSAE.
3. Address CSAM upon discovery.
4. Comply with applicable child-safety laws.
5. Designate a **safety point of contact** and declare it in Play Console.

Missing declaration → app rejected. This is checked in the Console form, not the binary.

### C. Inappropriate Content
- **Sexual Content and Profanity** — no pornography, no sexually gratifying content, no
  NCII. No escort services or "sugar dating".
- **Hate Speech** — no promotion of violence or hatred against protected groups.
- **Violence** — no gratuitous/realistic graphic violence; no promotion of self-harm or
  eating disorders.
- **Violent Extremism** — no terrorist content; no glorification or recruitment.
- **Sensitive Events** — no capitalizing on tragedies; no denial of well-documented tragic
  events.
- **Bullying and Harassment**.
- **Dangerous Products** — no facilitation of explosives, firearms, ammunition sales, or
  weapon-manufacturing instructions.
- **Marijuana** — no facilitation of marijuana sales, **regardless of local legality**.
  (Stricter than Apple.)
- **Tobacco and Alcohol** — no facilitation of nicotine product sales; no encouragement of
  illegal use. Narrow grocery-delivery exception with age-gating.

### II. Age-Restricted Content and Functionality
Apps facilitating **real-money gambling** or **matchmaking/dating** must block minors using
Play Console age-signal tools. **Unrated apps are not permitted on Google Play** (clarified
July 2026) — the IARC content-rating questionnaire is mandatory.

---

## III. Financial Services

- **Binary options** — prohibited outright.
- **Personal Loans**
  - Prohibited: loans requiring **repayment in full in 60 days or less**.
  - Must disclose: minimum and maximum repayment period, **maximum APR**, a representative
    total-cost example, and a full privacy policy.
  - **Must not request `READ_EXTERNAL_STORAGE` or `READ_CONTACTS`** (and by extension photo,
    video, contacts, precise-location, and call-log permissions). This is an automatic
    removal trigger for lending apps.
  - **US:** APR must be < 36%, calculated per the Truth in Lending Act.
  - **India:** RBI-licensed entities only. **Indonesia:** OJK licence. **Philippines:** SEC
    registration + Certificate of Authority. **Nigeria:** FCCPC approval. **Kenya:** CBK
    licence. **Pakistan:** one DLA per NBFC, SECP approval, no short-term loans.
    **Thailand:** BoT/MoF licence for ≥15%; a "non-regulated" statement below.
- **Earned Wage Access (EWA)** — allowed with automatic payroll repayment, advances limited
  to wages earned, fees of $1–$5 or 1–5%, and no credit-bureau reporting. Reframed to match
  financial-service standards in July 2026.

---

## IV. Real-Money Gambling, Games, and Contests

Licensed gambling apps are permitted only where the developer is an approved operator with
a **valid licence in the target country**, prevents under-18 use, geo-restricts, is a
**free download**, carries the **AO / highest** content rating, and displays responsible-
gambling information. Daily Fantasy Sports requires a separate DFS application. Gamified
loyalty programs and gambling advertising have their own sub-rules. NFT gamification cannot
accept money for a chance at an NFT of unknown value.

---

## V. Illegal Activities
No facilitation of illegal drug sales, minor drug/alcohol/tobacco use, or manufacturing
instructions.

---

## VI. User Generated Content — `BLOCKER` if controls are missing
Apps with UGC must implement:
1. Terms of service / user policy **acceptance**.
2. A definition of objectionable content and behavior.
3. **Active moderation** — in-app reporting *and* user blocking.
4. Safeguards around monetization of UGC.

**Incidental sexual content** requires a **two-action filter** to reach it, age screening,
and an accurate content-rating questionnaire.

---

## VII. Health Content and Services
- **Health apps declaration** must be completed in Play Console.
- Privacy policy linked in **Console and in-app**, with disclosure exceeding the Data
  safety section.
- Health functionality accuracy claims, external device compatibility, and **medical device
  self-declaration** required.
- Research apps need **IRB approval documentation**.
- **Health Connect data is personal & sensitive user data** subject to the User Data policy;
  Health Connect access requires a declaration and approved use case.
- No prescription-drug sales without a prescription; no unapproved substances (LegitScript
  list, ephedra, hCG weight-loss).
- **Health misinformation** — no claims contradicting medical consensus (vaccines, unproven
  treatments).
- **Google Play Billing may not be used for regulated clinical-service transactions.**

---

## VIII. Blockchain-Based Content
- Crypto exchanges and software wallets require certification and local regulatory
  compliance.
- **On-device cryptomining is banned**; remote mining *management* is allowed.
- Tokenized digital assets require the **Financial features declaration** and in-app product
  indication; **promoting earning potential is prohibited**.

---

## IX. AI-Generated Content — `HIGH`, actively enforced
Apps that generate AI content must:
1. Comply with all existing content policies (no restricted content generation).
2. Provide **in-app reporting/flagging** of offensive AI output, directly in the context
   where the content appears.
3. **Use those reports to inform filtering and moderation.**

Raw, unmoderated LLM or image-model output exposed to users is a current, common rejection.

---

## X. Intellectual Property
- Unauthorized copyrighted content (album art, movie stills, professional photos, soundboards
  of copyrighted audio).
- Encouraging infringement (stream-ripping / download-from-YouTube).
- **Trademark infringement** — names, icons, or branding likely to cause confusion.
- Counterfeit goods.

---

## XI. Privacy, Deception and Device Abuse — the biggest rejection surface

### A/B. User Data & Personal and Sensitive User Data — `BLOCKER`
- Be transparent about collection, handling, and sharing — **including data collected by
  third-party SDKs you embed.** You are responsible for your SDKs' behavior.
- Never access data beyond what the disclosed functionality requires.
- No public disclosure of financial or government-ID information.
- **No non-approved SDKs in child-directed apps** (Families ads/analytics certification).
- No linking persistent device identifiers to other personal data outside narrow telephony/
  enterprise purposes.

### C. Prominent Disclosure & Consent — `BLOCKER`
If your app accesses personal/sensitive data in a way that isn't obvious from the UI, you
must show an **in-app disclosure** — a dedicated screen or dialog, **not** just the privacy
policy and **not** the runtime permission dialog alone — **before** the permission request,
that states what data is accessed, how it's used, and that it's this app doing it. Consent
requires **affirmative user action**; auto-dismissing or expiring messages don't count.
This is the single most common Play rejection for apps using location, contacts, SMS,
call log, camera in the background, or accessibility services.

### D. Data safety section — `BLOCKER`
Declared collection/sharing must be **accurate, complete, current**, and consistent with
your privacy policy *and* your observed network traffic. Google runs automated traffic
analysis; an undeclared analytics or ad SDK is a common suspension cause. Must be
re-reviewed on every release that adds an SDK.

### E. Privacy Policy — `BLOCKER`
Must be at a **stable, publicly accessible, non-editable, non-PDF URL**, linked in Play
Console **and** inside the app. Must identify the developer/company, list all data accessed/
collected/used/shared, describe retention and deletion, and give a contact for deletion
requests.

### F. Account Deletion Requirement — `BLOCKER`
If your app allows account creation, you must provide:
1. An **in-app** account-deletion path, **and**
2. A **web-accessible** deletion request URL (declared in Play Console under App content ▸
   Data safety ▸ Account deletion) that works without installing the app.

Deletion must remove **all** data associated with the account, not just deactivate it. You
may retain data only where law requires; disclose it.

### G. App Set ID — must not be used for ad personalization or measurement, must not be
linked to PII or other device identifiers, and requires disclosure and valid consent.

### H. EU-US / UK / Swiss Data Privacy Frameworks — process EU personal data only for
consented purposes, implement security measures, notify Google if you can't comply.

---

## XII. Permissions and APIs that Access Sensitive Information

**Core rule: request the minimum scope, use the system picker, and declare anything
restricted.** Play Console's "App content ▸ Sensitive app permissions" declarations gate
publishing.

| Permission / API | Rule |
|---|---|
| **Photo & video** (`READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO`) | Use the **Android Photo Picker**. Broad access requires a declaration proving the app's *core* purpose is managing all photos/videos (gallery, backup). Effective for Android 13+ (API 33+) since **May 28, 2025**. A custom in-app picker does **not** qualify. |
| **Contacts** (`READ_CONTACTS`) | Use the **Android Contact Picker** (`Intent.ACTION_PICK_CONTACTS`). Broad access requires a declaration explaining why the picker is insufficient and which feature needs it. Permitted uses: contact management, dialer/SMS, call history, CRM, call screening, accessibility, personal assistants, friend matching, backup/restore, autocomplete, user-initiated selection. **Not** permitted: file sharing, collaboration invites, single-contact transactions. Announced April 2026; policy effective **January 2027 (Android 17+/API 37+)**. |
| **All files access** (`MANAGE_EXTERNAL_STORAGE`) | Only for file managers, backup/restore, anti-virus, document management, on-device search, disk/file encryption. Everything else must use Storage Access Framework or MediaStore. Declaration required. |
| **Background location** (`ACCESS_BACKGROUND_LOCATION`) | Requires a **Location permissions declaration** + a demo video showing the feature. Must be core to the feature, disclosed prominently, and unavailable via foreground-only. Most apps should simply remove it. |
| **Precise location** (`ACCESS_FINE_LOCATION`) | April 2026: the **location button** (`Settings.ACTION_...`/`FusedLocationProvider` one-shot) is the recommended minimum scope. Use `ACCESS_COARSE_LOCATION` unless precision is demonstrably required. |
| **SMS / Call Log** (`READ_SMS`, `RECEIVE_SMS`, `READ_CALL_LOG`, `WRITE_CALL_LOG`, `PROCESS_OUTGOING_CALLS`) | Only for apps whose registered core function is default SMS/dialer/assistant handler. Requires a **Permissions declaration**. **July 2026: `READ_CALL_LOG` may no longer be used for account verification via phone call** — use the Digital Credentials API, SMS Retriever API, or another method. Use **SMS Retriever API** for OTP autofill instead of `READ_SMS`. |
| **Package visibility** (`QUERY_ALL_PACKAGES`) | Only where awareness of *all* installed apps is core (antivirus, file manager, browser, device management, banking anti-fraud in some cases). Otherwise declare specific `<queries>` entries. Declaration required. |
| **AccessibilityService** | Only for genuine accessibility. Must disclose the use in-app **and** in the Play listing. Using it for automation, ad-blocking, or overlays → removal. |
| **Advertising ID** (`AD_ID`) | Must declare `com.google.android.gms.permission.AD_ID` for API 33+, complete the **Advertising ID declaration** in Console, and honor "Delete advertising ID". Must not be used in child-directed apps or linked to persistent identifiers/PII. |
| **Exact alarms** (`SCHEDULE_EXACT_ALARM` / `USE_EXACT_ALARM`) | `USE_EXACT_ALARM` only for alarm clock and calendar apps. Others must use `SCHEDULE_EXACT_ALARM` and handle the user denying it. |
| **Full-screen intent** (`USE_FULL_SCREEN_INTENT`) | Only for calling and alarm apps (API 34+). |
| **`REQUEST_INSTALL_PACKAGES`** | Only for app stores, file managers, backup/restore, enterprise device management. |
| **VPN service** | Only for actual VPN functionality; must not collect/redirect traffic for other purposes. |
| **Foreground services** | Every FGS type must map to a declared, user-visible use case. **April 2026: geofencing was removed as an approved FGS use case — use the Geofence API.** |
| **Health Connect** | Requires declaration + approved use case; treated as sensitive data. |
| **Device & Network Abuse** | No self-updating/self-modifying code outside Play; no downloading executable code (DEX, native, web) outside Play except for JS in a sandbox with no privileged access; no interfering with other apps; no ad fraud; no excessive battery/data use. |

---

## XIII. Deceptive Behavior & Misrepresentation
- App must do exactly what the listing says. No misleading claims, no fake system UI, no
  alarmist "your phone is infected" prompts, no fake reviews or ratings incentives.
- **Impersonation** — no icon, name, or developer name that imitates another app or entity.
- No manipulation of Play ratings/rankings; no incentivized installs or reviews.
- No hidden/dormant functionality activated after review.

---

## XIV. Store Listing & Promotion
- **Title ≤ 30 characters.** No emoji, no ALL-CAPS gimmicks, no "#1", "Best", "Free",
  performance claims, or price/promo text in title, icon, or developer name.
- **Short description ≤ 80 characters**; **full description ≤ 4000 characters**. No keyword
  stuffing, no irrelevant references to other apps/brands, no repeated blocks.
- **Icon** 512×512 PNG (32-bit, alpha allowed), must not include store badges, ratings,
  price, or "New"/"Sale" flashes, and must not imply Play Store ranking.
- **Feature graphic** 1024×500, no device frames, no cropped text, no call-to-action buttons
  that mimic UI, no fabricated app-store badges.
- **Screenshots** — min 2, max 8 per type; 16:9 or 9:16; between 320 px and 3840 px on each
  side; the long side ≤ 2× the short side. **Must depict actual in-app experience.**
  For Play's "large screen" and tablet quality tiers you need dedicated tablet screenshots.
- Machine-translated listings and misleading promo video content are policy violations.

---

## XV. Spam and Minimum Functionality
- No repetitive, near-duplicate, or auto-generated apps (a big 2026 enforcement theme).
- No webview-only wrappers of a website with no added value.
- Apps must install, load, and function; must not crash, force-close, or hang.
- No text/SMS spam or contact spam.

---

## XVI. Monetization and Ads
- **Google Play Billing is required** for in-app purchases of digital goods and content
  consumed within the app, with the same categories of exception Apple has (physical goods,
  services delivered outside the app, peer-to-peer, etc.), plus regional alternative-billing
  programs.
- **Billing Library version: 8 or later required for all new apps and updates by
  August 31, 2026** (extension available to November 1, 2026). Version 9 becomes required
  by August 31, 2027.
  - `AndroidManifest.xml` must contain the `com.google.android.play.billingclient.version`
    metadata (the Play plugin injects it).
- Subscriptions must clearly disclose price, billing period, and how to cancel, and must let
  the user cancel through Play.
- Ads must not be deceptive, must not interfere with device/app usability, must be
  distinguishable from app content, must be closeable, and must not appear outside the app or
  on the lock screen. Interstitials must not fire unexpectedly or immediately on launch.
- Ads in **Families**-program apps must use only **Google-certified ad SDKs** and must not
  be interest-based or remarketing-driven for children.

---

## XVII. Families Policy
If your target audience includes children:
- Complete the **Target audience and content** declaration accurately.
- Use only **Families-self-certified ad SDKs**.
- No collection of AAID/persistent identifiers from children; no interest-based ads.
- Content must be appropriate; app must comply with COPPA/GDPR-K and the Families Policy.
- Apps that appeal to children but declare an adult-only audience get reclassified — Play
  looks at icon, screenshots, description, and actual content.

---

## XVIII. Account-level and Console requirements

| Requirement | Detail |
|---|---|
| **App registration** | July 2026: **every app on Play must be registered in Play Console** to satisfy Android developer verification, or it is removed. |
| **Android developer verification** | Identity verification (government ID for individuals; **D-U-N-S number** for organizations, free, up to 28 days to obtain). Enforcement begins **September 30, 2026** in Brazil, Indonesia, Singapore, and Thailand; global in 2027. Unverified developers' apps become uninstallable on certified Android devices in those regions. Limited accounts (free) may distribute to ≤ 20 devices. Full account fee remains **$25 one-time**. |
| **Closed testing requirement (new personal developer accounts)** | Personal accounts created after Nov 13, 2023 must run a **closed test with at least 12 testers who opt in and stay opted in for 14 continuous days**, then apply for production access. As of 2026 the threshold is **12 testers / 14 days** (down from 20). |
| **Account transfers** | April 2026: must use the Play Console **"Transfer ownership"** workflow. Informal transfers violate policy. |
| **Content rating (IARC)** | Mandatory; unrated apps are not permitted. |
| **Target audience declaration** | Mandatory. |
| **Data safety** | Mandatory. |
| **Government apps / News apps / Financial features / Health / VPN / Prediction markets** declarations | Mandatory where applicable. News & magazine apps had a self-declaration deadline of **May 27, 2026**; prediction-market apps had to enroll in the pilot by **June 1, 2026**. |
| **App access instructions** | If any part of the app is behind a login or geofence, provide working credentials and steps in Play Console ▸ App content ▸ App access. Missing credentials is a top rejection. |

---

## Rule ID index for the scanner

| Rule ID | Policy | Severity |
|---|---|---|
| `PLAY-TARGETSDK` | Target API level | BLOCKER |
| `PLAY-BILLING-VER` | Billing Library ≥ 8 | BLOCKER (if IAP) |
| `PLAY-16KB` | 16 KB page-size support | BLOCKER |
| `PLAY-64BIT` | 64-bit ABI present | BLOCKER |
| `PLAY-DEBUGGABLE` | `android:debuggable=true` in release | BLOCKER |
| `PLAY-CLEARTEXT` | `usesCleartextTraffic=true` | HIGH |
| `PLAY-BACKUP` | `allowBackup=true` with sensitive data | MEDIUM |
| `PLAY-PERM-SMS` | SMS/Call Log without declaration | BLOCKER |
| `PLAY-PERM-BGLOC` | Background location without declaration | BLOCKER |
| `PLAY-PERM-STORAGE` | `MANAGE_EXTERNAL_STORAGE` without declaration | BLOCKER |
| `PLAY-PERM-MEDIA` | Broad photo/video without declaration | BLOCKER |
| `PLAY-PERM-QUERYALL` | `QUERY_ALL_PACKAGES` without declaration | HIGH |
| `PLAY-PERM-A11Y` | AccessibilityService misuse | BLOCKER |
| `PLAY-PERM-ADID` | Missing `AD_ID` permission/declaration | HIGH |
| `PLAY-PERM-EXACTALARM` | `USE_EXACT_ALARM` in a non-alarm app | HIGH |
| `PLAY-PERM-INSTALL` | `REQUEST_INSTALL_PACKAGES` unjustified | HIGH |
| `PLAY-FGS-TYPE` | Foreground service type unmapped / geofencing FGS | HIGH |
| `PLAY-DISCLOSURE` | Prominent disclosure missing | BLOCKER |
| `PLAY-DATASAFETY` | Data safety inconsistent with SDKs | BLOCKER |
| `PLAY-DELETE` | No in-app + web account deletion | BLOCKER |
| `PLAY-POLICY-URL` | Privacy policy missing/unreachable | BLOCKER |
| `PLAY-UGC` | UGC without report/block/moderation | BLOCKER |
| `PLAY-AI-REPORT` | AI content without in-app reporting | HIGH |
| `PLAY-LISTING-TITLE` | Title > 30 chars / promo text | BLOCKER |
| `PLAY-LISTING-ASSETS` | Screenshot/feature-graphic spec violation | HIGH |
| `PLAY-FAMILIES-SDK` | Non-certified ad SDK in a Families app | BLOCKER |
| `PLAY-ACCESS-INSTR` | App access instructions missing | BLOCKER |
| `PLAY-LOAN-PERMS` | Lending app requesting contacts/storage | BLOCKER |

---

## Sources
- [Developer Program Policy — Play Console Help](https://support.google.com/googleplay/android-developer/answer/16944162?hl=en)
- [Policy announcement: July 15, 2026 — Play Console Help](https://support.google.com/googleplay/android-developer/answer/17134731?hl=en)
- [Policy announcement: April 15, 2026 — Play Console Help](https://support.google.com/googleplay/android-developer/answer/16926792?hl=en)
- [Understanding Restricted Permissions with minimum scope alternatives — Play Console Help](https://support.google.com/googleplay/android-developer/answer/14115180?hl=en)
- [Understanding Android developer verification — Android Developer Console Help](https://support.google.com/android-developer-console/answer/16561738?hl=en)
- [Target API level requirements for Google Play apps — Play Console Help](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en)
- [Google Play Billing Library version deprecation — Android Developers](https://developer.android.com/google/play/billing/deprecation-faq)
