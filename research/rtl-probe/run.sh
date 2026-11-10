#!/bin/zsh
# usage: run.sh <udid> <pose-label> <mode: split|arrangement|uikit> <lang: en|ar|en-forceRTL>
set -euo pipefail
cd "${0:A:h}"
UDID=$1 POSE=$2 MODE=$3 LANG_CASE=$4
shift 4
EXTRA=("$@")
BID=${BID:-dev.probe.DuoRTLProbe}
OUT=results/$POSE/$MODE-$LANG_CASE
mkdir -p "$OUT"

case $LANG_CASE in
  ar)          ARGS=(-AppleLanguages "(ar)" -AppleLocale ar_EG) ;;
  en)          ARGS=(-AppleLanguages "(en)" -AppleLocale en_US) ;;
  en-forceRTL) ARGS=(-AppleLanguages "(en)" -AppleLocale en_US -ForceRTLAppearance YES) ;;
  en-forceRTL-traits) ARGS=(-AppleLanguages "(en)" -AppleLocale en_US -ForceRTLAppearance YES -ForceRTLTraits YES) ;;
esac

xcrun simctl terminate "$UDID" $BID 2>/dev/null || true
DATA=$(xcrun simctl get_app_container "$UDID" $BID data)
rm -f "$DATA/Documents/probe.log"
xcrun simctl launch "$UDID" $BID -ProbeMode "$MODE" "${ARGS[@]}" "${EXTRA[@]}" >/dev/null
sleep 4

for d in 1 3; do
  xcrun simctl io "$UDID" screenshot --display="$d" "$OUT/display-$d.png" >/dev/null 2>&1 || true
done
cp "$DATA/Documents/probe.log" "$OUT/probe.log" 2>/dev/null || echo "no probe.log" > "$OUT/probe.log"
echo "== $OUT"; cat "$OUT/probe.log"
