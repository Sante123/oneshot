import SwiftUI
import StoreKit

struct PaywallView: View {
    var body: some View {
        VStack {
            Text("Go Premium")
            Text("$9.99")
            Button("Subscribe") { Task { try? await Product.products(for: ["pro"]) } }
        }
    }
}
