import UIKit
import AVFoundation
import StoreKit
import AppTrackingTransparency
import UserNotifications

final class AppDelegate: UIResponder, UIApplicationDelegate {
    let baseURL = "https://api.ledgerly.app"
    let privacyPolicyURL = "https://ledgerly.app/privacy-policy"
    let termsOfUseURL = "https://ledgerly.app/terms-of-use"

    func start() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert]) { _, _ in }
        let session = AVCaptureSession()
        _ = session
        UserDefaults.standard.set(true, forKey: "onboarded")
        ATTrackingManager.requestTrackingAuthorization { _ in }
    }

    func createAccount(email: String, password: String) {}
    func deleteAccount() async throws {}
}
