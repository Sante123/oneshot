# Content Policy — UGC, AI, Kids, and Regulated Categories

These are judgment-heavy rules. The scanner can detect *whether the required controls
exist*; a human or an agent must judge *whether the content itself is acceptable*.

---

## 1. User-Generated Content — the four controls

Both stores require the same four things. If your app lets users post, upload, comment,
message, name things publicly, or share profiles, **all four must exist and be reachable**:

| # | Control | Apple 1.2 | Play VI | Implementation bar |
|---|---|---|---|---|
| 1 | **Filter objectionable content** | Required | Required | Automated moderation (keyword/classifier) applied *before* content is publicly visible, or a pre-publication review queue |
| 2 | **Report mechanism** | Required, with **timely responses** | Required | Report control **on every piece of content and every user profile** — not buried in Settings. ≤ 2 taps. Must produce a real ticket someone reads |
| 3 | **Block abusive users** | Required | Required | Per-user block, reachable from the content and the profile. Blocking must actually hide content both ways |
| 4 | **Published contact information** | Required | Required | An email or form the user can reach without an account; also in the store listing |

Plus:
- **24-hour takedown commitment.** Apple explicitly expects abusive content and the user who
  posted it to be **ejected within 24 hours** of a report. State this in your review notes
  and in your terms.
- **Terms of service acceptance** at sign-up defining objectionable content (Play VI).
- **Age gating** for content exceeding the app's rating (Apple 1.2.1(a), 4.7.5).
- **Anonymous/random pairing chat** is heavily restricted — Apple 1.2 rejects
  Chatroulette-style and anonymous chat outright; Play's July 2026 update added
  requirements for anonymous/random chat apps involving minors.
- **Child Safety Standards (Play)** for social and dating apps: published anti-CSAE
  standards, in-app CSAE reporting, CSAM handling, legal compliance, and a **declared
  safety point of contact** in Play Console.

**Reviewer note template for UGC apps** — include this verbatim in Notes for Review:

> This app includes user-generated content. Moderation controls:
> • Automated filtering: {describe classifier/keyword system} applied before content is
>   visible to other users.
> • Reporting: every post and profile has a "Report" action ({exact path}). Reports enter
>   {tool} and are triaged within 24 hours.
> • Blocking: every profile and post has a "Block user" action ({exact path}); blocked users'
>   content is hidden bidirectionally.
> • Contact: {email} is published in-app at {path} and in the store listing.
> • Terms: users must accept the Community Guidelines at {URL} before posting.
> • We remove violating content and eject the offending user within 24 hours of a report.

---

## 2. AI features — the current enforcement frontier

### Apple
- **5.1.2(i) (Nov 2025):** sharing personal data with **third-party AI** requires explicit
  disclosure and consent. If user content goes to an external model, say so and get consent.
- **1.1 / age rating:** an AI assistant's *possible outputs* count toward the age rating.
  The updated questionnaire asks about frequency of mature content; answer for what the
  model can produce, not what you intend.
- **1.1.6:** an AI feature must not misrepresent what it can do. "AI doctor", "AI lawyer",
  "AI therapist" claims run into 1.4.1 and 2.3.1.
- **4.3(b) (June 2026):** apps that are thin wrappers around a model API, indistinguishable
  from what's widely available, are rejected as low-effort. **This clause was written in
  response to AI-assisted app submissions.** A chat UI over an API is not a product.
- **4.7:** if you host third-party chatbots/mini-apps, you are responsible for all of them.
- **1.2 / UGC:** AI-generated content shown to other users is UGC — all four controls apply.
- **Deepfakes:** generating likenesses of real, named people is rejected (1.1, 5.2).

### Google Play (Policy IX — AI-Generated Content)
Apps that generate AI content must:
1. Comply with all restricted-content policies — the model must not produce CSAE, violent
   extremism, NCII, etc.
2. **Provide an in-app reporting/flagging mechanism in the context where AI content
   appears.**
3. **Use those reports to inform filtering and moderation.**

Also: no promoting AI to generate restricted content, and the app description must not
overstate capability.

### Practical AI compliance checklist
- [ ] Input and output moderation (provider moderation endpoint + your own policy layer)
- [ ] "Report this response" control **on each AI message**
- [ ] Reports feed a real review queue
- [ ] Rate limiting and abuse prevention
- [ ] Disclosure screen before first use: which provider, what is sent, what is retained
- [ ] Consent recorded; a way to opt out or delete conversation history
- [ ] Privacy policy names the AI processor(s)
- [ ] Data safety / nutrition label declares User Content as **collected and shared**
- [ ] Age rating answered for the model's possible output
- [ ] Prompt-injection and jailbreak resistance tested against the store's restricted
      categories (self-harm, weapons, CSAE, medical advice)
- [ ] Visible "AI can make mistakes" disclaimer, and no medical/legal/financial advice
      framing
- [ ] Refusal behavior for real-person likenesses
- [ ] The app does something beyond the raw model — otherwise 4.3(b)

---

## 3. Kids and Families

### Apple Kids Category (1.3 + 5.1.4)
- No links out, no purchasing, no third-party ads/analytics (narrow contextual exception),
  no PII or device info to third parties.
- **Parental gate** for anything that leaves the safe space. A parental gate is a
  skill-based challenge (multi-digit math, "swipe to unlock" with reading) — **it is not
  parental consent for data collection**.
- Privacy policy required; COPPA/GDPR-K compliance required.
- Requirements survive later updates even if you deselect the category.
- Apps **not** in the Kids Category must not imply a child audience in name, subtitle, icon,
  screenshots, or description.

### Google Play Families
- Complete **Target audience and content** honestly. Play reclassifies apps whose icon,
  art style, characters, or subject matter appeal to children.
- **Families self-certified ad SDKs only**; no interest-based advertising or remarketing to
  children; no AAID collection from children.
- No non-approved SDKs in child-directed apps at all.
- Content must be age-appropriate; UGC controls are stricter.
- Neutral age screen where a mixed audience is claimed.

### Both
- If the audience is mixed, implement a **neutral age screen** (no pre-filled defaults, not
  skippable by "just tap next") and branch behavior by declared age.
- Never collect precise location from children.
- No social features for children without moderation and parental controls.

---

## 4. Regulated categories — required documentation

| Category | Apple | Play |
|---|---|---|
| **Health / medical** | 1.4.1: disclose data & methodology; **cannot claim sensor-only measurement of x-rays, blood pressure, temperature, blood glucose, blood oxygen**; remind users to consult a doctor; submit regulatory clearance | Health apps declaration; medical-device self-declaration; extended privacy disclosure; no health misinformation |
| **Health research** | 5.1.3: informed consent + **IRB/ethics approval, provable on request** | IRB documentation required |
| **Banking / financial** | 5.1.1(ix): must be a **legal entity**, not an individual account | Financial features declaration; per-country licensing |
| **Lending** | 3.2.2(ix): ≤36% APR, ≥60 days | III.B: no ≤60-day full repayment; no contacts/storage permissions; per-country licence docs |
| **Trading / FOREX / CFD** | 3.2.2(viii): binary options banned; licensing in every jurisdiction | Financial features declaration |
| **Crypto** | 3.1.5: org account for wallets; licensed exchanges; no on-device mining; no task rewards | Certified exchanges/wallets; no on-device mining; no earning-potential promotion |
| **Gambling / real-money gaming** | 5.3: **free app**, licensed per geography, **geo-fenced**, no IAP, official rules stating Apple is not a sponsor | Licensed operator, free download, AO rating, under-18 blocking, responsible-gambling display, geo-restriction; DFS needs a separate application |
| **Cannabis** | 5.1.1(ix): geo-restricted to legal jurisdictions; licensed dispensaries only | **Prohibited regardless of legality** |
| **Pharmacy / prescriptions** | 1.4.3: licensed pharmacies only | No prescription sales without a prescription; no unapproved substances |
| **VPN** | **5.4: organization account required**; NEVPNManager; no data sale, ever | VPN service declaration; no traffic redirection for other purposes |
| **MDM / device management** | 5.5: enterprise/education/government submitters; Apple must grant the capability; no data sale | Device management policy |
| **Dating** | 1.1.4 (no hookup apps in the pornographic sense); age gate | Age-restricted functionality; child-safety standards |
| **News** | — | News app self-declaration |
| **Government** | — | Government apps declaration + affiliation proof |
| **Contact tracing / public health** | Apple entitlement | "Disease Prevention and Public Health" designation, government affiliation |

**Rule of thumb:** if your category appears in this table, attach the licence/registration
document to the submission *proactively*. Waiting to be asked costs a review cycle.

---

## 5. Content judgment checklist (agent-run, not script-run)

Ask these of the actual app content and the actual model behavior:

- Could any screen, string, or asset be read as targeting a protected group? (1.1.1)
- Is there realistic violence, gore, or weapon glorification? (1.1.2, 1.1.3)
- Any sexual content, and is it gated appropriately for the declared rating? (1.1.4)
- Any religious content quoted or characterized inaccurately? (1.1.5)
- Any feature that is fake, joke, or prank — including "for entertainment only" framing?
  (1.1.6)
- Does the app reference a current conflict, disaster, or epidemic? (1.1.7)
- Any medical claim, measurement, or dosage calculation? (1.4.1, 1.4.2)
- Any encouragement of drugs, alcohol, tobacco, vaping, or reckless activity? (1.4.3–1.4.5)
- Any third-party IP: logos, characters, music, fonts, screenshots, scraped data? (5.2)
- Does the app enable downloading media from YouTube/SoundCloud/etc.? (5.2.3 — hard no)
- Does the icon, name, or UI resemble another app or an Apple/Google product? (4.1, 5.2.5)
- Is the app meaningfully different from what already exists? (4.3(b))
- Is the app more than a website wrapper? (4.2)
- Does anything require a review/rating/download to unlock? (3.2.2(x), 5.6.1)
- Are there any dormant, hidden, feature-flagged, or geo-gated behaviors the reviewer
  cannot see? (2.3.1)

---

## Sources
- [App Review Guidelines §1 Safety and §4.7 — Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- [Apple's new App Review guidelines clamp down on apps sharing personal data with third-party AI — TechCrunch](https://techcrunch.com/2025/11/13/apples-new-app-review-guidelines-clamp-down-on-apps-sharing-personal-data-with-third-party-ai)
- [Apple tightens App Review Guidelines against apps that "do not add value" — 9to5Mac](https://9to5mac.com/2026/06/09/apple-tightens-app-review-guidelines-against-apps-that-do-not-add-value-to-the-app-store/)
- [Developer Program Policy §IX AI-Generated Content — Play Console Help](https://support.google.com/googleplay/android-developer/answer/16944162?hl=en)
