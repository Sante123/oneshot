# Apple App Review Guidelines — Rejection Index

Authoritative source: <https://developer.apple.com/app-store/review/guidelines/>
Last verified against the live guidelines: **2026-08-19**.

Guidelines marked **(ASR & NR)** apply to both App Store Review *and* Notarization
for iOS/iPadOS apps distributed through alternative marketplaces (EU).

> **How to use this file.** Each entry is `GUIDELINE — RULE — WHAT GETS REJECTED — FIX`.
> When you cite a finding, cite the guideline number exactly. Reviewers cite numbers;
> your remediation must map 1:1 to the number, or the resubmission bounces again.

---

## Severity legend used by the scanner

| Severity | Meaning |
|---|---|
| `BLOCKER` | Ship this and rejection is near-certain. Gate must fail. |
| `HIGH` | Frequently rejected. Gate fails unless explicitly waived with a written justification. |
| `MEDIUM` | Rejected in some review passes / some reviewers. Warn loudly. |
| `LOW` | Best practice; reduces reviewer friction. |

---

# 1. SAFETY

## 1.1 Objectionable Content — `HIGH`
Apps must not include content that is offensive, insensitive, upsetting, intended to
disgust, in exceptionally poor taste, or just plain creepy.

- **1.1.1** Defamatory, discriminatory, or mean-spirited content — including references
  or commentary about religion, race, sexual orientation, gender, national/ethnic origin,
  or other targeted groups. Professional political satirists and humorists are generally
  exempt.
- **1.1.2** Realistic portrayals of people or animals being killed, maimed, tortured, or
  abused; content that encourages violence. "Enemies" in a game cannot solely target a
  real race, culture, real government, corporation, or other real entity.
- **1.1.3** Depictions that encourage illegal or reckless use of weapons; facilitating
  the purchase of firearms or ammunition.
- **1.1.4** Overtly sexual or pornographic material — "explicit descriptions or displays
  of sexual organs or activities intended to stimulate erotic rather than aesthetic or
  emotional feelings." Includes "hookup" apps and anything facilitating prostitution or
  human trafficking.
- **1.1.5** Inflammatory religious commentary or inaccurate/misleading quotations of
  religious texts.
- **1.1.6 (ASR & NR)** False information and features — fake location trackers, "trick"
  or joke functionality. An "entertainment purposes only" disclaimer does **not** cure it.
  Apps that enable anonymous or prank calls / SMS / MMS are rejected.
- **1.1.7** Harmful concepts that capitalize on recent or current events — armed conflicts,
  terrorist attacks, epidemics.

**2026 note:** AI-generated deepfakes / likenesses of real, named people are being rejected
under 1.1 in addition to 5.2. Block named-real-person prompts or gate the feature.

## 1.2 User-Generated Content — `BLOCKER` if any of the four controls are missing
Apps with UGC or social networking **must** include **all four**:

1. A method for **filtering objectionable material** from being posted.
2. A mechanism to **report offensive content** with **timely responses** to concerns.
3. The ability to **block abusive users** from the service.
4. **Published contact information** so users can reach the developer easily.

Rejected outright: apps primarily used for pornography, Chatroulette-style random-video
experiences, anonymous chat, objectification ("hot-or-not" voting), physical threats, or
bullying.

- **1.2.1 Creator Content** — apps built around creator-generated content must provide a
  *structured* experience, not a bare repository. Creator content counts as UGC and is
  subject to all of 1.2.
  - **1.2.1(a) (ASR & NR)** Must provide a method for users to identify content that
    exceeds the app's age rating, and must apply verified or declared age restrictions
    for minors.

**2026 note:** guideline 1.2 gained new language around anonymous/random chat and minors.
Any anonymous-pairing feature must age-gate and moderate, or expect rejection.

## 1.3 Kids Category — `BLOCKER` for Kids Category apps
- No links out of the app, no purchasing opportunities, no other distractions — unless
  reserved behind a **parental gate**.
- Must comply with applicable children's privacy statutes **worldwide**.
- **No** personally identifiable information or device information transmitted to third
  parties.
- **No** third-party analytics or third-party advertising, with narrow exceptions for
  services that do **not** collect IDFA, identifiable children's data, location, or
  device information.
- Third-party **contextual** ads are permitted only where the ad service has publicly
  documented practices and human review for age-appropriateness.
- Requirements persist in subsequent updates even after the Kids Category is deselected.

## 1.4 Physical Harm (ASR & NR) — `BLOCKER` where applicable
- **1.4.1** Medical apps must disclose the data/methodology behind accuracy claims.
  **Cannot claim to measure x-rays, blood pressure, body temperature, blood glucose, or
  blood oxygen using device sensors alone.** Must remind users to consult a doctor.
  Regulatory clearance documentation must be submitted if claimed.
- **1.4.2** Drug-dosage calculators must originate from the drug manufacturer, a hospital,
  university, health-insurance company, pharmacy, or another approved entity, or receive
  FDA (or international equivalent) approval.
- **1.4.3** Must not encourage tobacco/vape/illegal-drug use or excessive alcohol
  consumption; must not encourage minors to consume any of these; must not facilitate the
  sale of controlled substances (licensed pharmacies and licensed/legal cannabis
  dispensaries excepted).
- **1.4.4** DUI checkpoint locations must be published by law enforcement. Never encourage
  drunk driving or other reckless behavior.
- **1.4.5** Must not urge customers to participate in activities that risk physical harm.

## 1.5 Developer Information (ASR & NR) — `HIGH`
An easy way to contact you must exist **inside the app** and in the Support URL. Wallet
passes require valid issuer contact info and a brand/trademark-owner certificate.

## 1.6 Data Security (ASR & NR) — `HIGH`
Implement appropriate security measures to prevent unauthorized access, use, or disclosure
of user information.

## 1.7 Reporting Criminal Activity
Must involve local law enforcement, and may only be offered in countries where that
involvement is active.

---

# 2. PERFORMANCE

## 2.1 App Completeness — `BLOCKER` (the single most common rejection)
- Submit the **final version**. No placeholder text, empty websites, temporary content,
  or "lorem ipsum".
- Test **on device** for bugs and stability before submitting.
- **Demo account required** if any part of the app is behind a login. Credentials must be
  live and working for the entire review. A built-in demo mode is allowed **only with
  prior Apple approval**.
- **Backend services must be live and accessible** during review — not behind a VPN,
  IP allowlist, geofence, or a staging environment that expires.
- All configured in-app purchases must be **complete, current, visible, and functional**.
- Non-obvious features must be explained specifically in **Notes for Review** — including
  hardware requirements, region requirements, and how to reach each feature.
- **2.1(b)** If a configured IAP is unavailable, explain why.

**The #1 concrete rejection: crash on launch on the reviewer's device.** Test on the
oldest supported OS *and* the newest, on a physical device, from a clean install, with no
prior app data and with network conditions constrained.

## 2.2 Beta Testing — `HIGH`
Beta/demo/trial versions belong on TestFlight only. Production listings must not say
"beta", "trial", "preview", "demo", or link to TestFlight. Testers cannot be compensated.

## 2.3 Accurate Metadata (ASR & NR) — `BLOCKER`
- **2.3.1(a)** No hidden, dormant, or undocumented features. Functionality must be clear
  to users **and to review**. New features must be described **specifically** in Notes for
  Review — generic descriptions get rejected. Marketing must be honest (e.g. no "iOS virus
  scanner" claims). False pricing is grounds for removal. Egregious or repeated behavior is
  grounds for **removal from the Apple Developer Program**.
- **2.3.1(b)** "If you attempt to deceive, you won't be doing business with us."
- **2.3.2** IAP features/levels/subscriptions must be clearly indicated in the description,
  screenshots, and previews. The app must properly handle `SKPaymentTransactionObserver`
  (or StoreKit 2 `Transaction.updates`) so promoted purchases complete seamlessly.
- **2.3.3** Screenshots must show the app **in use** — not just title art, a login screen,
  or a splash screen. Overlays and extended functionality framing are permitted.
- **2.3.4** App previews must use screen captures of the app only. Narration and overlays
  are permitted.
- **2.3.5** Choose the correct primary category. Apple may recategorize you.
- **2.3.6** Answer age-rating questions honestly. Misrating triggers customer complaints and
  regulatory inquiry. Territory-specific content-rating requirements apply.
- **2.3.7** App name must be unique, ≤ **30 characters**, and free of trademarked terms,
  other popular app names, pricing information, or irrelevant keyword-stuffing. Subtitles
  follow the same rules and must not contain unverifiable claims. Apple may modify
  inappropriate keywords.
- **2.3.8** Metadata must be appropriate for **all audiences (4+)** — icons, screenshots,
  and previews must be 4+ regardless of the app's own rating. No gruesome deaths, no guns
  pointed at characters. "For Kids"/"For Children" is reserved for the Kids Category.
  App name and icon must be consistent so users aren't confused.
- **2.3.9** You are responsible for securing rights to all materials. Use fictional account
  data in screenshots, never real personal data.
- **2.3.10** Do not reference other mobile platforms or alternative marketplaces by name,
  icon, or imagery in metadata.
- **2.3.11** Pre-orders must ship materially as advertised.
- **2.3.12** "What's New" must describe meaningful changes. "Bug fixes and performance
  improvements" alone is only acceptable for genuine bug-fix releases.
- **2.3.13** In-app events must be real, timely, correctly typed, accurately described, and
  deep-link to the right destination.

## 2.4 Hardware Compatibility
- **2.4.1** iPhone apps should run on iPad where possible.
- **2.4.2 (ASR & NR)** Design for power efficiency. No rapid battery drain, excessive heat,
  or unnecessary device strain. **No background cryptocurrency mining.**
- **2.4.3** tvOS apps must be usable with the Siri Remote alone; declare required
  controllers in metadata.
- **2.4.4 (ASR & NR)** Never require or suggest a device restart or modification of
  unrelated system settings.
- **2.4.5** Mac App Store: must be sandboxed (i); packaged via Xcode, single self-contained
  bundle, no third-party installers (ii); no auto-launch/login items or persistent
  background processes without consent, no auto-added Dock icons (iii); cannot download and
  install standalone apps/kexts/code (iv); cannot request root or setuid (v); no license
  screens or copy protection (vi); updates only through the Mac App Store (vii); must run on
  a currently shipping OS with no deprecated technologies (viii); all localizations in a
  single bundle (ix).

## 2.5 Software Requirements — `BLOCKER`
- **2.5.1** **Public APIs only.** No private API usage — this is detected by static analysis
  of your binary and is an automatic rejection. Run on the currently shipping OS. Phase out
  deprecated frameworks.
- **2.5.2** Self-contained bundles. Cannot read/write outside the container. **Cannot
  download, install, or execute code that introduces or changes features/functionality.**
  (JS-driven config changes to existing features are fine; shipping new native behavior is
  not.) Narrow exception for educational coding apps.
- **2.5.3** No viruses, files, or code that could damage or disrupt the OS/hardware,
  including via Push Notifications or Game Center.
- **2.5.4** Background modes only for their intended purposes — VoIP, audio playback,
  location, task completion, local notifications. **Declaring `UIBackgroundModes` you don't
  actually use is a rejection.**
- **2.5.5** Must be fully functional on **IPv6-only** networks (Apple's review network is
  IPv6-only NAT64/DNS64). Hardcoded IPv4 literals fail here.
- **2.5.6** Web browsing must use WebKit and WebKit JavaScript. Alternative browser engines
  require an entitlement (EU/Japan only).
- **2.5.8** Alternate desktop/home-screen environments are rejected.
- **2.5.9** Cannot alter or disable standard switches (Volume, Ring/Silent) or native UI
  elements and behaviors.
- **2.5.11 SiriKit / Shortcuts** — handle only intents your app can fulfil (i); vocabulary
  must pertain to your app, not generic terms or third-party services (ii); resolve requests
  directly with no ads or marketing between request and fulfilment (iii).
- **2.5.12 CallKit / SMS Fraud Extension** — only block confirmed spam; clearly identify
  blocking in marketing; explain criteria; data only for app operation, never for tracking,
  profiling, or sale.
- **2.5.13** Facial recognition for authentication must use `LocalAuthentication` where
  possible (not ARKit or third-party face recognition). Provide an alternative for users
  under 13.
- **2.5.14** Recording camera, microphone, screen, or user input requires **explicit user
  consent and a clear visual or audible indication** while recording.
- **2.5.15** File-selection apps must include Files-app items and the user's iCloud documents.
- **2.5.16** Widgets, extensions, and notifications must relate to the app's own content and
  functionality. **2.5.16(a)** All App Clip functionality must exist in the main binary; no
  advertising in App Clips.
- **2.5.17** Matter support must use Apple's Matter framework for pairing; non-Apple Matter
  components must be CSA-certified.
- **2.5.18 Advertising** — display ads only in the **main app binary**. **Not** in
  extensions, App Clips, widgets, notifications, keyboards, or watchOS apps. Ads must be
  age-appropriate. No targeted/behavioral ads based on sensitive data (health, school, kids).
  Interstitial/blocking ads need a clear indication and an **easily accessible dismiss
  button**. Apps with ads must let users report inappropriate ads.

---

# 3. BUSINESS

## 3.1 Payments — `BLOCKER`

### 3.1.1 In-App Purchase
Unlocking features or functionality inside the app **must** use IAP. Subscriptions,
in-game currencies, game levels, premium content, and full-version unlocks all qualify.
You may **not** use your own mechanisms — license keys, AR markers, QR codes, crypto
wallets — to unlock content.

- IAP currency may be used for tipping developers/content providers.
- Purchased credits and in-game currency **cannot expire**, and a **restore mechanism is
  mandatory**.
- Gifting of IAP-eligible items is permitted; refunds go to the original purchaser only.
- **Loot boxes / randomized virtual items must disclose the odds** before purchase.
- Digital gift cards/vouchers/coupons redeemable for digital goods must use IAP.
- Free time-based trials for non-subscription apps: use a **Non-Consumable IAP at Price
  Tier 0** named "XX-day Trial", and clearly disclose duration, what is lost at trial end,
  and downstream charges.
- NFTs: minting, listing, and transferring are allowed. Viewing owned NFTs is allowed if
  ownership does not unlock features. Browsing other collections is allowed, **but outside
  the US storefront you cannot include buttons or external links directing users to
  purchase outside IAP**.

**3.1.1(a) Link to Other Purchase Methods** — StoreKit External Purchase Link Entitlement
and Music Streaming Services Entitlement permit links in specific regions on iOS/iPadOS
only. Misleading marketing here means removal *and* Developer Program expulsion.

### 3.1.2 Subscriptions
- **3.1.2(a)** Must deliver **ongoing value**, minimum **7-day** period, and must work
  **across all of the user's devices**. Cannot require the user to perform tasks (social
  posts, contact uploads, check-ins) to access what they paid for. Existing paid-unlock
  users must retain access when a subscription model is introduced.
- **3.1.2(b)** Upgrades/downgrades must be seamless; users must not accidentally end up
  with multiple subscriptions.
- **3.1.2(c)** Clearly describe what the user gets. **The paywall must display, before
  purchase and without scrolling: title, length of subscription, content/services provided,
  price per period, and — for trials — "after the free trial, $X/period".** Links to
  **Terms of Use (EULA)** and **Privacy Policy** must be present on the paywall *and* in
  App Store Connect metadata. This is the most-cited subscription rejection.

### 3.1.3 Other Purchase Methods (non-IAP is allowed for these, but you may not
*encourage* alternatives inside the app outside the US storefront and the 3.1.1(a)/3.1.3(a)
entitlements)
- **(a) Reader apps** — magazines, newspapers, books, audio, music, video. External Link
  Account Entitlement available.
- **(b) Multiplatform services** — content purchased elsewhere may be accessed.
- **(c) Enterprise services** — sales to organizations, not consumers.
- **(d) Person-to-person services** — real-time one-to-one (tutoring, medical consults,
  real-estate tours, training). One-to-few/one-to-many requires IAP.
- **(e) Goods and services consumed outside the app** — physical goods **must not** use IAP;
  use Apple Pay or a card processor. Using IAP for physical goods is itself a rejection.
- **(f) Free standalone apps** companion to a paid web tool, with no in-app purchasing and
  no external purchase calls-to-action.
- **(g) Advertising management apps.**

### 3.1.4 Hardware-specific content
### 3.1.5 Cryptocurrencies
Wallets require organization enrollment (i). Mining must be off-device/cloud (ii).
Exchanges must be approved and licensed in the relevant country (iii). ICOs only from
established banks/securities firms/FCMs (iv). **Cannot reward users with cryptocurrency for
completing tasks** — downloads, referrals, social posts (v).

## 3.2 Other Business Model Issues
**Unacceptable (3.2.2):** App-Store-like interfaces of third-party apps (i); artificially
inflating ad impressions or clicks, or apps predominantly for ad display (iii); collecting
charity funds in-app unless an approved nonprofit (iv); arbitrary user restrictions by
location or carrier (v); artificially manipulating visibility/rank on other services (vii);
**binary options trading is prohibited**, and CFD/FOREX requires licensing in every
jurisdiction (viii); **personal loans must disclose max APR, must not exceed 36% APR, and
must allow at least 60 days to repay** (ix); **cannot force ratings, reviews, downloads, or
other store actions to unlock functionality** (x).

**Acceptable (3.2.1):** promoting your own apps (i); curated third-party recommendations
with robust editorial content (ii); rental expiry for films/TV/music/books (iii); Wallet
passes for payments/offers/identification (iv); insurance apps must be **free** and contain
no IAP (v); approved nonprofits fundraising with Apple Pay (vi); optional person-to-person
monetary gifts where 100% goes to the recipient (vii); financial trading apps from licensed
institutions (viii).

---

# 4. DESIGN

## 4.1 Copycats — `BLOCKER`
Original ideas only. Do not copy popular apps or make minor variations. Impersonating
another app or service violates the Developer Code of Conduct and can end your membership.
Do not use another developer's icon, brand, or name.

## 4.2 Minimum Functionality — `BLOCKER` (top-3 rejection)
Your app must be more than a repackaged website. It needs "lasting entertainment value" or
"adequate utility". A WebView wrapper of your site is the canonical rejection here.

- **4.2.1** ARKit apps need rich, integrated AR — not a model dropped into a camera view.
- **4.2.2** Apps must not be primarily marketing material, ads, web clippings, content
  aggregators, or link collections.
- **4.2.3(i)** The app must work independently of any other app being installed.
- **4.2.3(ii)** If additional resources download on first launch, **disclose the size and
  prompt the user**.
- **4.2.6** **Template or app-generation services are rejected unless submitted by the
  content provider directly**, on their own developer account. This kills white-label
  "one app per client on our account" models.
- **4.2.7 Remote desktop clients** — LAN + user-owned host only (a); execution/rendering on
  the host (b); account management initiated from the host (c); UI must not resemble iOS or
  the App Store (d); thin clients for cloud apps are inappropriate (e).

## 4.3 Spam — `BLOCKER`
- **4.3(a)** No multiple Bundle IDs of substantially the same app (e.g. one map app per
  city). Use one app with IAP or content variation.
- **4.3(b)** Apps **indistinguishable from what's already widely available** are rejected.
  **Updated June 2026:** dating, flashlight, sound-effect, wallpaper, timer, and
  fortune-telling apps must offer a "meaningfully different or improved experience".
  "Mediocre, low-quality, or low-effort" apps — drinking games, novelty/fart/burp apps,
  Kama Sutra apps — "do not add value to the App Store"; repeated submissions can get you
  removed from the Developer Program. This clause was tightened in direct response to the
  surge in AI-assisted app submissions. **If your app is AI-generated boilerplate, it will
  be rejected under 4.3(b).**

## 4.4 Extensions (ASR & NR)
- **4.4.1 Keyboards** must provide typed-character input, offer a next-keyboard method,
  function **without full network access / Full Access**, and collect activity only to
  improve the keyboard. They must not launch apps other than Settings or repurpose buttons.
- **4.4.2 Safari extensions** must run on the current Safari, not interfere with system or
  Safari UI, contain no malicious or misleading code, and not request more host permissions
  than needed.

## 4.5 Apple Sites and Services (ASR & NR)
- **4.5.1** No scraping of apple.com, the iTunes Store, App Store, App Store Connect, or the
  developer portal; no rankings built from that data.
- **4.5.2 Apple Music / MusicKit** — user-initiated playback with standard controls, no
  monetization gating, no downloading/uploading/sharing music files; MusicKit is not a
  substitute for a sync license; Apple Music data (playlists, favorites) must be disclosed
  and never used to identify users or target ads.
- **4.5.3** Do not spam or phish through Game Center, Push Notifications, or **Live
  Activities** (added 2026). Do not reverse-lookup Player IDs.
- **4.5.4** Push Notifications must not be required for the app to function, must not carry
  sensitive/confidential information, and may only be used for promotion/marketing **if the
  user opted in via a consent UI with an opt-out**.
- **4.5.5** Game Center Player IDs must not be displayed or shared.
- **4.5.6** Apple emoji may appear in the app and metadata, but not on other platforms and
  not embedded directly in your binary.

## 4.7 Mini apps, mini games, streaming games, chatbots, plug-ins, emulators (ASR & NR)
You are responsible for **all** embedded software. It must follow the same privacy rules
(4.7.1), must not extend native APIs without permission (4.7.2), must not inherit your app's
privacy permissions without **explicit per-instance user consent** (4.7.3), must be indexed
with universal links (4.7.4), and must let users identify content exceeding the age rating
(4.7.5).

## 4.8 Login Services (ASR & NR) — `BLOCKER` when triggered
If your app uses a **third-party or social login** (Facebook, Google, LinkedIn, Amazon,
WeChat, X) as its **primary** account mechanism, you must **also** offer an equivalent
privacy-preserving option that: limits data collection to name and email; lets the user keep
the email private; and does not collect interactions for advertising without consent.
Sign in with Apple satisfies this.

**Not required if:** you use only your own account system; you're an alternative marketplace
using its own login; you're an education/enterprise app requiring an existing institutional
account; you use a government/industry-backed citizen ID; or your app is a client for a
specific third-party service (e.g. a Gmail client).

## 4.9 Apple Pay — disclose all material purchase information; use branding correctly;
recurring payments must disclose the renewal term, what's provided, actual charges, and how
to cancel.

## 4.10 Monetizing Built-In Capabilities — you cannot charge for access to hardware
capabilities (Push, camera, gyroscope) or Apple services (Apple Music access, iCloud
storage, Screen Time APIs).

---

# 5. LEGAL

## 5.1 Privacy (ASR & NR) — `BLOCKER`

### 5.1.1 Data Collection and Storage
- **(i) Privacy Policies — required for every app, no exceptions.** Must be linked in App
  Store Connect metadata **and** accessible **inside the app**. Must identify what data is
  collected, how, and how it's used; confirm that third parties (analytics, ad networks,
  SDKs) provide equal protection; and explain retention/deletion and how users withdraw
  consent. A privacy policy behind a 404, a PDF, or a page that doesn't mention your SDKs is
  a rejection.
- **(ii) Permission** — collect data only with consent; purpose strings must be **clear and
  complete**, describing the actual user-facing benefit. `NS*UsageDescription` strings that
  say "This app needs camera access" are rejected; say *what for*.
- **(iii) Data Minimization** — request only data relevant to core functionality. Prefer
  out-of-process pickers (`PHPickerViewController`, `CNContactPickerViewController`, share
  sheet) over full library/Contacts access.
- **(iv) Access** — respect the user's permission settings. Never manipulate, trick, or force
  consent. Never make unrelated permissions mandatory. Provide graceful alternatives when
  a user declines (manual address entry instead of location).
- **(v) Account Sign-In** — **if the app does not include significant account-based features,
  let people use it without a login.** If you offer account creation, you **must offer
  account deletion from within the app** — not an email request, not a support ticket.
  Do not require personal information that isn't core-relevant or legally required. Do not
  store social credentials or tokens off-device.
- **(vi)** Surreptitiously discovering passwords or private data → removal from the Program.
- **(vii)** `SFSafariViewController` must be presented visibly and must not be hidden,
  obscured, or used to track users.
- **(viii)** Do not compile personal information from non-user sources (public databases)
  without explicit consent.
- **(ix)** Highly regulated fields — banking, financial services, healthcare, gambling,
  cannabis, air travel, crypto exchanges — must be submitted by a **legal entity**, not an
  individual developer account. Cannabis must be geo-restricted to legal jurisdictions.
- **(x)** Requests for basic contact information (name, email) must be **optional**, and
  features must not be conditional on providing it.

### 5.1.2 Data Use and Sharing
- **(i)** Never use, transmit, or share personal data without permission. **Clearly disclose
  third-party sharing — including third-party AI providers (added November 2025).** Sending
  user content to an LLM API without disclosure and consent is a current, actively enforced
  rejection. **App Tracking Transparency is mandatory before any tracking or access to the
  IDFA.** You may not require push, location, or tracking permission as a condition of using
  the app or receiving compensation.
- **(ii)** Data collected for one purpose cannot be repurposed without further consent.
- **(iii)** No surreptitious user profiles; no re-identifying "anonymized" data.
- **(iv)** Don't use Contacts or Photos APIs to build a database for sale/distribution;
  don't collect installed-app information for analytics or advertising.
- **(v)** No unsolicited messages via Contacts/Photos data. No "Select All", no pre-selected
  recipients; describe the message and sender before sending.
- **(vi)** **HomeKit, HealthKit, Clinical Health Records, MovementDisorder, ClassKit, and
  depth/facial-mapping (ARKit/Camera/Photos) data must never be used for marketing,
  advertising, or data mining** — by you or any third party.
- **(vii)** Apple Pay data only to facilitate/improve delivery of the goods or services.

### 5.1.3 Health and Health Research
Health data must not be disclosed to third parties for advertising, marketing, or data
mining (i). No false health data written to HealthKit; **no personal health information in
iCloud** (ii). Research requires informed consent covering nature/purpose/duration,
procedures, risks, benefits, confidentiality, a contact point, and withdrawal process (iii),
plus **independent ethics-board (IRB) approval, provable on request** (iv).

### 5.1.4 Kids
COPPA/GDPR-K compliance. Ask for birthdate or parental contact only to comply with statute.
Kids apps should not include third-party analytics or advertising. A **parental gate is not
parental consent** for data collection. "For Kids"/"For Children" naming is reserved for the
Kids Category; apps outside it must not imply a child audience in name, subtitle, icon,
screenshots, or description.

### 5.1.5 Location Services
Use location APIs only when directly relevant. Not for emergency services or autonomous
control of vehicles/aircraft (small drones, toys, and car alarms excepted). Notify and get
consent before collecting, transmitting, or using location data. Request **When In Use**
before **Always**; requesting Always without a demonstrated background need is rejected.

## 5.2 Intellectual Property — `BLOCKER`
- **5.2.1 Generally** — do not use protected third-party material (trademarks, copyrighted
  works, patented ideas) without authorization; provide documentation on request.
- **5.2.2 Third-Party Sites/Services** — if your app uses or accesses a third-party service,
  you must be authorized under its terms. Provide that authorization on request.
- **5.2.3 Audio/Video Downloading** — apps must not facilitate illegal file sharing or
  include the ability to save, convert, or download media from third-party sources
  (YouTube, SoundCloud, Vimeo, etc.) without explicit authorization.
- **5.2.4 Apple Endorsements** — don't suggest Apple is a source or endorser, and don't
  display Apple products in a false or disparaging light.
- **5.2.5 Apple Products** — don't create an app that looks confusingly similar to an
  existing Apple product, interface, or advertising theme. Don't use protected Apple assets
  (Apple logo, Apple Music/iTunes marks, icons) without a license. Music-identity guidelines
  apply for Apple Music integrations.

## 5.3 Gaming, Gambling, and Lotteries — `BLOCKER`
- **5.3.1** Sweepstakes and contests must be sponsored by the developer, with official rules
  in the app, and must state that Apple is **not** a sponsor or involved in any way.
- **5.3.2** Official rules for contests must be presented in the app and make clear Apple is
  not involved.
- **5.3.3** Apps may not use IAP to purchase credit or currency for use in real-money
  gaming; may not enable lotteries or raffles without the necessary licensing and
  permissions in **every** location where the app is available. Real-money gaming apps must
  be **free** on the App Store.
- **5.3.4** Real-money gaming, lotteries, and charitable donation apps must be **free**,
  must have the necessary licensing and permissions in each geography, must be **geo-fenced
  to those geographies**, and must not use IAP.
- **5.3.5** Apps that offer skill-based competition between real players for real-money
  prizes must be free and geo-restricted, with all applicable licenses.

## 5.4 VPN Apps — `BLOCKER` when misconfigured
Must use the `NEVPNManager` API and **must be submitted by a developer enrolled as an
organization**. Must clearly declare in the privacy policy what data is collected and how
it's used. **Must not sell, use, or disclose any data to third parties for any purpose.**
Must comply with local laws — you may be required to provide evidence of a licence in some
countries. Apps for parental control, content blocking, and enterprise security may use the
NEVPNManager API but must not violate these rules.

## 5.5 Mobile Device Management
MDM apps must be submitted by **commercial enterprises, educational institutions, or
government agencies**, and in limited cases by companies using MDM for parental controls or
device security. Must request the MDM capability from Apple. **Must not sell, use, or
disclose data to third parties for any purpose**, and must include a privacy policy
explaining what is collected. Apps offering configuration profiles must similarly comply.

## 5.6 Developer Code of Conduct — `BLOCKER`
Treat customers and App Review with respect. Manipulation, dishonesty, harassment of App
Review, or abusive behavior in the developer forums can end your membership.

- **5.6.1 App Store Reviews and Chart Ranking** — **Do not attempt to manipulate reviews,
  chart rankings, search results, or user reviews with paid, incentivized, fake, or
  fraudulent feedback, or any other dishonest method.** Use the native
  `SKStoreReviewController` / `AppStore.requestReview` API for rating prompts; do not gate
  functionality on a review; do not filter users to only route positive reviewers to the
  store. Prompting more than the system-allowed cadence, or custom review prompts that
  bypass the API, are rejections.
- **5.6.2 Developer Identity** — your account and app identity must be accurate. You may not
  create accounts on behalf of others, sell or transfer accounts, or misrepresent who you
  are. Providing false information in App Store Connect is grounds for termination.
- **5.6.3 Discovery Fraud** — do not manipulate App Store discovery: keyword stuffing,
  metadata cloaking, using competitor names, deceptive category selection, or artificially
  inflating downloads.
- **5.6.4 Account Integrity** — you are responsible for everything your team and your
  affiliated accounts do. Repeated violations across related accounts can result in the
  termination of all of them.

---

## Guideline-numbered quick index for the scanner

| Rule ID | Guideline | Severity | Detection surface |
|---|---|---|---|
| `APPLE-2.1-DEMO` | 2.1 | BLOCKER | login present & no demo account in review notes |
| `APPLE-2.1-BACKEND` | 2.1 | BLOCKER | staging/localhost/IP-allowlisted base URL in release config |
| `APPLE-2.3.1-PLACEHOLDER` | 2.3.1 | BLOCKER | lorem ipsum / TODO / TBD in metadata or strings |
| `APPLE-2.3.7-NAMELEN` | 2.3.7 | BLOCKER | app name > 30 chars |
| `APPLE-2.3.8-4PLUS` | 2.3.8 | HIGH | icon/screenshot content rating |
| `APPLE-2.5.1-PRIVATEAPI` | 2.5.1 | BLOCKER | private selector strings in binary/source |
| `APPLE-2.5.4-BGMODES` | 2.5.4 | HIGH | UIBackgroundModes declared without matching code |
| `APPLE-2.5.5-IPV6` | 2.5.5 | HIGH | hardcoded IPv4 literal in networking code |
| `APPLE-2.5.18-ADS` | 2.5.18 | HIGH | ad SDK linked into an extension/widget target |
| `APPLE-3.1.1-IAP` | 3.1.1 | BLOCKER | external payment SDK + digital goods |
| `APPLE-3.1.1-RESTORE` | 3.1.1 | BLOCKER | IAP present, no restore-purchases path |
| `APPLE-3.1.2-PAYWALL` | 3.1.2(c) | BLOCKER | paywall missing price/period/terms/privacy links |
| `APPLE-4.2-WEBVIEW` | 4.2 | BLOCKER | app is a WebView shell |
| `APPLE-4.8-SIWA` | 4.8 | BLOCKER | third-party social login without a privacy-preserving option |
| `APPLE-5.1.1-POLICY` | 5.1.1(i) | BLOCKER | no privacy policy URL in app + metadata |
| `APPLE-5.1.1-DELETE` | 5.1.1(v) | BLOCKER | account creation without in-app deletion |
| `APPLE-5.1.1-PURPOSE` | 5.1.1(ii) | BLOCKER | missing/vague `NS*UsageDescription` |
| `APPLE-5.1.2-ATT` | 5.1.2(i) | BLOCKER | IDFA/tracking SDK without `NSUserTrackingUsageDescription` + ATT call |
| `APPLE-5.1.2-AI` | 5.1.2(i) | HIGH | third-party LLM endpoint without disclosure/consent |
| `APPLE-5.1.3-MANIFEST` | 5.1 / ITMS-91053 | BLOCKER | Required Reason API used without `PrivacyInfo.xcprivacy` |
| `APPLE-5.1-ENCRYPTION` | 5.1 | HIGH | `ITSAppUsesNonExemptEncryption` missing |
| `APPLE-5.6.1-REVIEWS` | 5.6.1 | HIGH | custom/incentivized review prompt |

---

## Sources
- [App Review Guidelines — Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- [Apple tightens App Review Guidelines against apps that "do not add value" — 9to5Mac (June 9, 2026)](https://9to5mac.com/2026/06/09/apple-tightens-app-review-guidelines-against-apps-that-do-not-add-value-to-the-app-store/)
- [Apple's new App Review guidelines clamp down on apps sharing personal data with third-party AI — TechCrunch](https://techcrunch.com/2025/11/13/apples-new-app-review-guidelines-clamp-down-on-apps-sharing-personal-data-with-third-party-ai)
- [App Store Rejection Reasons Index (2026) — Push My App](https://pushmyapp.ai/blog/app-store-rejection-reasons)
