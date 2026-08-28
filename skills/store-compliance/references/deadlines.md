# Hard Deadlines & Version Floors

This file is the one most likely to go stale. **Re-verify before relying on it.**
Last verified: **2026-08-19**.

The `oneshot verify-deadlines` command re-checks these against the live sources.

---

## Apple

| Requirement | Deadline | Status as of 2026-08-19 | Source |
|---|---|---|---|
| Build with **Xcode 26+ / iOS 26 SDK** (also iPadOS/tvOS/visionOS/watchOS 26) for all App Store Connect uploads | **2026-04-28** | **In force** | [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) |
| Answer the **updated age-rating questionnaire** (new 13+/16+/18+ tiers) | **2026-01-31** | **In force** — unanswered blocks submission | [Apple Developer News](https://developer.apple.com/news/?id=ks775ehf) |
| **Privacy manifests** (`PrivacyInfo.xcprivacy`) for Required Reason APIs + third-party SDK manifests & signatures | 2024-05-01 | In force | [Apple Developer News](https://developer.apple.com/news/?id=3d8a9yyh) |
| **EU DSA trader status** for EU storefront distribution | 2025-02-17 | In force | App Store Connect |
| App Store receipt signing — SHA-256 support for on-device validation | 2025-01-24 | In force | Apple Developer News |
| APNs certificate trust-store update (SHA-2 root) | 2025-02-24 | In force | Apple Developer News |
| macOS: strip `com.apple.quarantine` before upload | 2025-02-18 | In force | Apple Developer News |
| **Third-party AI data-sharing disclosure** (5.1.2(i)) | 2025-11 | In force | Guidelines update |
| **4.3(b) low-quality/low-effort app tightening** | 2026-06-09 | In force | Guidelines update |
| **Accessibility Nutrition Labels** | Rolling; declare accurately | Available in App Store Connect | Apple |

### Apple version floors
| Thing | Floor |
|---|---|
| Build SDK | iOS/iPadOS/tvOS/watchOS/visionOS **26** |
| Xcode | **26** |
| Web rendering | WebKit (`WKWebView`); `UIWebView` removed |
| Receipt validation | SHA-256, or `AppTransaction`/`Transaction` APIs |
| Recommended deployment target | Current − 2 major versions (your call; not a store rule) |

---

## Google Play

| Requirement | Deadline | Status | Source |
|---|---|---|---|
| **Target API 36 (Android 16)** for new apps & updates (phone/tablet/Auto) | **2026-08-31** (extension to **2026-11-01**) | **Imminent — 12 days out** | [Target API level requirements](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en) |
| Existing apps must target **API 35** to stay discoverable on newer devices | **2026-08-31** | Imminent | same |
| **Wear OS** target API 35 (new/updates); API 34 (existing) | **2026-08-31** | Imminent | same |
| **Android TV** target API 34 (new/updates, since 2025); API 33 (existing) | **2026-08-31** | Imminent | same |
| **Android Automotive** target API 35 (new/updates); API 32 (existing) | **2026-08-31** | Imminent | same |
| **Android XR** target API 34 | **2026-08-31** | Imminent | same |
| **Play Billing Library ≥ 8** for new apps & updates | **2026-08-31** (extension to 2026-11-01) | **Imminent** | [Billing deprecation FAQ](https://developer.android.com/google/play/billing/deprecation-faq) |
| Play Billing Library ≥ 9 | 2027-08-31 | Upcoming | same |
| **16 KB page-size support** for apps with native code targeting API 35+ | 2025-11-01 | In force | [16 KB page sizes](https://developer.android.com/guide/practices/page-sizes) |
| **Photo & video permissions** minimum scope (Photo Picker) | 2025-05-28 | In force | [Restricted permissions](https://support.google.com/googleplay/android-developer/answer/14115180?hl=en) |
| **Contacts permission** minimum scope (Contact Picker) | **2027-01** (Android 17 / API 37+) | Upcoming — build for it now | same |
| **Foreground services**: geofencing removed as an approved use case | ~2026-05-15 (30 days from 2026-04-15) | In force | [April 15, 2026 announcement](https://support.google.com/googleplay/android-developer/answer/16926792?hl=en) |
| **Location permissions**: location button as minimum scope | ~2026-05-15 | In force | same |
| **Account transfers** must use Play Console "Transfer ownership" | ~2026-05-15 | In force | same |
| **`READ_CALL_LOG` no longer valid for phone-call account verification** | ~2026-08-14 (30 days from 2026-07-15) | **Just in force** | [July 15, 2026 announcement](https://support.google.com/googleplay/android-developer/answer/17134731?hl=en) |
| **All Play apps must be registered in Play Console** (developer verification) | ~2026-08-14 | **Just in force** | same |
| Anonymous/random chat + child-safety requirements | ~2026-08-14 | **Just in force** | same |
| **Unrated apps not permitted** (IARC mandatory) | Clarified 2026-07-15 | In force | same |
| **Android developer verification enforcement** — Brazil, Indonesia, Singapore, Thailand | **2026-09-30** | **~6 weeks out** | [Understanding Android developer verification](https://support.google.com/android-developer-console/answer/16561738?hl=en) |
| Android developer verification — global | 2027 | Upcoming | same |
| News & magazine app self-declaration | 2026-05-27 | In force | April 2026 announcement |
| Prediction-market app pilot enrollment | 2026-06-01 | In force | April 2026 announcement |

### Google Play version floors
| Thing | Floor |
|---|---|
| `targetSdk` (new apps & updates) | **36** |
| `compileSdk` | ≥ targetSdk (36) |
| Play Billing Library | **8.0.0** |
| Native `.so` alignment | **16384** (16 KB) |
| ABIs | must include **arm64-v8a** |
| Publishing format | **AAB** for new apps |
| AGP / NDK for 16 KB | AGP 8.5.1+, NDK r27+ |

### Google Play account thresholds
| Thing | Value |
|---|---|
| New personal account closed testing | **12 testers, opted in continuously for 14 days**, then apply for production access |
| Full developer account fee | **$25** one-time |
| Limited (unverified) distribution | ≤ **20 devices** |
| D-U-N-S processing time | up to **28 days** — start early |
| Android vitals: user-perceived crash rate | keep **< 1.09%** |
| Android vitals: user-perceived ANR rate | keep **< 0.47%** |

---

## Immediate action items (as of 2026-08-19)

1. **`targetSdk = 36` and Play Billing Library 8** — the deadline is **August 31, 2026**,
   twelve days away. If you cannot make it, request the extension to November 1 in Play
   Console ▸ Policy status **before** the 31st.
2. **Android developer verification** — if you distribute in Brazil, Indonesia, Singapore,
   or Thailand, verification enforcement starts **September 30, 2026**, and a D-U-N-S number
   can take 28 days. Start today.
3. **Register every app in Play Console** — the requirement is already in force.
4. **Xcode 26 / iOS 26 SDK** — already mandatory; check your CI image.

---

## Keeping this file current

```bash
python3 scripts/oneshot.py verify-deadlines
```

That command re-fetches the source pages listed above and reports any date or version that
has changed, so this file never silently rots. Run it before every submission and before
trusting any version floor in this document.
