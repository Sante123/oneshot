"""Project stack detection."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import util


@dataclass
class Project:
    root: Path
    stacks: list = field(default_factory=list)          # native-ios, native-android, react-native, expo, flutter, unity, capacitor
    ios_info_plists: list = field(default_factory=list)
    ios_entitlements: list = field(default_factory=list)
    ios_privacy_manifests: list = field(default_factory=list)
    ios_built_apps: list = field(default_factory=list)
    android_manifests: list = field(default_factory=list)
    android_merged_manifests: list = field(default_factory=list)
    gradle_files: list = field(default_factory=list)
    package_json: Path | None = None
    expo_config: Path | None = None
    pubspec: Path | None = None
    podfile_lock: Path | None = None
    artifacts: list = field(default_factory=list)       # .ipa/.aab/.apk found
    metadata_dirs: list = field(default_factory=list)

    @property
    def has_ios(self) -> bool:
        return bool(self.ios_info_plists or self.ios_built_apps) or "native-ios" in self.stacks

    @property
    def has_android(self) -> bool:
        return bool(self.android_manifests or self.gradle_files)

    def summary(self) -> dict:
        return {
            "root": str(self.root),
            "stacks": self.stacks,
            "ios": {
                "info_plists": [util.rel(p, self.root) for p in self.ios_info_plists],
                "entitlements": [util.rel(p, self.root) for p in self.ios_entitlements],
                "privacy_manifests": [util.rel(p, self.root) for p in self.ios_privacy_manifests],
                "built_apps": [util.rel(p, self.root) for p in self.ios_built_apps],
            },
            "android": {
                "manifests": [util.rel(p, self.root) for p in self.android_manifests],
                "merged_manifests": [util.rel(p, self.root) for p in self.android_merged_manifests],
                "gradle": [util.rel(p, self.root) for p in self.gradle_files],
            },
            "config": {
                "package_json": util.rel(self.package_json, self.root) if self.package_json else None,
                "expo_config": util.rel(self.expo_config, self.root) if self.expo_config else None,
                "pubspec": util.rel(self.pubspec, self.root) if self.pubspec else None,
                "podfile_lock": util.rel(self.podfile_lock, self.root) if self.podfile_lock else None,
            },
            "artifacts": [util.rel(p, self.root) for p in self.artifacts],
            "metadata_dirs": [util.rel(p, self.root) for p in self.metadata_dirs],
        }


def detect(root: Path) -> Project:
    root = root.resolve()
    proj = Project(root=root)

    # --- iOS surfaces -------------------------------------------------------
    proj.ios_info_plists = [
        p for p in util.find_files(root, "Info.plist")
        if "Pods" not in p.parts
    ]
    proj.ios_entitlements = util.find_files(root, "*.entitlements")
    proj.ios_privacy_manifests = util.find_files(root, "PrivacyInfo.xcprivacy")
    proj.ios_built_apps = [p for p in util.find_files(root, "*.app") if p.is_dir()]
    if util.find_files(root, "*.xcodeproj") or util.find_files(root, "*.xcworkspace"):
        proj.stacks.append("native-ios")
    lock = root / "ios" / "Podfile.lock"
    if not lock.exists():
        found = util.find_files(root, "Podfile.lock", limit=3)
        lock = found[0] if found else None
    proj.podfile_lock = lock if lock and lock.exists() else None

    # --- Android surfaces ---------------------------------------------------
    manifests = util.find_files(root, "AndroidManifest.xml")
    proj.android_manifests = [m for m in manifests if "intermediates" not in m.parts]
    proj.android_merged_manifests = [m for m in manifests if "intermediates" in m.parts or "merged_manifest" in str(m)]
    proj.gradle_files = (
        util.find_files(root, "build.gradle") + util.find_files(root, "build.gradle.kts")
    )
    if proj.android_manifests or (root / "settings.gradle").exists() or (root / "settings.gradle.kts").exists():
        if "native-android" not in proj.stacks:
            proj.stacks.append("native-android")

    # --- Cross-platform config ---------------------------------------------
    pkg = root / "package.json"
    if pkg.exists():
        proj.package_json = pkg
        try:
            data = json.loads(util.read_text(pkg) or "{}")
        except json.JSONDecodeError:
            data = {}
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if "expo" in deps:
            proj.stacks.append("expo")
        if "react-native" in deps:
            proj.stacks.append("react-native")
        if "@capacitor/core" in deps:
            proj.stacks.append("capacitor")

    for name in ("app.json", "app.config.js", "app.config.ts", "app.config.json"):
        cand = root / name
        if cand.exists():
            proj.expo_config = cand
            break

    pubspec = root / "pubspec.yaml"
    if pubspec.exists():
        proj.pubspec = pubspec
        proj.stacks.append("flutter")

    if (root / "ProjectSettings" / "ProjectSettings.asset").exists():
        proj.stacks.append("unity")
    if (root / "config.xml").exists() and util.any_match(root, r"<widget[^>]*cordova", {".xml"}):
        proj.stacks.append("cordova")

    # --- Artifacts & metadata ----------------------------------------------
    for pattern in ("*.ipa", "*.aab", "*.apk"):
        proj.artifacts += util.find_files(root, pattern, limit=20)

    for cand in ("fastlane/metadata", "fastlane/metadata/android", "store", "listing", ".appstore"):
        d = root / cand
        if d.exists() and d.is_dir():
            proj.metadata_dirs.append(d)

    if not proj.stacks:
        proj.stacks.append("unknown")
    proj.stacks = sorted(set(proj.stacks))
    return proj
