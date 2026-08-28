# Reference Implementations

Working patterns for the four things reviewers most often cannot find. Adapt the copy;
keep the structure.

> These are illustrative implementations, not drop-in libraries. Wire them to your own
> API and design system, and **verify the server side actually does what the UI claims** —
> a Delete Account button that deactivates instead of deleting is still a violation.

---

## 1. Prominent disclosure before a sensitive permission (Play XI.C)

**The bar:** a dedicated screen or dialog, shown **before** the runtime permission
request, that names the data, states the use, makes clear *this app* collects it, and
requires an **affirmative tap**. A toast, a snackbar, an auto-dismissing message, or the
runtime dialog alone does **not** satisfy this.

### Kotlin / Compose

```kotlin
@Composable
fun BackgroundLocationDisclosure(
    onAccept: () -> Unit,
    onDecline: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = { /* deliberately non-dismissible: consent must be affirmative */ },
        title = { Text("Ledgerly collects location in the background") },
        text = {
            Text(
                "To remind you to log an expense when you arrive at a client site, Ledgerly " +
                "collects location data even when the app is closed or not in use. " +
                "This data is used only to trigger your own reminders. It is never sold or " +
                "shared with advertisers.\n\n" +
                "You can use Ledgerly without this — arrival reminders will be off."
            )
        },
        confirmButton = { TextButton(onClick = onAccept) { Text("Allow location") } },
        dismissButton = { TextButton(onClick = onDecline) { Text("No thanks") } },
    )
}

// Only after onAccept:
//   requestPermissions(ACCESS_FINE_LOCATION) -> then ACCESS_BACKGROUND_LOCATION
// Never request the OS permission before the user taps "Allow location".
```

### Swift / SwiftUI

```swift
struct LocationDisclosureSheet: View {
    let onAccept: () -> Void
    let onDecline: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Ledgerly uses your location").font(.title2.bold())
            Text("""
                To tag expenses with where they happened and remind you at client sites, \
                Ledgerly reads your location while you are using the app. Location is stored \
                on your device and in your own account. It is never sold or shared with \
                advertisers.

                You can decline — everything else in Ledgerly keeps working.
                """)
            Button("Allow location", action: onAccept).buttonStyle(.borderedProminent)
            Button("Not now", action: onDecline)
        }
        .padding()
        .interactiveDismissDisabled()
    }
}
```

Checklist: shown before the OS prompt · names the data · states the purpose · names the
app · affirmative tap · a real decline path · the app still works after declining.

---

## 2. In-app account deletion (Apple 5.1.1(v), Play XI.F)

**The bar:** reachable in ≤ 3 taps from settings, labelled "Delete Account", confirms,
then actually deletes server-side. Not an email to support. Not "deactivate".

### Swift

```swift
struct DeleteAccountView: View {
    @State private var confirming = false
    @State private var error: String?

    var body: some View {
        List {
            Section {
                Text("Deleting your account permanently removes your profile, receipts, "
                     "expense reports, and shared folders. This cannot be undone.")
                Text("We keep transaction records for 7 years where tax law requires it. "
                     "Everything else is deleted within 30 days.")
                    .font(.footnote).foregroundStyle(.secondary)
            }
            Section {
                Button("Delete Account", role: .destructive) { confirming = true }
            }
        }
        .navigationTitle("Delete Account")
        .confirmationDialog("Delete your account?", isPresented: $confirming) {
            Button("Delete permanently", role: .destructive) { Task { await delete() } }
            Button("Cancel", role: .cancel) {}
        }
        .alert("Couldn't delete account", isPresented: .constant(error != nil)) {
            Button("OK") { error = nil }
        } message: { Text(error ?? "") }
    }

    private func delete() async {
        do {
            try await API.shared.deleteAccount()   // DELETE /v1/account
            await Session.shared.signOut()          // clear keychain + local DB
        } catch {
            self.error = error.localizedDescription
        }
    }
}
```

Play additionally requires a **web deletion URL** that works without the app installed
and without being signed into the app. Declare it in
**Play Console ▸ App content ▸ Data safety ▸ Account deletion**. A minimal page that
takes an email, verifies ownership by emailed link, and queues the deletion is enough.

---

## 3. UGC report and block (Apple 1.2, Play VI)

**The bar:** report and block reachable in ≤ 2 taps from **both** the content and the
profile; blocking hides content bidirectionally; reports create a real ticket.

### Kotlin

```kotlin
@Composable
fun PostOverflowMenu(post: Post, viewModel: FeedViewModel) {
    var open by remember { mutableStateOf(false) }
    IconButton(onClick = { open = true }) { Icon(Icons.Default.MoreVert, "More options") }
    DropdownMenu(expanded = open, onDismissRequest = { open = false }) {
        DropdownMenuItem(
            text = { Text("Report this post") },
            onClick = { open = false; viewModel.openReportSheet(post.id) },
        )
        DropdownMenuItem(
            text = { Text("Block @${post.author.handle}") },
            onClick = { open = false; viewModel.blockUser(post.author.id) },
        )
    }
}

// ReportSheet asks for a reason (harassment, spam, sexual content, violence,
// self-harm, IP infringement, other), files it to the moderation queue, and
// immediately hides the content for the reporting user.
//
// blockUser() must:
//   - hide the blocked user's content from this user
//   - hide this user's content from the blocked user
//   - prevent messaging in both directions
//   - persist server-side, not just locally
```

Also required: automated filtering before content becomes publicly visible; ToS
acceptance at sign-up; published contact information; and a stated commitment to remove
violating content and eject the offending user **within 24 hours** of a report.

---

## 4. Third-party AI disclosure + consent (Apple 5.1.2(i), Play XI.A / IX)

**The bar:** before the first request leaves the device, name the provider, state exactly
what is sent, and record affirmative consent. Then give a report control on every
generated response.

### Swift

```swift
struct AIConsentView: View {
    @AppStorage("ai_consent_v1") private var consented = false
    let onContinue: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Smart Categories uses an AI service").font(.title2.bold())
            Text("""
                When you use Smart Categories, the merchant name and amount on your receipt \
                are sent to OpenAI to suggest a category. Your name, email, card number, and \
                receipt image are not sent.

                OpenAI processes this data on our behalf and does not use it to train models. \
                See our Privacy Policy for details.

                You can skip this and categorize manually.
                """)
            Link("Privacy Policy", destination: URL(string: "https://ledgerly.app/privacy-policy")!)
            Button("Turn on Smart Categories") { consented = true; onContinue() }
                .buttonStyle(.borderedProminent)
            Button("Not now") { onContinue() }
        }
        .padding()
    }
}
```

And on each generated response:

```swift
HStack {
    Text(response.text)
    Spacer()
    Menu {
        Button("Report this response") { moderation.report(response.id) }
        Button("Copy") { UIPasteboard.general.string = response.text }
    } label: { Image(systemName: "ellipsis") }
}
```

Also required: moderation on inputs and outputs; the provider named in the privacy
policy; User Content declared as **collected and shared** in both stores; and an age
rating that reflects what the model can produce.

---

## 5. Paywall with the required disclosures (Apple 3.1.2(c))

```swift
VStack(spacing: 12) {
    Text("Ledgerly Pro").font(.title.bold())
    Text("Unlimited receipts, multi-currency, and shared team folders.")

    // Everything below must be visible WITHOUT SCROLLING, next to the buy button.
    Text("$4.99 per month")
    Text("7 days free, then $4.99 per month.")            // omit if no trial
    Text("Subscription renews automatically unless cancelled at least 24 hours before "
         "the end of the current period. Manage or cancel in Settings › Apple ID › "
         "Subscriptions.")
        .font(.footnote).foregroundStyle(.secondary)

    Button("Start free trial") { Task { await purchase() } }
        .buttonStyle(.borderedProminent)

    Button("Restore Purchases") { Task { try? await AppStore.sync() } }   // must work signed out

    HStack(spacing: 16) {
        Link("Terms of Use", destination: URL(string: "https://ledgerly.app/terms-of-use")!)
        Link("Privacy Policy", destination: URL(string: "https://ledgerly.app/privacy-policy")!)
    }
    .font(.footnote)
}
```

Both URLs must also be entered in App Store Connect — the paywall links alone are not
sufficient.
