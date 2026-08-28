# Submission Playbook — Reviewer Notes, Demo Accounts, Testing, Appeals

The scanner catches what is mechanically checkable. This file covers the part that
determines whether a *human* reviewer approves you on the first pass.

---

## 1. The reviewer's actual experience

An App Review reviewer spends roughly 5–15 minutes with your app. They:
1. Read your **Notes for Review** first.
2. Install on a **physical device**, often an older model, often on a constrained network,
   often in a **NAT64/IPv6-only** lab environment.
3. Try to log in with whatever you gave them.
4. Tap around looking for the features your metadata claims.
5. Trigger every permission prompt and read the purpose strings.
6. Hit the paywall.
7. Look for the privacy policy, account deletion, and — for UGC — report/block.

Every one of those steps is a rejection opportunity. Optimize for **the reviewer finding
things quickly**.

A Play reviewer's flow is more automated (pre-launch report on real devices, static
analysis, traffic analysis) plus human review of your **App content declarations** and, for
sensitive permissions, a **demo video**.

---

## 2. Notes for Review — the highest-leverage artifact

Use this structure. Fill every bracket. Delete nothing.

```
=== DEMO ACCOUNT ===
Username: reviewer@example.com
Password: ReviewPass2026!
2FA: disabled for this account  (or: use code 000000 / no 2FA required)
Notes: This account is pre-populated with sample data and does not expire.
       It is not rate-limited. Multiple concurrent sessions are allowed.

=== HOW TO REACH EACH FEATURE ===
1. [Feature name]  -> Launch > Tap "X" in the tab bar > Tap "Y"
2. [Feature name]  -> Profile > Settings > "Z"
3. [Paywall]       -> Home > "Upgrade" button (top right)
4. [Account deletion] -> Profile > Settings > Account > Delete Account
5. [Privacy policy]   -> Profile > Settings > About > Privacy Policy
6. [Report content]   -> Long-press any post > "Report"     (UGC apps)
7. [Block user]       -> Any profile > "..." > "Block"      (UGC apps)

=== WHAT'S NEW IN THIS BUILD ===
[Specific description of every new feature. Generic text is rejected under 2.3.1(a).]

=== PERMISSIONS AND WHY ===
- Camera: used at [screen] to [purpose]. Optional; app works without it.
- Location (When In Use): used at [screen] to [purpose]. Optional.
- [etc. — one line per permission, with the screen it's requested from]

=== IN-APP PURCHASES ===
Products: [list product IDs]. All are Ready to Submit and attached to this version.
Sandbox testing: sign in with a Sandbox Apple ID; purchases are free in sandbox.
Restore Purchases: Settings > Restore Purchases (works without being signed in).

=== THIRD-PARTY / AI SERVICES ===
[If applicable] User-entered text in the [feature] is sent to [provider] for processing.
This is disclosed on first use at [screen] and the user must consent before any data is
sent. It is described in our privacy policy at [URL] under "[section]".

=== REQUIREMENTS AND LIMITATIONS ===
- Minimum OS: [version]
- Requires: [hardware / region / external account], if any
- The app is fully functional on IPv6-only networks.
- No VPN, allowlist, or special network is required to reach our backend.

=== REGULATED CATEGORY DOCUMENTATION ===  (delete if not applicable)
Attached: [licence / registration / IRB approval / authorization letter]
Jurisdictions: [list]. The app is geo-restricted to those jurisdictions.

=== CONTACT ===
[Name], [email], [phone with country code], timezone [X], typical response < 4 hours.
```

**Google Play equivalent** goes in **App content ▸ App access**: pick "All or some
functionality is restricted", then add an instruction set per gated area with credentials
and steps. For background location, all-files access, SMS/Call Log, and accessibility
services, also attach a **demo video URL** (unlisted YouTube is fine) showing the prominent
disclosure and the feature in use.

---

## 3. Demo account requirements (Apple 2.1)

- [ ] Credentials are **live and tested from a device that has never used your app**.
- [ ] The account **does not expire** during review (set a long expiry or no expiry).
- [ ] **2FA disabled**, or a static bypass code provided. SMS 2FA to your phone is the
      classic failure — the reviewer can't receive it.
- [ ] Pre-populated with realistic data so empty states don't look like a broken app.
- [ ] Has any **premium entitlement** the reviewer needs to see paid features (or explain
      how to purchase in sandbox).
- [ ] Not rate-limited, not IP-restricted, not geo-restricted.
- [ ] Works with **multiple concurrent sessions** (reviewers may share it).
- [ ] Backend is **production or production-equivalent** and will stay up for the whole
      review window — including weekends.
- [ ] If your app requires an invite code, phone verification, or KYC, provide a bypass and
      say so explicitly.

---

## 4. Pre-submission test matrix

Run this before every submission. Most 2.1 rejections die here.

| # | Test | Pass criteria |
|---|---|---|
| 1 | Clean install on a **physical device**, oldest supported OS | Launches, no crash |
| 2 | Clean install, **newest** OS (including current beta) | Launches, no crash |
| 3 | Launch with **no network** | Graceful error, no crash, no infinite spinner |
| 4 | Launch on **IPv6-only / NAT64** network (Apple review network) | Fully functional |
| 5 | **Deny every permission** when prompted | App remains usable; no dead ends |
| 6 | **Deny ATT** | No IDFA read, no fingerprinting fallback, app still works |
| 7 | Reach every feature named in the description | All reachable |
| 8 | Purchase flow in **sandbox**, including cancel and interrupt | Entitlement granted; no hang |
| 9 | **Restore Purchases** from a fresh install, signed out | Works |
| 10 | Account creation → **account deletion** → data gone | Works in-app |
| 11 | Privacy policy link from inside the app | Opens, loads, correct content |
| 12 | UGC: report + block, from content and profile | Both reachable in ≤ 2 taps |
| 13 | **Dark mode** and **Dynamic Type / large font** on every screen | No clipped or invisible text |
| 14 | **Landscape** and iPad multitasking (if supported) | No broken layout |
| 15 | **VoiceOver / TalkBack** on primary flows | Elements labelled, navigable |
| 16 | Background → foreground after 10 min | State restored, no crash |
| 17 | Low storage / low memory | Graceful |
| 18 | Play **pre-launch report** on all offered devices | Zero crashes/ANRs |
| 19 | Release build with **R8/minification enabled** | No reflection crashes |
| 20 | Anti-tamper / root / emulator / Play Integrity checks | Do **not** block review devices |
| 21 | Every localization | No placeholder or untranslated strings |
| 22 | Screenshot audit against the current build | Every screenshot still accurate |

---

## 5. Timing and process

| | Apple | Google Play |
|---|---|---|
| Typical review time | ~24–48 h; 90% within 24 h | A few hours to 7 days; **new personal accounts and sensitive categories take longer** |
| First submission of a new app | Slower than updates | Slowest; often several days |
| Expedited review | Request via Apple's form; genuine emergencies only, sparingly | No formal expedite |
| Rejection response | "App Review" message in App Store Connect citing a guideline | Policy email + Play Console Policy status |
| Resubmission | Reply in App Store Connect, or upload a new build | New release on the track |
| Appeal | App Review Board (for guideline interpretation) | Play Console appeal form |
| Strikes | Repeated violations risk Developer Program removal | 3-strike account enforcement |

**Never** submit a first release on a Friday, before a holiday, or in the week before
WWDC/Google I/O.

**Phased release** (Apple) / **staged rollout** (Play) — use them. They don't affect review,
but they limit blast radius.

---

## 6. When you get rejected

### Do this, in order
1. **Read the exact guideline number.** Everything hinges on it.
2. **Look at the attached screenshots/video** in App Store Connect's Resolution Center —
   reviewers usually attach evidence.
3. **Reproduce it in the exact configuration named** — device model, OS version, network,
   region, account.
4. Decide: is this a **fix** or a **misunderstanding**?
   - Fix → change the code/metadata, upload a new build, reply describing exactly what
     changed and where to see it.
   - Misunderstanding → reply **in Resolution Center without a new build**, with a
     step-by-step walkthrough and a screen recording. Do not re-upload; that resets the
     queue.
5. **Reply within the same thread.** A new submission loses the reviewer's context.

### Reply template

```
Hello,

Thank you for the review. Regarding Guideline [X.Y.Z]:

[If fixed:]
We have addressed this in build [N]. Specifically:
- [Change 1] — visible at [exact navigation path]
- [Change 2] — visible at [exact navigation path]
A screen recording demonstrating the corrected behavior is attached.

[If clarifying:]
We believe this may be a misunderstanding. [Feature] is reachable at [exact path].
We were unable to reproduce [issue] on [device/OS]; attached is a screen recording of
the flow on [device/OS] showing [outcome]. Could you confirm the device, OS version,
and network conditions used, and whether the demo account [email] was used?

Demo account (verified working as of [date/time UTC]):
  Username: [x]  Password: [y]  2FA: disabled

Please let us know if any further information would help.
[Name], [role], [email]
```

### Escalation
- **App Review Board** — for guideline *interpretation* disputes, not bug fixes. Use once,
  with a clear argument and precedent (similar approved apps).
- **Apple Developer Support phone call** — often faster than three message round-trips.
- **Play appeal form** — one shot; include evidence and a remediation description.
- Never argue, never repeat submissions without changes, never contact reviewers outside
  the official channels (5.6 Developer Code of Conduct).

---

## 7. Repeat-offender risk

Both stores track patterns:
- Apple: "egregious or repeated" violations of 2.3.1, 4.3, 5.6 → removal from the Developer
  Program. Related accounts are linked (5.6.4).
- Play: **3 strikes** across your account can permanently terminate it, and Google links
  accounts by device, payment instrument, and signing key.

The practical implication: it is far cheaper to over-prepare one submission than to burn
cycles. That is the entire premise of this skill.

---

## Sources
- [App Review — Apple Developer](https://developer.apple.com/distribute/app-review/)
- [App Review Guidelines §2.1, §5.6 — Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- [Developer Program Policy — Play Console Help](https://support.google.com/googleplay/android-developer/answer/16944162?hl=en)
