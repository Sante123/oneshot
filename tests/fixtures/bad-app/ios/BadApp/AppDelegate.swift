import UIKit
import AVFoundation
import CoreLocation
import StoreKit
import AdSupport

final class AppDelegate: UIResponder, UIApplicationDelegate {
    let base = "https://api-staging.badapp.com"
    let fallback = "192.0.2.14"
    let locationManager = CLLocationManager()

    func start() {
        locationManager.requestWhenInUseAuthorization()
        let session = AVCaptureSession()          // camera, no purpose string
        _ = session
        let idfa = ASIdentifierManager.shared().advertisingIdentifier   // no ATT
        _ = idfa
        let uptime = ProcessInfo.processInfo.systemUptime               // required reason API
        _ = uptime
        UserDefaults.standard.set(true, forKey: "seen")                 // required reason API
    }

    func createAccount(email: String, password: String) { /* signUp */ }
}
