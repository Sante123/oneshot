# Notes for Review — template

Paste the Apple section into **App Store Connect ▸ App Review Information ▸ Notes**, and
the Play section into **Play Console ▸ App content ▸ App access**.

Fill every `[bracket]`. A reviewer who cannot find a feature assumes it does not exist.

---

## APPLE — Notes for Review

```
=== DEMO ACCOUNT ===
Username: [reviewer@yourapp.com]
Password: [WorkingPassword2026!]
2FA: [disabled for this account]   (or: static code [000000])
Notes: Pre-populated with sample data. Does not expire. Not rate-limited.
       Multiple concurrent sessions allowed. Verified working on [date, time UTC].

=== HOW TO REACH EACH FEATURE ===
1. [Feature]           -> Launch > [tab] > [screen]
2. [Feature]           -> Profile > Settings > [item]
3. Paywall             -> [exact path]
4. Restore Purchases   -> [exact path]  (works while signed out)
5. Delete Account      -> [exact path]
6. Privacy Policy      -> [exact path]
7. Report content      -> [exact path]   (UGC apps)
8. Block user          -> [exact path]   (UGC apps)
9. [Hardware/region-gated feature] -> [exact path + what is required]

=== WHAT'S NEW IN THIS BUILD ===
[Describe each new feature specifically. Generic descriptions are rejected under
 guideline 2.3.1(a). Name the screens a reviewer must visit to see each one.]

=== PERMISSIONS AND WHY ===
- [Camera]: requested at [screen] to [purpose]. Optional; the app works if denied.
- [Location, When In Use]: requested at [screen] to [purpose]. Optional.
- [Notifications]: requested at [screen]; the app is fully usable without them.
- [one line per permission the app requests]

=== IN-APP PURCHASES ===
Product IDs: [list]. All are Ready to Submit and attached to this version.
Sandbox: sign in with a Sandbox Apple ID; purchases are free in sandbox.
Restore Purchases is at [exact path] and works without being signed in.
Subscription terms (price, period, renewal, trial) are displayed on the paywall at
[exact path] above the purchase button.

=== THIRD-PARTY AND AI SERVICES ===       (delete if not applicable)
[Feature] sends [exactly what data] to [provider] for [purpose]. This is disclosed on
first use at [screen], and the user must consent before anything is sent. It is
described in our privacy policy at [URL] under "[section heading]". Users can [opt out
/ delete history] at [exact path].

=== USER-GENERATED CONTENT ===            (delete if not applicable)
- Filtering: [describe the classifier/keyword system] runs before content becomes
  visible to other users.
- Reporting: every post and profile has a "Report" action at [exact path]. Reports enter
  [tool] and are triaged within 24 hours.
- Blocking: every profile and post has "Block user" at [exact path]; blocked users'
  content is hidden in both directions.
- Contact: [email] is published in-app at [path] and in the store listing.
- Terms: users accept the Community Guidelines at [URL] before posting.
- We remove violating content and eject the offending user within 24 hours of a report.

=== REQUIREMENTS AND LIMITATIONS ===
- Minimum OS: [version]
- Requires: [hardware / region / external account], if any
- The app is fully functional on IPv6-only (NAT64) networks.
- No VPN, IP allowlist, or special network is required to reach our backend.
- [If the app has anti-tamper/root/integrity checks: describe the review bypass.]

=== REGULATED CATEGORY DOCUMENTATION ===  (delete if not applicable)
Attached: [licence / registration / IRB approval / authorization letter]
Jurisdictions: [list]. The app is geo-restricted to these jurisdictions.

=== CONTACT ===
[Name], [email], [+country phone], timezone [X], typical response under 4 hours.
```

---

## GOOGLE PLAY — App access instructions

In **Play Console ▸ App content ▸ App access**, choose "All or some functionality is
restricted" and add one instruction set per gated area:

```
Instruction name: Sign in
Username: [reviewer@yourapp.com]
Password: [WorkingPassword2026!]
Any other instructions:
  - 2FA is disabled on this account.
  - The account has an active Pro entitlement so all paid screens are reachable.
  - Backend is production and available continuously.
  - Verified working on [date, time UTC].
```

```
Instruction name: [Gated feature name]
Any other instructions:
  1. Sign in with the account above.
  2. [step]
  3. [step]
  The prominent disclosure for [data] appears at step [n]; the runtime permission
  request follows it.
```

**Attach a demo video** (unlisted YouTube is fine) for each of these, if present:
- Background location — showing the disclosure and the feature in use
- All files access (`MANAGE_EXTERNAL_STORAGE`)
- SMS / Call Log
- Accessibility service
- Broad photo/video access
- Anything the reviewer would not find by tapping around

---

## Attachments to prepare

- [ ] Screen recording: sign-in with the demo account on a clean install
- [ ] Screen recording: purchase + **Restore Purchases from a signed-out fresh install**
- [ ] Screen recording: account creation → in-app deletion
- [ ] Screen recording: report and block, from content **and** profile (UGC apps)
- [ ] Screen recording: prominent disclosure before each sensitive permission
- [ ] Licence / registration documents for any regulated category
- [ ] IRB approval for health research
