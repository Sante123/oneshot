# Store Listing Metadata & Assets

Metadata rejections are the cheapest to prevent and the most annoying to receive, because
they cost a full review cycle for something that took 30 seconds to get wrong.

---

## 1. Side-by-side spec table

| Field | Apple App Store | Google Play |
|---|---|---|
| App name / title | **≤ 30 chars**, unique | **≤ 30 chars** |
| Subtitle / short description | Subtitle **≤ 30 chars** | Short description **≤ 80 chars** |
| Description | **≤ 4,000 chars** | **≤ 4,000 chars** |
| Keywords | **≤ 100 chars**, comma-separated, not visible to users | No keyword field — keywords live in the description |
| Promotional text | ≤ 170 chars, editable without a new version | — |
| What's New / Release notes | ≤ 4,000 chars | ≤ 500 chars |
| App icon | **1024×1024 PNG, no alpha, no transparency, no rounded corners** | **512×512 PNG, 32-bit, alpha allowed** |
| Feature graphic | — | **1024×500 PNG/JPG, required** |
| Screenshots | iPhone 6.9" (1320×2868 / 2868×1320) **required**; iPad 13" required if iPad supported. 1–10 per size per locale | 2–8 phone screenshots; 16:9 or 9:16; each side 320–3840 px; long side ≤ 2× short side. Tablet + Wear/TV sets if supported |
| App preview / promo video | 15–30 s, ≤ 3 per size, screen capture only | YouTube URL, no age restriction, no ads on the video |
| Support URL | **Required** | Support email **required**; website optional |
| Marketing URL | Optional | — |
| Privacy Policy URL | **Required** | **Required** |
| Terms of Use (EULA) | Required for subscriptions | — |
| Copyright | Required | — |
| Category | 1 primary + 1 secondary | 1 category + up to 5 tags |
| Content rating | Age-rating questionnaire (**4+, 9+, 13+, 16+, 18+** since 2025/26) | **IARC questionnaire — mandatory**; unrated apps not permitted |
| Contact info for review | Name, phone, email + Notes for Review | App access instructions + contact email |

---

## 2. Naming rules that get apps rejected

**Both stores:**
- No competitor or third-party trademarks ("for WhatsApp", "Instagram Downloader",
  "ChatGPT Client") unless licensed — Apple 5.2.1, Play X.C.
- No pricing or promotional text ("Free", "50% Off", "Sale", "#1", "Best").
- No keyword stuffing in the name ("Photo Editor - Collage Maker, Filters, Effects, Pic
  Grid, Camera, Beauty") — Apple 2.3.7, Play XIV.
- No emoji or unusual Unicode in the title (Play), no misleading Unicode look-alikes.
- No "For Kids"/"For Children" outside the Kids Category (Apple 2.3.8 / 5.1.4(b)).
- No implying store ranking, editorial features, or Apple/Google endorsement
  (Apple 5.2.4, Play XIII).
- The **installed app's display name must match the store name** (Apple 2.3.8).

**Apple-specific:** subtitle follows all name rules and must not contain unverifiable claims
("the fastest", "the most secure"). Apple may unilaterally edit keywords.

**Play-specific:** the **developer name** must not impersonate another entity, and must be
the verified legal entity for organization accounts.

---

## 3. Screenshot rules

- **Must show the app actually in use.** Not a splash screen, not a login screen, not pure
  marketing artwork (Apple 2.3.3).
- Must reflect the **current build**. Screenshots showing features you removed, or a UI you
  redesigned, is a 2.3 rejection.
- **Must be 4+ appropriate on Apple regardless of the app's own age rating** (2.3.8): no
  gore, no guns pointed at people, no drugs, no nudity — even in an 18+ app.
- No other-platform imagery, Android UI, or "Get it on Google Play" badges in Apple assets
  (Apple 2.3.10), and vice versa.
- Text overlays and device frames are fine; frames must not misrepresent the device or add
  fake system UI.
- Localized screenshots should be genuinely localized. Machine-translated listings are a
  Play policy violation.
- Play feature graphic: **no device frames, no cropped text, no fake buttons, no store
  badges, no ratings/awards claims.**

---

## 4. Description rules

- Describe what the app does, accurately (Apple 2.3, Play XIII/XIV).
- **Disclose in-app purchases and subscriptions in the description** (Apple 2.3.2).
- Any feature that requires hardware, a subscription, a region, or an account must say so.
- No unverifiable superlatives, no medical claims without evidence, no "virus scanner"
  claims on iOS.
- No links to other platforms' stores; no references to Android/iOS by name in the other
  store's listing.
- No testimonials attributed to real people you didn't get permission from.
- Do not include a changelog in the description.
- Play: no repeated keyword blocks, no irrelevant brand references, no "download now"
  spam blocks.

**Required disclosures to include where applicable:**
- "Subscription required for X" / "Some features require a subscription"
- "Requires an account"
- "Requires [hardware device]"
- "Available only in [regions]"
- "Contains ads"
- "Uses AI; content may be inaccurate" (increasingly expected for LLM features)
- Loot-box odds (Apple 3.1.1)
- Loan terms (Apple 3.2.2(ix), Play III.B)

---

## 5. Localization consistency
- Every localization declared in App Store Connect / Play Console must have complete
  metadata — a half-translated listing reads as unfinished.
- `CFBundleLocalizations` and Play's supported languages must match the store listing set.
- **Purpose strings must be localized** (`InfoPlist.strings`), or non-English reviewers see
  English prompts.
- Placeholder strings (`TODO`, `TBD`, `lorem ipsum`, `XXX`, `PLACEHOLDER`, `Untitled`) in
  *any* locale is a 2.3.1 rejection. Grep every `.strings`, `.xcstrings`, `strings.xml`,
  and listing file.

---

## 6. Age rating / content rating

### Apple (updated questionnaire — mandatory since Jan 31, 2026)
Tiers: **4+, 9+, 13+, 16+, 18+**. The questionnaire now asks about:
- **In-app controls** (parental controls, content filters, communication limits)
- **Capabilities** (in-app purchases, ads, user-generated content, messaging, location
  sharing, unrestricted web access)
- **Medical or wellness topics**
- **Violent themes** — frequency and intensity

**If your app embeds an AI assistant or chatbot, you must answer for what that assistant
can produce**, not just your own content. Under-rating an AI feature is an active
enforcement area.

You may set a **higher** rating than the calculated one if your own policy requires a
minimum age.

### Google Play (IARC)
Mandatory questionnaire producing per-region ratings (ESRB, PEGI, USK, ClassInd, etc.).
**Unrated apps are not permitted on Play** (clarified July 2026). Answer honestly — Play
re-rates apps it believes are misrated and a misrating is a policy violation.

Also complete **Target audience and content**: if children are in your target audience, the
Families policy applies in full.

---

## 7. Declarations checklist

### App Store Connect ▸ App Information / Version
- [ ] Age rating questionnaire (updated version) — **answered**
- [ ] App Privacy nutrition label — complete and consistent
- [ ] Privacy Policy URL — live
- [ ] Terms of Use (EULA) — set if subscriptions
- [ ] Content rights (third-party content) declaration
- [ ] Export compliance (`ITSAppUsesNonExemptEncryption`)
- [ ] **EU DSA trader status** — required for EU storefronts
- [ ] Accessibility Nutrition Label — declare only what you actually support
- [ ] Category + secondary category
- [ ] Pricing & availability, including all storefronts you claim in metadata
- [ ] Sign-in required? → App Review Information demo account filled
- [ ] Notes for Review — see `submission-playbook.md`
- [ ] Attachment — demo video for non-obvious/hardware/regulated features
- [ ] Game Center / regulated-category documentation if applicable

### Play Console ▸ App content
- [ ] Privacy policy URL
- [ ] App access (login credentials / steps for gated features)
- [ ] Ads declaration (contains ads?)
- [ ] **Content rating (IARC)**
- [ ] **Target audience and content** (+ Families if children)
- [ ] News app declaration (if applicable)
- [ ] COVID-19 / contact-tracing (if applicable)
- [ ] **Data safety** — complete, matching SDKs, with account-deletion URL
- [ ] Government apps declaration
- [ ] **Financial features** declaration (loans, crypto, tokenized assets, investing)
- [ ] **Health apps** declaration
- [ ] **Sensitive app permissions** (background location, SMS/Call Log, all-files,
      photo/video, package visibility, accessibility, exact alarms)
- [ ] Advertising ID declaration
- [ ] Child safety standards (social/dating apps)
- [ ] Store listing: title, short & full description, icon, feature graphic, screenshots
- [ ] Countries/regions and pricing
- [ ] Developer verification complete (identity / D-U-N-S)

---

## 8. Asset generation & verification commands

```bash
# Apple icon: verify no alpha channel
sips -g hasAlpha AppIcon-1024.png          # must print hasAlpha: no
python3 -c "from PIL import Image; im=Image.open('AppIcon-1024.png'); print(im.mode, im.size)"
# expect: RGB (1024, 1024)

# Strip alpha if present
python3 - <<'PY'
from PIL import Image
im = Image.open('AppIcon-1024.png').convert('RGBA')
bg = Image.new('RGB', im.size, (255,255,255))
bg.paste(im, mask=im.split()[3])
bg.save('AppIcon-1024.png')
PY

# Play screenshot dimension check
python3 - <<'PY'
from PIL import Image; import sys, glob
for f in glob.glob('screenshots/*.png'):
    w,h = Image.open(f).size
    lo,hi = sorted((w,h))
    ok = 320 <= lo and hi <= 3840 and hi <= 2*lo
    print(("OK " if ok else "BAD"), f, w, h)
PY
```

---

## Sources
- [App Review Guidelines §2.3 Accurate Metadata — Apple Developer](https://developer.apple.com/app-store/review/guidelines/#accurate-metadata)
- [Updated age ratings in App Store Connect — Apple Developer News](https://developer.apple.com/news/?id=ks775ehf)
- [Developer Program Policy — Play Console Help](https://support.google.com/googleplay/android-developer/answer/16944162?hl=en)
