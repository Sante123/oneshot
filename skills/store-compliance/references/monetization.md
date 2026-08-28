# Monetization — IAP, Subscriptions, Paywalls, Ads

Payments are the second-largest rejection cluster after completeness/privacy, and the most
expensive to get wrong because fixing it usually means changing product design, not config.

---

## 1. The decision tree: must I use the store's billing?

```
What is being purchased?
│
├─ Digital content/features consumed INSIDE the app
│    → Apple: In-App Purchase REQUIRED (3.1.1)
│    → Play:  Google Play Billing REQUIRED (Monetization policy)
│
├─ Physical goods, or services delivered in the real world
│    (ride-hailing, food delivery, event tickets, physical retail)
│    → Apple: IAP FORBIDDEN (3.1.3(e)) — use Apple Pay / card processor
│    → Play:  Play Billing not required
│
├─ Real-time PERSON-TO-PERSON service (1:1 tutoring, medical consult,
│    property tour, personal training)
│    → Apple: IAP not required (3.1.3(d)). One-to-many DOES require IAP.
│    → Play:  generally allowed outside Play Billing
│
├─ Access to content the user already bought elsewhere ("reader" app:
│    magazines, newspapers, books, audio, music, video)
│    → Apple: IAP not required (3.1.3(a)); External Link Account
│      Entitlement available; NO in-app purchase calls-to-action
│    → Play:  allowed
│
├─ Multiplatform service where purchase happened on another platform
│    → Apple: access allowed (3.1.3(b)); no in-app steering
│    → Play:  allowed
│
├─ Sale to an ORGANIZATION for its employees/students (not consumers)
│    → Apple: 3.1.3(c) exemption
│
├─ Free companion app to a paid web SaaS tool, with no purchasing UI
│    → Apple: 3.1.3(f) exemption
│
├─ Insurance
│    → Apple: app must be FREE with NO IAP (3.2.1(v))
│
├─ Real-money gambling / lottery / skill-for-cash
│    → Apple: app must be FREE, licensed, geo-fenced, NO IAP (5.3)
│    → Play:  licensed operator, free download, AO rating, geo-restricted
│
├─ Charitable donations
│    → Apple: only approved nonprofits may collect in-app (with Apple Pay);
│      everyone else must collect outside the app, and the app must be free
│    → Play:  donations generally outside Play Billing
│
└─ Optional person-to-person monetary gift, 100% to recipient,
     not tied to digital content
     → Apple: 3.2.1(vii) allowed without IAP
```

**Getting this backwards in either direction is a rejection.** Selling a t-shirt through
StoreKit is 3.1.3(e); selling a premium tier through Stripe is 3.1.1.

---

## 2. Paywall requirements (Apple 3.1.2, and the single most-cited subscription rejection)

The purchase screen must show, **visible without scrolling, adjacent to the buy button**:

- [ ] **Subscription title** / what the tier is called
- [ ] **Length of the subscription period** ("1 month", "1 year")
- [ ] **What the subscription provides** during that period
- [ ] **Price** and **price per unit** where relevant ("$59.99/year ($5.00/month)")
- [ ] **Auto-renewal statement** — "Subscription automatically renews unless cancelled at
      least 24 hours before the end of the current period."
- [ ] **Free-trial disclosure**, if any — "7 days free, then $9.99/month"
- [ ] **Link to Terms of Use (EULA)** — functional, opens the actual document
- [ ] **Link to Privacy Policy** — functional
- [ ] **Restore Purchases** button — mandatory whenever any non-consumable or subscription
      exists (3.1.1). Must be reachable **without being signed in**.

And in App Store Connect:
- [ ] **Privacy Policy URL** filled
- [ ] **Terms of Use (EULA) URL** filled (or Apple's standard EULA accepted)
- [ ] Every subscription has a **localized display name and description** and a
      **review screenshot**
- [ ] Subscription group set up correctly so upgrades/downgrades are seamless (3.1.2(b))

**Play equivalent:** show price, period, renewal, and cancellation path; direct users to
Play's subscription management for cancellation; do not imply cancellation happens in your
app when it happens in Play.

### Common paywall rejections
| Symptom | Guideline |
|---|---|
| Price shown only after tapping "Continue" | 3.1.2(c) |
| Terms/Privacy links are plain text, not tappable | 3.1.2(c) |
| No Restore Purchases anywhere | 3.1.1 |
| Restore only available after login | 3.1.1 |
| Trial length shown but not the post-trial price | 3.1.2(a) |
| Hard paywall on launch with no way to see any value or dismiss | 4.2 / 3.1.2 (not an automatic rejection, but heavily scrutinized — offer a preview or a clear close button) |
| "Cancel anytime in the app" (you can't; it's in Settings/Play) | 2.3.1 |
| Subscription that only works on one device | 3.1.2(a) |
| Credits that expire | 3.1.1 |
| Loot box with undisclosed odds | 3.1.1 |

---

## 3. StoreKit implementation checklist (Apple)

- [ ] StoreKit 2 (`Product`, `Transaction`) or a correctly-registered
      `SKPaymentTransactionObserver` — required for **promoted in-app purchases** to work
      (2.3.2). A missing observer means purchases initiated from the App Store page hang.
- [ ] `Transaction.updates` listener started at app launch, before UI.
- [ ] All transactions `finish()`ed after the entitlement is granted.
- [ ] Interrupted purchases (`Transaction.unfinished`) are recovered at launch.
- [ ] Receipt/JWS validation done server-side (or via `AppTransaction`/`Transaction` APIs);
      on-device receipt validation must support SHA-256.
- [ ] Ask-to-Buy / pending (`.pending`) state handled — the reviewer's sandbox account may
      hit it.
- [ ] Sandbox tested with a fresh Sandbox Apple ID **and** with an interrupted/failed
      purchase.
- [ ] All products **Ready to Submit** in App Store Connect and attached to the version
      (first submission of a new IAP must be submitted **with** the app binary).
- [ ] Products' review screenshot and review notes filled.
- [ ] Prices set in every storefront where the app is available.

## 4. Play Billing implementation checklist

- [ ] **Billing Library ≥ 8.0.0** (required for new apps/updates by Aug 31, 2026).
- [ ] `com.android.vending.BILLING` permission (added by the library).
- [ ] `com.google.android.play.billingclient.version` metadata present in the merged
      manifest.
- [ ] `BillingClient` connection retry/reconnect implemented.
- [ ] **Purchases acknowledged within 3 days** (`acknowledgePurchase` /
      `consumeAsync`) — unacknowledged purchases are auto-refunded and look like a bug.
- [ ] `queryPurchasesAsync` on resume to restore entitlements.
- [ ] Real-time developer notifications (RTDN) wired for subscription lifecycle.
- [ ] Server-side verification via the Play Developer API.
- [ ] Products active in Play Console and the app uploaded to a track that includes them,
      or testers can't see them.
- [ ] License testers configured so the reviewer's flow works.

---

## 5. Advertising

### Apple 2.5.18
- Ads only in the **main app binary**. Never in extensions, App Clips, widgets,
  notifications, keyboards, or watchOS.
- Age-appropriate for the app's rating; no behavioral targeting on sensitive categories
  (health, school, kids).
- Interstitials must be clearly indicated with an **easily accessible dismiss control** —
  a 4×4pt X in the corner is a rejection; give a real tap target and don't delay it
  excessively.
- Users must be able to **report inappropriate ads**.
- Ad SDK must be ATT-compliant and must appear in `NSPrivacyTrackingDomains`.

### Play Monetization & Ads
- Ads must be distinguishable from content, must not mimic system UI or notifications,
  must not appear outside the app or on the lock screen, must be closeable, and must not
  fire unexpectedly (e.g. immediately on cold start before any interaction).
- No ads that interfere with device functionality (full-screen ads on back-press chains).
- **Families apps: Google-certified ad SDKs only, non-personalized ads only.**
- Ad fraud (clicks/impressions not from genuine user interaction) → account termination.

### Both
- Rewarded ads must not be required to use core functionality that the user paid for.
- Never reward users for granting ATT/permissions or for rating the app.

---

## 6. Region and category traps

| Category | Rule |
|---|---|
| Personal loans | Apple 3.2.2(ix): ≤ 36% APR, ≥ 60 days to repay, full term disclosure. Play: same + no contacts/storage permissions + country licensing |
| Crypto | Apple 3.1.5: wallets need an org account; exchanges need local licensing; no on-device mining; **no rewards for tasks**. Play: certified exchanges/wallets, no on-device mining, financial-features declaration for tokenized assets, **no earning-potential promotion** |
| Trading / FOREX / CFD | Apple 3.2.2(viii): binary options banned; licensing everywhere you ship |
| Healthcare payments | Play: **Play Billing may not be used for regulated clinical services** |
| Dating | Both: age-gate; Play requires child-safety standards for social/dating |
| Gambling | See §1 — free app, licensed, geo-fenced, AO rating |
| NFTs | Apple: viewing owned NFTs OK if it doesn't unlock features; **no external purchase links outside the US storefront**. Play: no paying for a chance at an unknown-value NFT |

---

## 7. Auto-fixable vs. product-decision

The `oneshot` fixer will change these automatically:
- Add a Restore Purchases entry point to an existing paywall view.
- Add Terms/Privacy links to the paywall.
- Add the missing renewal/price disclosure text block.
- Bump Play Billing Library version in Gradle.
- Register the StoreKit transaction listener at launch.
- Fill Terms of Use URL in the submission metadata file.

These require a human decision and will be reported, not fixed:
- Replacing an external payment flow with IAP (product/revenue impact).
- Changing the paywall from hard to soft.
- Restructuring subscription tiers or pricing.
- Anything involving licensing or regulated categories.

---

## Sources
- [App Review Guidelines §3 Business — Apple Developer](https://developer.apple.com/app-store/review/guidelines/#business)
- [Google Play Billing Library version deprecation — Android Developers](https://developer.android.com/google/play/billing/deprecation-faq)
- [Developer Program Policy — Play Console Help](https://support.google.com/googleplay/android-developer/answer/16944162?hl=en)
