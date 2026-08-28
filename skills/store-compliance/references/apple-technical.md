# Apple — Technical & Build-Level Rejection Surface

Everything here is deterministic: it can be checked mechanically before you ever hit
"Submit". These are the failures that produce **ITMS-* errors** (upload-time, hard blocks)
and **automated binary-scan rejections** (post-upload emails from App Store Connect).

---

## 1. Upload-blocking requirements (ITMS-*)

| Code | Cause | Fix |
|---|---|---|
| `ITMS-90683` | Missing purpose string for a protected resource (`NSCameraUsageDescription`, etc.) | Add the `NS*UsageDescription` key to the **app target's** Info.plist *and* to any extension target that triggers the prompt |
| `ITMS-91053` | Missing `NSPrivacyAccessedAPITypes` entry for a Required Reason API your code calls | Add `PrivacyInfo.xcprivacy` with the right category and reason code |
| `ITMS-91056` | Invalid privacy manifest — malformed plist or unknown key | Validate the plist; only the four top-level keys are legal |
| `ITMS-91061` | A linked third-party SDK on Apple's "commonly used SDKs" list is missing its privacy manifest and/or signature | Update the SDK to a version that ships `PrivacyInfo.xcprivacy` + signature |
| `ITMS-90809` | Deprecated API (historically UIWebView) | Migrate to `WKWebView` |
| `ITMS-90717` | Invalid app icon — alpha channel or transparency in the marketing icon | Flatten to opaque RGB, 1024×1024, no alpha, no rounded corners |
| `ITMS-90022/23/24` | Missing required icon sizes | Regenerate the full icon set / use a single 1024 App Icon asset with "Single Size" |
| `ITMS-90704/90705` | Missing or wrong-size Marketing Icon | 1024×1024 PNG |
| `ITMS-90478` | Invalid version — CFBundleShortVersionString must increase | Bump the version |
| `ITMS-90062` | `CFBundleVersion` not a valid, monotonically increasing build number | Bump build |
| `ITMS-90111` | Bitcode/architecture mismatch | Rebuild with the required SDK |
| `ITMS-90338` | Non-public API usage detected | Remove the symbol |
| `ITMS-90535` | Unexpected CFBundleExecutable key | Fix nested bundle plists (often from a resource bundle) |
| `ITMS-90206/90171` | Invalid bundle structure — disallowed files/frameworks in the wrong place | Embed frameworks only in `Frameworks/` |
| `ITMS-90885` | Bundle ID already exists | Change the bundle ID |
| `ITMS-90889` | Missing `CFBundleIconName` in an asset catalog | Use an asset catalog for icons |
| `ITMS-90165` | Missing/invalid provisioning profile or entitlements mismatch | Regenerate profile with matching entitlements |
| `ITMS-90426` | Invalid Swift support / missing swift libraries | Clean build with matching Xcode |
| `ITMS-90503` | Invalid `NSPhotoLibraryAddUsageDescription` missing when writing to Photos | Add the *Add*-specific key |

**Rule:** an ITMS error means the binary never reached a human. Fix and re-upload; it does
not consume a review cycle, but it does consume your day.

---

## 2. Minimum SDK requirement — hard deadline

**As of April 28, 2026**, all apps submitted to App Store Connect must be **built with
Xcode 26 or later** using the **iOS 26 / iPadOS 26 / tvOS 26 / visionOS 26 / watchOS 26
SDK** (or later).

- This is the **build SDK**, not the deployment target. Your `IPHONEOS_DEPLOYMENT_TARGET`
  can stay low; `SDKROOT` must be 26+.
- Verify: `xcodebuild -version` and, on the built app, `plutil -p Info.plist | grep -i DTSDK`
  → `DTSDKName` should read `iphoneos26.x` and `DTPlatformVersion` `26.x`.
- CI runners pinned to older Xcode images will fail upload with a clear message.
- React Native / Expo / Flutter: bump the CI image and, for Expo, the EAS build image.

**Verification command:**

```bash
# On a built .app or extracted .ipa payload
plutil -extract DTSDKName raw Payload/YourApp.app/Info.plist
plutil -extract DTXcodeBuild raw Payload/YourApp.app/Info.plist
```

---

## 3. Info.plist — required and rejection-prone keys

### 3.1 Purpose strings (`NS*UsageDescription`)

Every protected resource your binary can touch needs a purpose string in **every target
that triggers the prompt**. Missing → `ITMS-90683` at upload. Vague → rejected under
**5.1.1(ii)**.

| Key | Triggered by |
|---|---|
| `NSCameraUsageDescription` | AVCapture, UIImagePickerController camera source, ARKit |
| `NSMicrophoneUsageDescription` | AVAudioRecorder, AVCaptureDevice audio, VoIP, video recording |
| `NSPhotoLibraryUsageDescription` | Full PhotoKit read access (not needed for `PHPickerViewController`) |
| `NSPhotoLibraryAddUsageDescription` | Saving to the camera roll |
| `NSLocationWhenInUseUsageDescription` | `requestWhenInUseAuthorization` |
| `NSLocationAlwaysAndWhenInUseUsageDescription` | `requestAlwaysAuthorization` |
| `NSLocationTemporaryUsageDescriptionDictionary` | Temporary full-accuracy request |
| `NSContactsUsageDescription` | CNContactStore (not needed for `CNContactPickerViewController`) |
| `NSCalendarsFullAccessUsageDescription` / `NSCalendarsWriteOnlyAccessUsageDescription` | EventKit (iOS 17+ split) |
| `NSRemindersFullAccessUsageDescription` | EventKit reminders (iOS 17+) |
| `NSMotionUsageDescription` | CMMotionManager, CMPedometer |
| `NSHealthShareUsageDescription` / `NSHealthUpdateUsageDescription` | HealthKit |
| `NSBluetoothAlwaysUsageDescription` | CoreBluetooth |
| `NSLocalNetworkUsageDescription` | Bonjour / local network discovery |
| `NSSpeechRecognitionUsageDescription` | SFSpeechRecognizer |
| `NSFaceIDUsageDescription` | LocalAuthentication with biometrics |
| `NSUserTrackingUsageDescription` | **ATTrackingManager — mandatory before IDFA** |
| `NSAppleMusicUsageDescription` | MediaPlayer / MusicKit library access |
| `NSSiriUsageDescription` | SiriKit |
| `NSNearbyInteractionUsageDescription` | NearbyInteraction |
| `NSFileProviderDomainUsageDescription` | File Provider |
| `NSDesktopFolderUsageDescription` / `NSDocumentsFolderUsageDescription` / `NSDownloadsFolderUsageDescription` | macOS folder access |

**Quality bar for the string:** name the feature and the user benefit.
- ✗ `"This app needs access to your camera."`
- ✓ `"Bright uses your camera so you can scan a receipt and add it to an expense report."`

Localize purpose strings in `InfoPlist.strings` for every localization you ship, or the
non-English storefronts show English text — a 5.1.1(ii) finding in some review passes.

### 3.2 Other required / high-risk keys

| Key | Requirement |
|---|---|
| `ITSAppUsesNonExemptEncryption` | Set to `false` if you only use standard HTTPS/OS-provided crypto. If `true`, you need export-compliance documentation (and possibly a CCATS/ERN). Omitting it forces a manual question on every submission and can stall review. |
| `CFBundleDisplayName` | Should visually match the App Store name (2.3.8) |
| `CFBundleShortVersionString` | Must strictly increase per submission |
| `CFBundleVersion` | Must strictly increase per upload of the same version |
| `UIBackgroundModes` | Declare **only** modes you actually use — 2.5.4 |
| `NSAppTransportSecurity` | `NSAllowsArbitraryLoads: true` requires justification; blanket ATS exceptions draw scrutiny. Prefer per-domain exceptions. |
| `LSApplicationQueriesSchemes` | Only schemes you genuinely query. Enumerating competitor apps → 5.1.2(iv) |
| `UIRequiredDeviceCapabilities` | Must not exclude devices your metadata claims to support |
| `UISupportedInterfaceOrientations` | If you claim iPad support (2.4.1), handle all iPad orientations & multitasking |
| `NSPrivacyAccessedAPITypes` | Lives in `PrivacyInfo.xcprivacy`, not Info.plist |
| `CFBundleLocalizations` | Must match the localizations declared in App Store Connect |
| `UIApplicationSceneManifest` | Required for multi-window on iPad |

---

## 4. Privacy manifests (`PrivacyInfo.xcprivacy`)

A property list added to **each target that needs one** (app, each app extension, each
framework/SDK you own). Four top-level keys:

```xml
<key>NSPrivacyTracking</key><false/>
<key>NSPrivacyTrackingDomains</key><array/>
<key>NSPrivacyCollectedDataTypes</key><array>...</array>
<key>NSPrivacyAccessedAPITypes</key><array>...</array>
```

### 4.1 `NSPrivacyTracking` / `NSPrivacyTrackingDomains`
- `NSPrivacyTracking` = `true` only if the app or SDK tracks as defined by ATT.
- If `true`, **every** domain that receives tracking traffic must be listed in
  `NSPrivacyTrackingDomains`. Those domains are **blocked at the network layer** when the
  user denies ATT. If you list nothing and still send tracking traffic, that's 5.1.2(i).

### 4.2 `NSPrivacyCollectedDataTypes`
One dict per collected data type:

```xml
<dict>
  <key>NSPrivacyCollectedDataType</key><string>NSPrivacyCollectedDataTypeEmailAddress</string>
  <key>NSPrivacyCollectedDataTypeLinked</key><true/>
  <key>NSPrivacyCollectedDataTypeTracking</key><false/>
  <key>NSPrivacyCollectedDataTypePurposes</key>
  <array><string>NSPrivacyCollectedDataTypePurposeAppFunctionality</string></array>
</dict>
```

**Purposes:** `ThirdPartyAdvertising`, `DeveloperAdvertising`, `AnalyticsPurpose`,
`ProductPersonalization`, `AppFunctionality`, `Other`.

**This must agree with the App Privacy ("nutrition label") answers in App Store Connect.**
A mismatch between the manifest, the nutrition label, and observed network traffic is the
classic 5.1.1 rejection.

### 4.3 `NSPrivacyAccessedAPITypes` — Required Reason APIs

Five categories. Each needs a category string and at least one approved reason code.

| Category (`NSPrivacyAccessedAPIType`) | APIs it covers | Common approved reasons (`NSPrivacyAccessedAPITypeReasons`) |
|---|---|---|
| `NSPrivacyAccessedAPICategoryFileTimestamp` | `creationDate`, `modificationDate`, `fileModificationDate`, `contentModificationDateKey`, `creationDateKey`, `getattrlist`, `getattrlistbulk`, `fgetattrlist`, `stat`, `fstat`, `fstatat`, `lstat`, `getattrlistat`, `NSFileCreationDate`, `NSFileModificationDate`, `NSURLContentModificationDateKey`, `NSURLCreationDateKey` | `DDA9.1` (display to user), `C617.1` (files inside the app container / app group / CloudKit container), `3B52.1` (timestamp of a file the user specifically granted access to), `0A2A.1` (third-party SDK acting on behalf of the app) |
| `NSPrivacyAccessedAPICategorySystemBootTime` | `systemUptime`, `mach_absolute_time` | `35F9.1` (measure elapsed time for in-app events), `8FFB.1` (calculate absolute timestamps for internal user-initiated events) |
| `NSPrivacyAccessedAPICategoryDiskSpace` | `volumeAvailableCapacityKey`, `volumeAvailableCapacityForImportantUsageKey`, `volumeAvailableCapacityForOpportunisticUsageKey`, `volumeTotalCapacityKey`, `systemFreeSize`, `systemSize`, `statfs`, `statvfs`, `fstatfs`, `fstatvfs`, `getattrlist`, `getattrlistat` | `85F4.1` (display to the user), `E174.1` (check for sufficient space before writing), `7D9E.1` (user-initiated bug report) |
| `NSPrivacyAccessedAPICategoryActiveKeyboards` | `UITextInputMode.activeInputModes` | `3EC4.1` (custom keyboard app, own keyboards only), `54BD.1` (customize UI for the user's keyboard languages, no off-device transmission) |
| `NSPrivacyAccessedAPICategoryUserDefaults` | `UserDefaults`, `NSUserDefaults`, `CFPreferences*` | `CA92.1` (access to information stored by the app itself), `1C8F.1` (app-group defaults shared with the app's own extensions/apps), `AC6B.1` (`com.apple.developer.web-browser` entitlement holders), `C56D.1` (third-party SDK providing defaults access on behalf of the app) |

**Reason codes are exact strings.** Inventing one or using a category without a reason
produces `ITMS-91053`/`ITMS-91056`.

### 4.4 Third-party SDK signature requirement
SDKs on Apple's "commonly used SDKs" list must ship a privacy manifest **and** a code
signature. If you link an old version, you get `ITMS-91061`. Practical fix: keep every SDK
on a post-2024 release and check each vendor's privacy-manifest release note. Static
`.a`/`.framework` copies vendored into your repo are the usual culprit.

**Aggregation:** run the target's manifests through Xcode's *Product ▸ Archive ▸ Generate
Privacy Report* and compare the result against your App Store Connect nutrition label
before every submission.

---

## 5. Entitlements — 2.5.4 orphan check

Every capability in your `.entitlements` must be exercised by shipping code. Orphaned
entitlements are a documented rejection.

| Entitlement | Must be justified by |
|---|---|
| `com.apple.developer.healthkit` | Real HealthKit reads/writes + both usage descriptions |
| `com.apple.developer.in-app-payments` | Apple Pay integration |
| `aps-environment` | A real push implementation with server-side sending |
| `com.apple.developer.associated-domains` | A live, reachable `apple-app-site-association` file served over HTTPS at `https://<domain>/.well-known/apple-app-site-association`, `Content-Type: application/json`, no redirects |
| `com.apple.developer.networking.vpn.api` | 5.4 — organization account required |
| `com.apple.developer.networking.networkextension` | Declared extension types actually implemented |
| `com.apple.developer.family-controls` / Screen Time | Apple approval + 4.10 compliance |
| `com.apple.developer.icloud-container-identifiers` | Actual CloudKit/iCloud usage |
| `com.apple.developer.applesignin` | Sign in with Apple actually implemented (4.8) |
| `com.apple.security.application-groups` | Extensions or a widget that share data |
| `keychain-access-groups` | Actual shared keychain use |

Also: **`get-task-allow` must be `false`** in a distribution build. A debuggable binary is
rejected/blocked at upload.

---

## 6. Binary hygiene checks

- **Private API usage (2.5.1)** — Apple runs static analysis over your binary looking for
  private selectors and symbols. Never call `_`-prefixed system selectors, never use
  `NSClassFromString` to reach private classes, never link private frameworks.
  Grep your source and your vendored SDKs.
- **UIWebView** — removed. Any residual reference (often in an old ad SDK) fails upload.
- **IPv6-only (2.5.5)** — Apple's review network is NAT64/DNS64 with no IPv4. Any hardcoded
  IPv4 literal, `AF_INET`-only socket, or IPv4-only backend fails. Test with macOS's
  *Internet Sharing ▸ NAT64 network* or `networkQuality`-style NAT64 test rig.
- **Debug artifacts** — no `NSLog` of credentials, no debug menus reachable in release, no
  `#if DEBUG` blocks accidentally compiled into Release, no test/staging URLs.
- **Symbol/dSYM** — upload dSYMs; missing symbols isn't a rejection but makes crash triage
  impossible when App Review sends you a crash log.
- **App thinning / bitcode** — bitcode is deprecated; strip it.
- **Executable size** — the uncompressed binary must be under 4 GB and each architecture
  slice under the per-slice limits.
- **Launch screen** — a storyboard-based launch screen is required for correct scaling on
  modern devices; missing it makes the app letterbox and reads as "unfinished" (4.0).

---

## 7. Encryption & export compliance
Set `ITSAppUsesNonExemptEncryption`:
- `false` — you only use HTTPS/TLS and Apple-provided crypto. This is the common case.
- `true` — you implement or ship your own non-exempt cryptography; you then need to supply
  export compliance docs (and per-year self-classification) in App Store Connect.

France requires an additional declaration for apps using encryption distributed in the
French storefront.

---

## 8. App Store Connect submission-time gates (2026)

| Gate | Requirement |
|---|---|
| **Age rating questionnaire** | The updated questionnaire (in-app controls, capabilities, medical/wellness topics, violent themes) had to be answered by **January 31, 2026**. Unanswered → submission is interrupted. New tiers: **4+, 9+, 13+, 16+, 18+**. AI assistants/chatbots must be accounted for in the frequency answers. |
| **App Privacy nutrition label** | Complete, and consistent with the privacy manifest and actual traffic. |
| **Privacy Policy URL** | Required for every app. Must be live, non-PDF, and reachable. |
| **Terms of Use (EULA)** | Required when you sell auto-renewable subscriptions. Apple's standard EULA or your own URL. |
| **DSA trader status (EU)** | Required for EU storefront distribution. Missing → removed from EU storefronts. |
| **Content rights** | Declare whether you display third-party content. |
| **Government/regulated declarations** | Banking, HealthKit research, gambling, cannabis, VPN, MDM, kids — extra documentation. |
| **Accessibility Nutrition Labels** | Declare which accessibility features the app supports (VoiceOver, Voice Control, Larger Text, Sufficient Contrast, Reduced Motion, Dark Interface, Captions, Differentiate Without Color Alone). Claiming support you don't have is a metadata accuracy issue under 2.3. |
| **Export compliance** | See §7. |
| **Notes for Review** | Demo credentials, feature walkthrough, hardware/region requirements, and justification for any unusual permission. |
| **Attachment** | Screen recordings and licence documents where relevant. |

---

## 9. Screenshots & assets

- **Required**: iPhone 6.9"/6.5" display size **and** iPad 13"/12.9" if you support iPad.
  Apple scales down for smaller devices; extra sizes are optional but let you tailor.
- 1–10 screenshots per size, per localization.
- Must show the **actual app in use** (2.3.3) — not a login screen, not pure marketing art.
- Must be **4+ appropriate** (2.3.8) regardless of the app's rating.
- No device frames that misrepresent the platform; no other-platform imagery (2.3.10).
- App previews: 15–30 s, screen capture of the app only.
- App icon: 1024×1024 PNG, **no alpha channel**, no transparency, sRGB or P3, no rounded
  corners baked in.
- Localized screenshots must match the localized listing.

---

## Sources
- [Upcoming requirements — Apple Developer](https://developer.apple.com/news/upcoming-requirements/)
- [Updated age ratings in App Store Connect — Apple Developer News](https://developer.apple.com/news/?id=ks775ehf)
- [Privacy manifest files — Apple Developer Documentation](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Reminder: Privacy requirement for app submissions starts May 1 — Apple Developer News](https://developer.apple.com/news/?id=pvszzano)
- [Apple updates minimum SDK requirements for App Store apps — 9to5Mac](https://9to5mac.com/2026/02/03/apple-to-update-minimum-sdk-requirements-for-all-app-store-submissions/)
