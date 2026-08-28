# Google Play — Technical & Build-Level Rejection Surface

Deterministic, mechanically checkable requirements. Last verified: **2026-08-19**.

---

## 1. Target API level — hard deadline

| Track | New apps & updates | Existing apps (discoverability) |
|---|---|---|
| **Phone / tablet / Android Auto** | **API 36 (Android 16) by Aug 31, 2026** | Must reach **API 35** by Aug 31, 2026 or become invisible to users on newer devices |
| **Wear OS** | API 35 by Aug 31, 2026 | API 34 by Aug 31, 2026 |
| **Android TV** | API 34 (since Aug 31, 2025) | API 33 by Aug 31, 2026 |
| **Android Automotive OS** | API 35 by Aug 31, 2026 | API 32 by Aug 31, 2026 |
| **Android XR** | API 34 by Aug 31, 2026 | — |

Extension available to **November 1, 2026** via Play Console ▸ Policy status.

**Check:** `targetSdk` (or `targetSdkVersion`) in `app/build.gradle[.kts]`, or
`android { defaultConfig { targetSdk = 36 } }`. Expo: `expo-build-properties` plugin.
Flutter: `android/app/build.gradle`. React Native: `android/build.gradle` `ext.targetSdkVersion`.

**Do not just bump the number.** Each API level brings behavior changes that break apps in
review. Re-test at minimum: runtime permissions, scoped storage, foreground services, exact
alarms, notification permission (`POST_NOTIFICATIONS`, API 33+), predictive back, and
`PendingIntent` mutability flags.

---

## 2. 16 KB page size — required

Android 15+ devices can boot with 16 KB memory pages. **Google Play requires all apps
targeting Android 15+ (API 35+) that contain native code to support 16 KB page sizes**
(enforced from **November 1, 2025** for new apps and updates).

- Applies to any app containing `.so` files — including transitively via React Native,
  Flutter, Unity, and most media/crypto/ML libraries.
- **Check:** every `lib/*/**.so` in the AAB/APK must have `p_align` ≥ 16384 (0x4000).

```bash
# Extract and check alignment
unzip -o app-release.aab -d /tmp/aab
find /tmp/aab -name '*.so' -print0 | while IFS= read -r -d '' so; do
  align=$(objdump -p "$so" | awk '/LOAD/ {print $NF; exit}')
  echo "$so -> $align"
done
# Or use the official check
# https://developer.android.com/guide/practices/page-sizes
```

- **Fix:** AGP 8.5.1+ with `android.experimental.enableNewResourceShrinker`, NDK r27+,
  and for CMake add:
  `-DCMAKE_SHARED_LINKER_FLAGS="-Wl,-z,max-page-size=16384"`.
  For prebuilt third-party `.so` files you must upgrade the dependency — you cannot realign
  someone else's binary.
- Also ensure uncompressed shared libraries: `android:extractNativeLibs="false"` and
  `useLegacyPackaging = false`.

---

## 3. 64-bit requirement
Every APK/AAB must include **arm64-v8a** (and x86_64 if you ship x86). 32-bit-only uploads
are rejected. Check `lib/` directories in the bundle.

---

## 4. App Bundle (AAB) requirement
New apps must be published as **Android App Bundles**. APK-only uploads are rejected for new
apps. Max compressed download size per install is 200 MB (use Play Asset Delivery /
Play Feature Delivery beyond that).

---

## 5. `AndroidManifest.xml` — rejection-prone attributes

| Attribute / element | Requirement |
|---|---|
| `android:debuggable` | Must be **absent or false** in the release build. Present-and-true → rejected. |
| `android:allowBackup` | Default `true` backs up app data to the cloud. For apps handling sensitive data, set `false` or configure `dataExtractionRules` / `fullBackupContent`. |
| `android:usesCleartextTraffic` | Should be `false` (default from API 28). If `true`, expect a security warning and a Data-safety inconsistency. Use a Network Security Config with per-domain exceptions instead. |
| `android:exported` | **Required explicitly** on every `activity`/`service`/`receiver` with an intent filter (API 31+). Missing → build failure; wrongly `true` → security rejection. |
| `<uses-permission>` | Every permission must map to a shipped feature. Unused permissions are the #1 Data-safety mismatch source. |
| `<uses-permission-sdk-23>` / `maxSdkVersion` | Use to scope legacy storage permissions. |
| `<queries>` | Declare specific packages/intents instead of `QUERY_ALL_PACKAGES`. |
| `android:foregroundServiceType` | Required for every foreground service (API 34+), and each type must map to an approved use case. `location` FGS for geofencing is no longer approved — use the Geofence API. |
| `com.google.android.play.billingclient.version` metadata | Must be present and ≥ 8.0.0 when using Play Billing. |
| `<uses-feature android:required="true">` | Over-declaring (e.g. `android.hardware.camera` required) silently excludes devices and contradicts your listing. |
| `android:networkSecurityConfig` | Prefer over blanket cleartext. |
| `INTERNET` permission | Required if you make network calls (obvious, but frequently missing in stripped manifests). |
| `POST_NOTIFICATIONS` | Required from API 33 to show notifications; must be requested at runtime with rationale. |

---

## 6. Gradle / signing / build config

- **Signing:** Play App Signing is effectively mandatory for new apps. Upload key ≠ app
  signing key. Keep the upload keystore backed up; a lost upload key requires a reset
  request.
- **Version codes** must strictly increase. `versionCode` is an integer; plan your scheme.
- **`minifyEnabled` / R8** — enable for release, and **verify your ProGuard/R8 rules don't
  strip reflection-dependent code**. A crash caused by over-aggressive minification is the
  most common "works in debug, rejected in review" failure.
- **`shrinkResources true`** with `minifyEnabled true`.
- Never ship `BuildConfig.DEBUG`-gated developer menus in release.
- Remove test/staging endpoints from release build types. Check `buildConfigField`,
  `manifestPlaceholders`, `.env`, `google-services.json` (make sure it's the production
  Firebase project), and any `*.properties` in the repo.
- **Secrets**: API keys checked into the APK are extractable. Play's automated scan flags
  known secret formats (Google API keys, AWS keys, Firebase secrets) and will send a
  security warning that blocks the release.
- **Dependency vulnerabilities**: Play blocks releases containing SDK versions with known
  critical vulnerabilities (Play SDK Index). Check the Play Console ▸ SDKs page.

---

## 7. Pre-launch report
Play runs your app on real devices before publishing to a track. Fix everything it
reports before promoting to production:
- **Stability** — crashes/ANRs on any tested device is a de-facto blocker.
- **Accessibility** — touch target size, contrast, missing content labels.
- **Security & trust** — insecure TLS, exposed components, known-vulnerable SDKs.
- **Performance** — startup time, frozen frames.

**Android vitals thresholds (bad-behavior, affects discoverability and can force removal):**
- User-perceived crash rate > **1.09%**
- User-perceived ANR rate > **0.47%**
These are the "bad behavior" thresholds; exceeding them demotes your app in Play and can
trigger a warning on the store listing.

---

## 8. Play Integrity / app signing
If you use Play Integrity API, ensure your response handling degrades gracefully — a hard
block on `MEETS_DEVICE_INTEGRITY` failure will make your app unusable on the reviewer's
emulator/lab device and reads as "app doesn't work".

**This is a real and under-appreciated rejection cause:** anti-tamper, root detection,
emulator detection, and SafetyNet/Integrity gating frequently block Google's own test
infrastructure and Apple's review devices. Provide a bypass path documented in your review
notes, or relax the check.

---

## 9. Stack-specific technical notes

### React Native
- `android/app/build.gradle` → `targetSdkVersion`, `compileSdkVersion` from
  `android/build.gradle` `ext`.
- Hermes vs JSC: Hermes `.so` must be 16 KB aligned — use RN 0.76+ / matching Hermes.
- **Code push / OTA updates:** shipping *new native functionality* over the air violates
  Apple 2.5.2. JS-only bug fixes and content updates to existing features are accepted in
  practice; new features that were never reviewed are not. Keep OTA payloads to changes you
  would have been comfortable submitting.
- `react-native-permissions` — configure only the permissions you use; the pod/manifest
  merge otherwise adds every purpose string placeholder.

### Expo / EAS
- `app.json` / `app.config.js` → `ios.infoPlist`, `ios.entitlements`,
  `android.permissions`, `android.blockedPermissions`.
- **`android.permissions` does not remove permissions added by libraries** — use
  `android.blockedPermissions` to strip them, or they end up in the merged manifest and
  contradict your Data safety form.
- `expo-build-properties` sets `targetSdkVersion`, `compileSdkVersion`, and iOS
  `deploymentTarget`.
- EAS build image must be on Xcode 26+ for iOS submissions after April 28, 2026.
- Expo's `ios.config.usesNonExemptEncryption` maps to `ITSAppUsesNonExemptEncryption`.
- `expo-tracking-transparency` is required if any dependency touches IDFA.

### Flutter
- `android/app/build.gradle` → `targetSdk`, `minSdk`, `ndkVersion`.
- `ios/Runner/Info.plist` for purpose strings; `ios/Runner/Runner.entitlements`.
- Flutter's engine `.so` files require Flutter 3.24+ for 16 KB page-size support.
- `flutter build appbundle --release` — verify `--obfuscate --split-debug-info` doesn't
  break plugins.
- Many Flutter plugins add permissions transitively; run
  `./gradlew :app:processReleaseManifest` and read `app/build/intermediates/merged_manifests/`
  to see the *actual* manifest that ships.

### Unity
- IL2CPP + ARM64 required; check `Player Settings ▸ Target Architectures`.
- Unity Ads / analytics packages add permissions and data collection you must declare.
- 16 KB alignment requires Unity 6 / 2022.3.x LTS with the 16 KB patch.

### Kotlin Multiplatform / native
- Standard Gradle/Xcode rules apply to each target.

---

## 10. The merged manifest is the source of truth

Never audit `src/main/AndroidManifest.xml` alone. Library manifests merge in.

```bash
./gradlew :app:processReleaseManifest
cat app/build/intermediates/merged_manifest/release/AndroidManifest.xml
# or, from a built artifact:
bundletool dump manifest --bundle=app-release.aab
aapt2 dump permissions app-release.apk
```

Do the same on iOS: inspect the **built** `Info.plist` inside the `.app`, because
CocoaPods/SPM resource bundles and build-setting substitutions change it.

```bash
plutil -p "Payload/YourApp.app/Info.plist"
codesign -d --entitlements :- "Payload/YourApp.app"
```

---

## Sources
- [Target API level requirements for Google Play apps — Play Console Help](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en)
- [Support 16 KB page sizes — Android Developers](https://developer.android.com/guide/practices/page-sizes)
- [Prepare your apps for Google Play's 16 KB page size compatibility requirement — Android Developers Blog](https://android-developers.googleblog.com/2025/05/prepare-play-apps-for-devices-with-16kb-page-size.html)
- [Google Play Billing Library version deprecation — Android Developers](https://developer.android.com/google/play/billing/deprecation-faq)
