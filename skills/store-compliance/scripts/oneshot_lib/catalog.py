"""Static knowledge tables used by the deterministic checks.

Everything here is derived from the reference documents in ../references/.
When a store changes a rule, update the reference doc AND this table.
"""
from __future__ import annotations

# --------------------------------------------------------------------------
# Version floors. Verified 2026-08-19 — re-check with `oneshot verify-deadlines`.
# --------------------------------------------------------------------------
FLOORS = {
    "verified_on": "2026-08-19",
    "apple_build_sdk_major": 26,          # Xcode 26 / iOS 26 SDK, mandatory 2026-04-28
    "play_target_sdk": 36,                # Android 16, deadline 2026-08-31
    "play_target_sdk_existing": 35,       # discoverability floor
    "play_target_sdk_wear": 35,
    "play_target_sdk_tv": 34,
    "play_billing_major": 8,              # deadline 2026-08-31
    "so_page_align": 16384,               # 16 KB, in force since 2025-11-01
    "deadlines": {
        "play_target_sdk_36": "2026-08-31",
        "play_billing_8": "2026-08-31",
        "play_extension": "2026-11-01",
        "apple_xcode_26": "2026-04-28",
        "apple_age_rating": "2026-01-31",
        "play_dev_verification_wave1": "2026-09-30",
        "play_contacts_picker": "2027-01-01",
    },
}

# --------------------------------------------------------------------------
# iOS: API usage -> required Info.plist purpose string.
# key = plist key, value = (regex matching API usage, human name)
# --------------------------------------------------------------------------
IOS_PURPOSE_STRINGS = {
    "NSCameraUsageDescription": (
        r"AVCaptureDevice|AVCaptureSession|UIImagePickerControllerSourceType\.camera"
        r"|sourceType\s*=\s*\.camera|ARSession|ARSCNView|ImagePicker\.launchCamera"
        r"|CameraController|requestCameraPermission|Permission\.camera",
        "camera",
    ),
    "NSMicrophoneUsageDescription": (
        r"AVAudioRecorder|AVAudioSession.*record|AVMediaType\.audio|requestRecordPermission"
        r"|SFSpeechAudioBufferRecognitionRequest|Permission\.microphone|\.microphone\b",
        "microphone",
    ),
    "NSPhotoLibraryUsageDescription": (
        r"PHPhotoLibrary|PHAsset(?!Collection)|PHImageManager"
        r"|UIImagePickerControllerSourceType\.photoLibrary|Permission\.photoLibrary",
        "photo library (read)",
    ),
    "NSPhotoLibraryAddUsageDescription": (
        r"UIImageWriteToSavedPhotosAlbum|PHPhotoLibrary\.shared\(\)\.performChanges"
        r"|creationRequestForAsset|saveToPhotos|Permission\.photoLibraryAddOnly",
        "photo library (write)",
    ),
    "NSLocationWhenInUseUsageDescription": (
        r"requestWhenInUseAuthorization|CLLocationManager|Geolocator|Geolocation"
        r"|Permission\.locationWhenInUse",
        "location (when in use)",
    ),
    "NSLocationAlwaysAndWhenInUseUsageDescription": (
        r"requestAlwaysAuthorization|allowsBackgroundLocationUpdates\s*=\s*true"
        r"|startMonitoringSignificantLocationChanges|Permission\.locationAlways",
        "location (always)",
    ),
    "NSContactsUsageDescription": (
        r"CNContactStore|CNContactFetchRequest|ABAddressBook|Permission\.contacts",
        "contacts",
    ),
    "NSCalendarsFullAccessUsageDescription": (
        r"EKEventStore|requestFullAccessToEvents|Permission\.calendarFullAccess",
        "calendar",
    ),
    "NSRemindersFullAccessUsageDescription": (
        r"requestFullAccessToReminders|EKReminder",
        "reminders",
    ),
    "NSMotionUsageDescription": (
        r"CMMotionManager|CMPedometer|CMMotionActivityManager|Permission\.sensors",
        "motion & fitness",
    ),
    "NSHealthShareUsageDescription": (
        r"HKHealthStore|HKObjectType|HealthKit", "HealthKit (read)",
    ),
    "NSHealthUpdateUsageDescription": (
        r"HKHealthStore\(\)\.save|requestAuthorization\(toShare", "HealthKit (write)",
    ),
    "NSBluetoothAlwaysUsageDescription": (
        r"CBCentralManager|CBPeripheralManager|CoreBluetooth|FlutterBluePlus",
        "Bluetooth",
    ),
    "NSLocalNetworkUsageDescription": (
        r"NWBrowser|NetService|Bonjour|_tcp\.local|multicast", "local network",
    ),
    "NSSpeechRecognitionUsageDescription": (
        r"SFSpeechRecognizer|SFSpeechURLRecognitionRequest", "speech recognition",
    ),
    "NSFaceIDUsageDescription": (
        r"LAContext|deviceOwnerAuthenticationWithBiometrics|LocalAuthentication"
        r"|BiometricPrompt|local_auth",
        "Face ID",
    ),
    "NSUserTrackingUsageDescription": (
        r"ATTrackingManager|requestTrackingAuthorization|advertisingIdentifier"
        r"|ASIdentifierManager|AppTrackingTransparency|getTrackingStatus",
        "App Tracking Transparency",
    ),
    "NSAppleMusicUsageDescription": (
        r"MPMediaLibrary|MPMediaQuery|MusicKit|SKCloudServiceController", "media library",
    ),
    "NSSiriUsageDescription": (r"INPreferences|SiriKit|INIntent", "Siri"),
    "NSNearbyInteractionUsageDescription": (r"NINearbyObject|NISession", "nearby interaction"),
}

# Vague purpose-string text that reviewers reject under 5.1.1(ii)
VAGUE_PURPOSE_PATTERNS = [
    r"^\s*$",
    r"^(this app|the app|app)\s+(needs|requires|uses|wants)\s+(access to\s+)?(your\s+)?\w+\.?\s*$",
    r"^(required|needed|necessary)( for (the )?app( to work| to function)?)?\.?\s*$",
    r"^(we need|we require|we use)\s+\w+\.?\s*$",
    r"^\w+\s+access\.?\s*$",
    r"^(permission|access)\s*$",
    r"^\$\(.*\)$",
    r"todo|tbd|xxx|placeholder|lorem",
]

# --------------------------------------------------------------------------
# iOS: Required Reason APIs -> category + valid reason codes
# --------------------------------------------------------------------------
REQUIRED_REASON_APIS = {
    "NSPrivacyAccessedAPICategoryFileTimestamp": {
        "pattern": (
            r"\.creationDate\b|\.modificationDate\b|contentModificationDateKey"
            r"|creationDateKey|getattrlistbulk|\bgetattrlist\b|\bfgetattrlist\b"
            r"|NSFileCreationDate|NSFileModificationDate|NSURLContentModificationDateKey"
            r"|NSURLCreationDateKey|\bfstatat\b|\blstat\b"
        ),
        "reasons": ["DDA9.1", "C617.1", "3B52.1", "0A2A.1"],
        "default": "C617.1",
        "human": "file timestamp APIs",
    },
    "NSPrivacyAccessedAPICategorySystemBootTime": {
        "pattern": r"systemUptime|mach_absolute_time|ProcessInfo\(\)\.systemUptime",
        "reasons": ["35F9.1", "8FFB.1"],
        "default": "35F9.1",
        "human": "system boot time APIs",
    },
    "NSPrivacyAccessedAPICategoryDiskSpace": {
        "pattern": (
            r"volumeAvailableCapacity|volumeTotalCapacityKey|systemFreeSize|systemSize"
            r"|\bstatfs\b|\bstatvfs\b|\bfstatfs\b|\bfstatvfs\b"
        ),
        "reasons": ["85F4.1", "E174.1", "7D9E.1"],
        "default": "E174.1",
        "human": "disk space APIs",
    },
    "NSPrivacyAccessedAPICategoryActiveKeyboards": {
        "pattern": r"activeInputModes|UITextInputMode\.activeInputModes",
        "reasons": ["3EC4.1", "54BD.1"],
        "default": "54BD.1",
        "human": "active keyboard APIs",
    },
    "NSPrivacyAccessedAPICategoryUserDefaults": {
        "pattern": r"UserDefaults|NSUserDefaults|CFPreferences|SharedPreferences\.ios",
        "reasons": ["CA92.1", "1C8F.1", "AC6B.1", "C56D.1"],
        "default": "CA92.1",
        "human": "UserDefaults",
    },
}

# --------------------------------------------------------------------------
# iOS: entitlement -> code that must exist to justify it (guideline 2.5.4)
# --------------------------------------------------------------------------
ENTITLEMENT_JUSTIFICATION = {
    "com.apple.developer.healthkit": r"HKHealthStore|HealthKit",
    "com.apple.developer.in-app-payments": r"PKPaymentAuthorization|ApplePay|PKPaymentRequest",
    "aps-environment": r"registerForRemoteNotifications|UNUserNotificationCenter|FirebaseMessaging|messaging\(\)",
    "com.apple.developer.associated-domains": r"NSUserActivity|continueUserActivity|universalLink|applinks",
    "com.apple.developer.applesignin": r"ASAuthorizationAppleIDProvider|SignInWithApple|AppleIDButton",
    "com.apple.developer.networking.vpn.api": r"NEVPNManager|NETunnelProvider",
    "com.apple.developer.networking.networkextension": r"NEFilter|NETunnelProvider|NEHotspot|NEDNSProxy",
    "com.apple.developer.family-controls": r"FamilyControls|ManagedSettings|DeviceActivity",
    "com.apple.developer.icloud-container-identifiers": r"CKContainer|NSUbiquitousKeyValueStore|NSFileManager.*ubiquity",
    "com.apple.developer.siri": r"INPreferences|INIntent|SiriKit",
    "com.apple.developer.homekit": r"HMHomeManager|HomeKit",
    "com.apple.developer.nfc.readersession.formats": r"NFCNDEFReaderSession|NFCTagReaderSession",
}

# UIBackgroundModes -> code that must exist (guideline 2.5.4)
BACKGROUND_MODE_JUSTIFICATION = {
    "audio": r"AVAudioSession|AVPlayer|AVAudioEngine|setCategory\(\.playback",
    "location": r"allowsBackgroundLocationUpdates|startMonitoringSignificantLocationChanges|startUpdatingLocation",
    "voip": r"CallKit|CXProvider|PKPushRegistry",
    "fetch": r"BGAppRefreshTask|setMinimumBackgroundFetchInterval|performFetchWithCompletionHandler",
    "processing": r"BGProcessingTask",
    "remote-notification": r"didReceiveRemoteNotification|UNNotificationServiceExtension|contentAvailable",
    "bluetooth-central": r"CBCentralManager",
    "bluetooth-peripheral": r"CBPeripheralManager",
    "external-accessory": r"EAAccessoryManager",
    "nearby-interaction": r"NISession",
}

# --------------------------------------------------------------------------
# Android: restricted permissions -> (severity, policy, required declaration)
# --------------------------------------------------------------------------
ANDROID_RESTRICTED_PERMISSIONS = {
    "android.permission.ACCESS_BACKGROUND_LOCATION": (
        "BLOCKER", "Play XII Restricted Permissions / Location",
        "Location permissions declaration in Play Console + a demo video showing the "
        "prominent disclosure and the feature. Remove the permission unless the feature "
        "is impossible with foreground-only location.",
    ),
    "android.permission.READ_SMS": (
        "BLOCKER", "Play XII SMS and Call Log permissions",
        "Only for a registered default SMS handler. Use the SMS Retriever API for OTP "
        "autofill instead. Permissions declaration required.",
    ),
    "android.permission.RECEIVE_SMS": (
        "BLOCKER", "Play XII SMS and Call Log permissions",
        "Use the SMS Retriever API instead; otherwise a Permissions declaration is required.",
    ),
    "android.permission.READ_CALL_LOG": (
        "BLOCKER", "Play XII SMS and Call Log permissions (July 2026 update)",
        "Only for a registered default dialer/assistant. As of July 2026 READ_CALL_LOG may "
        "NOT be used for account verification via phone call — use the Digital Credentials "
        "API or SMS Retriever API.",
    ),
    "android.permission.WRITE_CALL_LOG": (
        "BLOCKER", "Play XII SMS and Call Log permissions",
        "Only for a registered default dialer. Declaration required.",
    ),
    "android.permission.PROCESS_OUTGOING_CALLS": (
        "HIGH", "Play XII SMS and Call Log permissions",
        "Deprecated; use CallRedirectionService or remove.",
    ),
    "android.permission.MANAGE_EXTERNAL_STORAGE": (
        "BLOCKER", "Play XII All files access",
        "Only for file managers, backup/restore, anti-virus, document management, on-device "
        "search, or disk/file encryption. Otherwise use the Storage Access Framework or "
        "MediaStore. Declaration required.",
    ),
    "android.permission.READ_MEDIA_IMAGES": (
        "HIGH", "Play XII Photo and Video permissions (in force 2025-05-28)",
        "Use the Android Photo Picker. Broad access requires a declaration proving the app's "
        "core purpose is managing all photos/videos. A custom in-app picker does not qualify.",
    ),
    "android.permission.READ_MEDIA_VIDEO": (
        "HIGH", "Play XII Photo and Video permissions (in force 2025-05-28)",
        "Use the Android Photo Picker. Broad access requires a declaration.",
    ),
    "android.permission.READ_EXTERNAL_STORAGE": (
        "MEDIUM", "Play XII Storage permissions",
        "Deprecated from API 33. Use scoped media permissions or the Photo Picker, and set "
        "android:maxSdkVersion=\"32\".",
    ),
    "android.permission.READ_CONTACTS": (
        "HIGH", "Play XII Contacts permission (effective January 2027, API 37+)",
        "Use the Android Contact Picker (Intent.ACTION_PICK_CONTACTS). Broad access requires "
        "a declaration explaining why the picker is insufficient.",
    ),
    "android.permission.WRITE_CONTACTS": (
        "MEDIUM", "Play XII Contacts permission",
        "Justify or remove; prefer the picker/insert intent.",
    ),
    "android.permission.QUERY_ALL_PACKAGES": (
        "HIGH", "Play XII Package (App) visibility",
        "Only for antivirus, file managers, browsers, device management, or banking "
        "anti-fraud. Replace with a specific <queries> block. Declaration required.",
    ),
    "android.permission.BIND_ACCESSIBILITY_SERVICE": (
        "BLOCKER", "Play XII Accessibility API",
        "Only for genuine accessibility use, disclosed in-app and in the store listing. "
        "Automation, ad-blocking, or overlay use results in removal.",
    ),
    "android.permission.REQUEST_INSTALL_PACKAGES": (
        "HIGH", "Play Device and Network Abuse",
        "Only for app stores, file managers, backup/restore, or enterprise device management.",
    ),
    "android.permission.SYSTEM_ALERT_WINDOW": (
        "MEDIUM", "Play Device and Network Abuse / Deceptive Behavior",
        "Overlays must not obscure ads, permission dialogs, or system UI. Justify or remove.",
    ),
    "android.permission.PACKAGE_USAGE_STATS": (
        "HIGH", "Play XI Personal and Sensitive User Data",
        "Requires prominent disclosure and a core use case (digital wellbeing, parental "
        "control, device management).",
    ),
    "android.permission.USE_EXACT_ALARM": (
        "HIGH", "Play Exact alarm permission",
        "Only for alarm clock and calendar apps. Use SCHEDULE_EXACT_ALARM and handle denial.",
    ),
    "android.permission.SCHEDULE_EXACT_ALARM": (
        "MEDIUM", "Play Exact alarm permission",
        "Handle the user denying it; do not treat it as guaranteed.",
    ),
    "android.permission.USE_FULL_SCREEN_INTENT": (
        "MEDIUM", "Play Full-screen intent permission",
        "Only for calling and alarm apps on API 34+.",
    ),
    "android.permission.RECORD_AUDIO": (
        "MEDIUM", "Play XI.C Prominent Disclosure",
        "Requires prominent disclosure if recording is not obvious from the UI.",
    ),
    "android.permission.CAMERA": (
        "LOW", "Play XI.C Prominent Disclosure",
        "Requires prominent disclosure if capture is not obvious from the UI.",
    ),
    "android.permission.BIND_DEVICE_ADMIN": (
        "HIGH", "Play Device Administration",
        "Enterprise/parental-control use only; requires justification.",
    ),
    "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE": (
        "HIGH", "Play XI Personal and Sensitive User Data",
        "Notification content is sensitive; requires prominent disclosure and a core use case.",
    ),
}

# Permissions a lending app must never request (Play III.B)
LENDING_FORBIDDEN_PERMISSIONS = {
    "android.permission.READ_CONTACTS",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.READ_MEDIA_VIDEO",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.READ_CALL_LOG",
    "android.permission.READ_SMS",
}

# --------------------------------------------------------------------------
# SDK inventory: dependency token -> declaration hints
# --------------------------------------------------------------------------
SDK_DATA_MAP = {
    "firebase-analytics": ("Firebase Analytics", ["Device or Other IDs", "App Interactions"], False),
    "google-analytics": ("Google Analytics", ["Device or Other IDs", "App Interactions"], False),
    "firebase_analytics": ("Firebase Analytics", ["Device or Other IDs", "App Interactions"], False),
    "crashlytics": ("Firebase Crashlytics", ["Crash Logs", "Diagnostics"], False),
    "play-services-ads": ("Google AdMob", ["Device or Other IDs", "Advertising Data"], True),
    "google-mobile-ads": ("Google Mobile Ads", ["Device or Other IDs", "Advertising Data"], True),
    "Google-Mobile-Ads-SDK": ("Google Mobile Ads", ["Device or Other IDs", "Advertising Data"], True),
    "facebook-android-sdk": ("Meta SDK", ["Device or Other IDs", "App Interactions"], True),
    "FBSDKCoreKit": ("Meta SDK", ["Device or Other IDs", "App Interactions"], True),
    "appsflyer": ("AppsFlyer", ["Device or Other IDs", "App Interactions"], True),
    "AppsFlyerFramework": ("AppsFlyer", ["Device or Other IDs", "App Interactions"], True),
    "adjust": ("Adjust", ["Device or Other IDs", "App Interactions"], True),
    "branch": ("Branch", ["Device or Other IDs", "App Interactions"], True),
    "singular": ("Singular", ["Device or Other IDs", "App Interactions"], True),
    "amplitude": ("Amplitude", ["Device or Other IDs", "App Interactions"], False),
    "mixpanel": ("Mixpanel", ["Device or Other IDs", "App Interactions"], False),
    "posthog": ("PostHog", ["Device or Other IDs", "App Interactions"], False),
    "sentry": ("Sentry", ["Crash Logs", "Diagnostics"], False),
    "bugsnag": ("Bugsnag", ["Crash Logs", "Diagnostics"], False),
    "datadog": ("Datadog RUM", ["Diagnostics", "App Interactions"], False),
    "revenuecat": ("RevenueCat", ["Purchase History", "User IDs"], False),
    "Purchases": ("RevenueCat", ["Purchase History", "User IDs"], False),
    "adapty": ("Adapty", ["Purchase History", "User IDs"], False),
    "superwall": ("Superwall", ["Purchase History", "User IDs"], False),
    "onesignal": ("OneSignal", ["Device or Other IDs", "App Interactions"], False),
    "braze": ("Braze", ["Device or Other IDs", "App Interactions"], False),
    "clevertap": ("CleverTap", ["Device or Other IDs", "App Interactions"], False),
    "iterable": ("Iterable", ["Email", "Device or Other IDs"], False),
    "intercom": ("Intercom", ["Email", "Name", "User Content"], False),
    "zendesk": ("Zendesk", ["Email", "Name", "User Content"], False),
    "stripe": ("Stripe", ["Payment Info"], False),
    "braintree": ("Braintree", ["Payment Info"], False),
    "mapbox": ("Mapbox", ["Approximate/Precise Location"], False),
    "play-services-maps": ("Google Maps", ["Approximate/Precise Location"], False),
    "GoogleMaps": ("Google Maps", ["Approximate/Precise Location"], False),
    "smartlook": ("Smartlook (session replay)", ["User Content", "App Interactions"], False),
    "fullstory": ("FullStory (session replay)", ["User Content", "App Interactions"], False),
    "clarity": ("Microsoft Clarity (session replay)", ["User Content", "App Interactions"], False),
}

TRACKING_SDK_TOKENS = [k for k, v in SDK_DATA_MAP.items() if v[2]]

# Third-party AI/LLM endpoints (Apple 5.1.2(i) Nov 2025; Play XI.A July 2026)
AI_ENDPOINT_PATTERN = (
    r"api\.openai\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com"
    r"|api\.cohere\.ai|api\.mistral\.ai|api\.together\.xyz|api\.groq\.com"
    r"|api\.replicate\.com|openai\.azure\.com|api\.perplexity\.ai|api\.deepseek\.com"
    r"|bedrock-runtime\.[a-z0-9-]+\.amazonaws\.com|api\.stability\.ai|api\.elevenlabs\.io"
)

# Placeholder text that fails Apple 2.3.1 / Play XIII
PLACEHOLDER_PATTERN = (
    r"lorem ipsum|\bTODO\b|\bTBD\b|\bFIXME\b|\bXXXX?\b|PLACEHOLDER|placeholder text"
    r"|\bUntitled\b|coming soon|example\.com|foo ?bar|asdfasdf|\btest test\b"
    r"|Insert .{0,20} here|YOUR_[A-Z_]+_HERE|CHANGEME|<your .{0,20}>"
)

# Secrets that Play's scanner blocks
SECRET_PATTERNS = {
    "Google API key": r"AIza[0-9A-Za-z_\-]{35}",
    "AWS access key": r"AKIA[0-9A-Z]{16}",
    "Private key block": r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----",
    "OpenAI key": r"sk-[A-Za-z0-9]{20,}",
    "Anthropic key": r"sk-ant-[A-Za-z0-9\-_]{20,}",
    "GitHub token": r"gh[pousr]_[A-Za-z0-9]{36,}",
    "Slack token": r"xox[baprs]-[A-Za-z0-9-]{10,}",
    "Stripe live key": r"sk_live_[A-Za-z0-9]{20,}",
    "Firebase server key": r"AAAA[A-Za-z0-9_-]{7}:[A-Za-z0-9_-]{140,}",
}

# Non-production endpoints that must not ship (Apple 2.1)
STAGING_PATTERN = (
    r"https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+"
    r"|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|[a-z0-9.-]*\b(staging|stage|dev|test|qa|sandbox|preprod|uat)\b[a-z0-9.-]*\.)"
)

# Signals used to infer app characteristics
SIGNALS = {
    "accounts": r"signUp|createAccount|registerUser|/auth/register|createUserWithEmail"
                r"|signInWithEmail|SignUpView|RegistrationActivity|useAuth\(\)|Auth\.auth\(\)",
    "account_deletion": r"deleteAccount|delete_account|/account/delete|deleteUser|removeAccount"
                        r"|DeleteAccount|accountDeletion|closeAccount",
    "iap": r"StoreKit|SKProduct|Product\.products|BillingClient|queryProductDetails"
           r"|purchases\.purchase|RevenueCat|Purchases\.shared|in_app_purchase",
    "restore": r"restorePurchases|restoreCompletedTransactions|AppStore\.sync\(\)"
               r"|queryPurchasesAsync|restoreTransactions|Purchases\.shared\.restore",
    "paywall": r"[Pp]aywall|SubscriptionView|UpgradeView|PremiumScreen|PricingView|SubscribeSheet",
    "ugc": r"createPost|uploadPost|submitComment|sendMessage|newComment|publishPost"
           r"|/posts\b|/comments\b|chatRoom|feedItem|UserProfile.*follow",
    "ugc_report": r"reportContent|reportPost|reportUser|flagContent|/report\b|ReportSheet"
                  r"|report_abuse|reportAbuse",
    "ugc_block": r"blockUser|blockedUsers|/block\b|BlockUser|muteUser",
    "privacy_policy": r"privacy[-_ ]?policy|privacyPolicyURL|PRIVACY_POLICY",
    "terms": r"terms[-_ ]?of[-_ ]?(use|service)|EULA|termsURL|TERMS_URL",
    "social_login": r"GIDSignIn|GoogleSignIn|LoginManager|FBSDKLoginKit|signInWithFacebook"
                    r"|TwitterAuthProvider|WeChatSDK|LinkedInSDK|OAuthProvider\(providerID",
    "sign_in_with_apple": r"ASAuthorizationAppleIDProvider|SignInWithAppleButton"
                          r"|apple_sign_in|AppleAuthProvider|OAuthProvider\(providerID:\s*\"apple",
    "webview_shell": r"WKWebView|WebView\(|android\.webkit\.WebView|InAppWebView|webview_flutter",
    "external_payment": r"stripe\.com|checkout\.stripe|paypal\.com|braintreepayments"
                        r"|razorpay|paddle\.com|lemonsqueezy|/checkout/session",
    "ads": r"GADBannerView|GADInterstitialAd|AdView|InterstitialAd|MaxAdView|IronSource"
           r"|AppLovin|UnityAds|admob",
    "review_prompt": r"requestReview|SKStoreReviewController|ReviewManager|InAppReview",
    "custom_review_prompt": r"rate ?us|rate this app|leave a review|5 ?stars",
    "kids": r"\bkids?\b|children|parental|toddler|preschool|nursery",
    "lending": r"\bloan\b|lending|borrow|APR|repayment|creditLine|payday",
    "health": r"HealthKit|HealthConnect|blood ?pressure|glucose|heart ?rate|bloodOxygen|spo2",
    "vpn": r"NEVPNManager|VpnService|WireGuard|OpenVPN|IKEv2",
    "gambling": r"casino|betting|wager|sportsbook|lottery|roulette|slots|poker",
    "crypto": r"web3|ethers|wallet_?connect|solana|bitcoin|blockchain|erc20",
    "location_bg": r"allowsBackgroundLocationUpdates|ACCESS_BACKGROUND_LOCATION"
                   r"|startMonitoringSignificantLocationChanges",
    "att": r"ATTrackingManager|requestTrackingAuthorization|AppTrackingTransparency",
    "idfa": r"advertisingIdentifier|ASIdentifierManager|AdvertisingIdClient|getAdvertisingIdInfo",
    "prominent_disclosure": r"prominent ?disclosure|DisclosureDialog|consent(Screen|Dialog|Sheet)"
                            r"|PrivacyConsent|DataUseDisclosure|beforeWeContinue",
    "ipv4_literal": r"[\"'](?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)[\"'/:]",
    "private_api": r"NSClassFromString\(\s*@?\"_|performSelector\(\s*NSSelectorFromString\(\s*@?\"_"
                   r"|valueForKey:\s*@\"_|\bLSApplicationWorkspace\b|\bSBSLaunchApplication",
    "uiwebview": r"\bUIWebView\b",
    "integrity_gate": r"SafetyNet|IntegrityManager|PlayIntegrity|isJailbroken|isRooted"
                      r"|RootBeer|jailbreakDetect|emulatorDetect|isEmulator",
}
