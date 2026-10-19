# Cross-platform build, release and signing guide

## GitHub project setup

1. Create/push `main` using the `gh repo create ...` command from `README.md` (or a manual remote).
2. In Settings → Pages, set source to **GitHub Actions**. The `deploy-pages` job only runs after the web browser integration tests pass.
3. Enable Actions and permit `GITHUB_TOKEN` write access to contents as needed for the tag-based `github-release` job; this job requests `contents: write` explicitly.
4. To publish a multi-platform preview, tag the current commit: `git tag v0.2.0 && git push origin v0.2.0`. The workflow builds all targets and creates a prerelease containing ZIPs with separate artifacts.

## Android (phones/tablets, 32-bit and 64-bit ARM)

`calculator2-android.zip` contains a universal **debug APK** usable for sideload testing and an **unsigned AAB** for packaging inspection. An AAB is not a directly installable APK. Since the app contains no architecture-specific native Python binaries, Capacitor relies on the device's Android WebView and WebAssembly implementation; ABI is not the sole compatibility constraint.

For signed output (Google Play or user-distributed APK), generate a keystore **privately**, then add repository Actions secrets:

- `ANDROID_KEYSTORE_BASE64` — base64 of `.jks`, single-line.
- `ANDROID_KEYSTORE_PASSWORD` — keystore password.
- `ANDROID_KEY_ALIAS` — key alias.
- `ANDROID_KEY_PASSWORD` — key password.

Run **Actions → Publish signed Android release (optional) → Run workflow** with an existing tag. It attempts to produce signed APK/AAB and attach them to the GitHub release. Never commit the keystore, signing credentials or provisioning files. Production Android signing and Play Store policies must be revalidated before publishing.

## iOS / iPadOS

`calculator2-ios-simulator-arm64.zip` / `x86_64.zip` contains an Xcode **simulator** `.app`, compiled without signing. It cannot run on a real iPhone or be sideloaded like an Android APK.

For an iPhone device / TestFlight release you must enroll in the Apple Developer Program, choose a unique bundle identifier, register signing certificates/provisioning profiles, and configure Actions secrets: `IOS_DISTRIBUTION_CERTIFICATE_P12_BASE64`, `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD`, `IOS_PROVISIONING_PROFILE_BASE64`, `IOS_TEAM_ID` and `IOS_BUNDLE_ID`. `ios-signed.yml` is a **manual opt-in** workflow that attempts an App Store Connect signed `.ipa` export and saves it as a restricted Actions artifact. It does **not** automatically submit to App Store Connect or TestFlight, and must be verified with your actual signing assets. Until then, iOS Safari can install the exact same Calculator 2.0 PWA via Share → Add to Home Screen on an HTTPS site.

## macOS (Apple Silicon and Intel)

Electron desktop packages are unsigned ZIPs built independently for ARM64 Apple Silicon and x64 Intel. Before public distribution, replace unsigned builds with Developer ID signing and notarization; otherwise Gatekeeper may block the app. Mac users can alternatively install the PWA through a browser.

## Windows ARM64 and x64

Electron portable `.exe` targets are built on the matching GitHub Windows architecture. Unsigned previews may trigger SmartScreen. Code signing with a trusted certificate is needed for polished redistribution.

## Linux ARM64 and x64

Electron tarballs run on compatible desktop environments. The ARM64 target includes devices such as 64-bit Raspberry Pi Linux desktops, provided required dynamic libraries and a modern enough system are available. An ARM64 CI *build* is not a guarantee that every Pi distro has matching glibc/graphics dependencies.

## CI limitations

This repository was prepared offline relative to the npm registry and platform toolchains: unit suites and static workflow checks were run locally, but no Android SDK, Apple Xcode, Electron packager or real browser integration was available in this environment. A GitHub Actions run is the authoritative signal for whether packages actually build; after the first run, inspect failed job logs and fix platform-specific issues before public distribution.
