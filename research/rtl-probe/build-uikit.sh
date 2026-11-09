#!/bin/zsh
set -euo pipefail
cd "${0:A:h}"
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
APP=build/DuoRTLProbeUIKit.app
rm -rf "$APP" && mkdir -p "$APP"
xcrun --sdk iphonesimulator swiftc -swift-version 6 -O \
  -sdk "$SDK" -target "$(uname -m)-apple-ios27.1-simulator" \
  UIKitSources/main.swift -o "$APP/DuoRTLProbeUIKit"
sed -e 's/dev.probe.DuoRTLProbe</dev.probe.DuoRTLProbeUIKit</' \
    -e 's/<string>DuoRTLProbe</<string>DuoRTLProbeUIKit</g' Resources/Info.plist > "$APP/Info.plist"
for l in en ar; do mkdir -p "$APP/$l.lproj" && touch "$APP/$l.lproj/InfoPlist.strings"; done
codesign --force --sign - "$APP" >/dev/null
echo "built $APP"
