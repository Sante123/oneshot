import SwiftUI
import StoreKit

struct PaywallView: View {
    var body: some View {
        VStack(spacing: 12) {
            Text("Ledgerly Pro")
            Text("$4.99 per month")
            Text("Renews automatically each month unless cancelled at least 24 hours before the period ends.")
            Button("Subscribe") {}
            Button("Restore Purchases") { Task { try? await AppStore.sync() } }
            Link("Terms of Use", destination: URL(string: "https://ledgerly.app/terms-of-use")!)
            Link("Privacy Policy", destination: URL(string: "https://ledgerly.app/privacy-policy")!)
        }
    }
}
