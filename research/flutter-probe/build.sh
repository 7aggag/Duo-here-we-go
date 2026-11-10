#!/bin/zsh
# usage: build.sh [baseline|push|dialog-safe]  — builds the probe for the simulator and captures it.
set -euo pipefail
cd "${0:A:h}"
VARIANT=${1:-baseline}
case $VARIANT in
  baseline)    DEFINES=() POSES=closed,open,half ;;
  push)        DEFINES=(--dart-define=PROBE_PUSH=true) POSES=closed,open ;;
  dialog-safe) DEFINES=(--dart-define=PROBE_DIALOG=true --dart-define=PROBE_SAFE=true) POSES=half,closed ;;
esac
flutter build ios --simulator --debug "${DEFINES[@]}"
python3 ../../skills/duo-here-we-go/scripts/capture.py --app build/ios/iphonesimulator/Runner.app \
  --out dhwg-out --label "$VARIANT" --poses "$POSES" $([[ $VARIANT == baseline ]] && echo --iphone)
