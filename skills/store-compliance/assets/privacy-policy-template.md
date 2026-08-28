# Privacy Policy — template

> **Not legal advice.** This is a structural skeleton covering the sections Apple 5.1.1(i)
> and Google Play XI.E require. Fill it from your **actual** data inventory
> (`data-safety-worksheet.md` §1) and have a lawyer review it before publishing.
> **Never publish a policy describing practices you have not verified in the code** —
> a policy that overstates or understates your collection is worse than no policy.

Publish it as **HTML at a stable HTTPS URL**. Not a PDF. Not a Google Doc. Not a page
visitors can edit. Link it from inside the app *and* in both store listings.

---

# Privacy Policy for [App Name]

**Last updated:** [date]
**Effective:** [date]

## 1. Who we are

[App Name] is operated by [Legal Entity Name], [company registration number],
registered at [address].

- Privacy contact: **[privacy@yourdomain.com]**
- Data Protection Officer / EU representative: [name and contact, if required]

## 2. What this policy covers

This policy covers the [App Name] mobile apps for iOS and Android, and
[website / API / other services].

## 3. Information we collect

### 3.1 Information you give us
| Data | Why | Retention |
|---|---|---|
| Email address | Create and secure your account | Until you delete your account |
| Name (optional) | Personalize the app | Until you delete your account |
| [Receipt images] | [The core feature] | [30 days after deletion] |

### 3.2 Information collected automatically
| Data | Collected by | Why | Retention |
|---|---|---|---|
| Device identifiers | [Firebase Analytics] | Understand feature usage | [14 months] |
| Crash logs and diagnostics | [Crashlytics] | Fix bugs | [90 days] |
| IP address | Our servers | Security and abuse prevention | [30 days] |
| [Advertising ID] | [AdMob] | [Show relevant ads] | [as set by the provider] |

### 3.3 Permissions we request
| Permission | When | What happens if you decline |
|---|---|---|
| Camera | When you photograph a receipt | You can still add expenses manually |
| Location (when in use) | When you tag an expense with a place | Tagging is unavailable |
| Notifications | [when] | [what still works] |

**We do not collect:** [list what you explicitly do not collect — precise background
location, contacts, health data, etc. Only claim this if it is true.]

## 4. Why we use your information

- To provide the service you asked for (contract / app functionality)
- To keep accounts and payments secure (legitimate interest / legal obligation)
- To understand how features are used so we can improve them (consent, where required)
- [To show advertising (consent)]
- To comply with tax, accounting, and other legal obligations

**Legal bases (GDPR/UK GDPR):** [contract, consent, legitimate interests, legal
obligation — map each purpose above].

## 5. Who we share information with

We do **not** sell your personal information.

| Recipient | What they receive | Why | Where | Their policy |
|---|---|---|---|---|
| [Amazon Web Services] | All app data (hosting) | Infrastructure | [region] | [link] |
| [Google Firebase] | Device ID, usage events, crash logs | Analytics, crash reporting | US/EU | [link] |
| [Stripe] | Payment details | Process payments | US/EU | [link] |
| **[OpenAI]** | **[Exactly which fields — e.g. merchant name and amount only]** | **[The AI feature]** | **US** | **[link]** |
| [Law enforcement] | As legally required | Legal obligation | — | — |

**AI processing.** [Describe precisely: which feature, which data leaves the device, which
provider, whether the provider may retain or train on it, and how the user opts out.
Both stores now require this to be explicit.]

## 6. International transfers

[Where data is processed, and the transfer mechanism — Standard Contractual Clauses, EU-US
Data Privacy Framework, adequacy decision.]

## 7. How long we keep information

[Per-category retention. Match §3's retention column.]

## 8. Your rights and choices

Depending on where you live you may have the right to access, correct, delete, port,
restrict, or object to the processing of your personal information, and to withdraw
consent at any time.

**Delete your account and data:**
- **In the app:** Settings ▸ Account ▸ Delete Account
- **On the web:** [https://yourdomain.com/delete-account]
- **By email:** [privacy@yourdomain.com]

Deletion removes all data associated with your account, except records we must keep by
law ([which records, for how long]). We complete deletion within [30] days.

**California residents:** [CCPA/CPRA rights, "Do Not Sell or Share My Personal
Information" link, categories collected and disclosed in the last 12 months.]

**EEA/UK residents:** you may lodge a complaint with your supervisory authority.

## 9. Security

[Encryption in transit and at rest, access controls, retention limits, incident response.
Describe what you actually do.]

## 10. Children

[App Name] is [not directed to children under 13 / directed to children and complies with
COPPA and the Google Play Families policy]. [If child-directed: describe verifiable
parental consent, the absence of behavioral advertising, and data minimization.]

## 11. Changes to this policy

We will post any changes here and update the "Last updated" date. For material changes we
will notify you in the app [and by email] before they take effect.

## 12. Contact

[Legal Entity Name]
[Address]
[privacy@yourdomain.com]

---

## Publishing checklist

- [ ] Live at a stable HTTPS URL, returning 200
- [ ] HTML, not a PDF; not editable by visitors
- [ ] Linked in App Store Connect **and** Play Console
- [ ] Linked inside the app (Settings/About)
- [ ] Every third party in §5 matches the SDK inventory
- [ ] Every data type in §3 matches the App Privacy label and the Data safety form
- [ ] The AI paragraph names the provider and the exact fields sent
- [ ] The account-deletion URL in §8 works without the app installed
- [ ] Reviewed by counsel
