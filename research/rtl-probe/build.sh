#!/bin/zsh
set -euo pipefail
cd "${0:A:h}"
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
APP=build/DuoRTLProbe.app
rm -rf build && mkdir -p "$APP"
xcrun --sdk iphonesimulator swiftc -parse-as-library -swift-version 6 -O \
  -sdk "$SDK" -target "$(uname -m)-apple-ios27.1-simulator" \
  Sources/*.swift -o "$APP/DuoRTLProbe"
cp Resources/Info.plist "$APP/"
for l in en ar; do mkdir -p "$APP/$l.lproj" && touch "$APP/$l.lproj/InfoPlist.strings"; done
codesign --force --sign - "$APP" >/dev/null
echo "built $APP"
