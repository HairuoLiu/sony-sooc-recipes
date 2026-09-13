#!/usr/bin/env bash
# Install a Recipe Lab APK onto a Sony PMCA camera over Wi-Fi ADB.
#
#   tools/install-wifi.sh <apk> <camera-ip> [port]
#
# This is the FAST LANE, not the first install. The camera must already have
# OpenMemories:Tweak with "Enable Wifi" and "Enable ADB" turned on — and the only way
# to get Tweak onto the camera the first time is Sony-PMCA-RE over USB. See
# docs/INSTALL.md.
#
# Security: while ADB is on, anything on the same network can reach the camera on
# port 5555 and read its card or uninstall apps. Use a network you trust, and turn
# ADB back off on the camera when you are done — this script's disconnect only drops
# the host side.
set -euo pipefail

APK="${1:-}"
CAMERA_IP="${2:-}"
PORT="${3:-5555}"

if [[ -z "$APK" || -z "$CAMERA_IP" ]]; then
  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi

if [[ ! -f "$APK" ]]; then
  echo "no such APK: $APK" >&2
  exit 1
fi

# Refuse the obvious placeholder so nobody pastes someone else's address from a guide.
case "$CAMERA_IP" in
  CAMERA_IP|192.168.1.1|0.0.0.0)
    echo "refusing '$CAMERA_IP' — that is a placeholder." >&2
    echo "Use the address your camera shows under Tweak -> Developer." >&2
    exit 1
    ;;
esac

if ! command -v adb >/dev/null 2>&1; then
  echo "adb not found. Install Android Platform-Tools:" >&2
  echo "  https://developer.android.com/tools/releases/platform-tools" >&2
  exit 1
fi

TARGET="${CAMERA_IP}:${PORT}"

echo "==> connecting to ${TARGET}"

# A stale connection from a previous session is the single most common cause of a
# bogus 'offline'. Drop it first, then connect fresh.
adb disconnect "$TARGET" >/dev/null 2>&1 || true
adb connect "$TARGET"

echo "==> waiting for the camera to report 'device'"
state=""
for _ in $(seq 1 15); do
  state="$(adb -s "$TARGET" get-state 2>/dev/null || true)"
  [[ "$state" == "device" ]] && break
  sleep 1
done

if [[ "$state" != "device" ]]; then
  cat >&2 <<'EOF'

The camera did not come up as 'device'.

Check, in this order:
  1. the camera is awake — it sleeps, and a sleeping camera drops adb
  2. the IP still matches Tweak -> Developer; DHCP hands out a new one freely
  3. host and camera are on the same network (guest networks isolate clients)
  4. no VPN on the host, and the terminal has local-network permission
  5. ADB is still enabled in Tweak -> Developer
  6. 'adb kill-server' then run this script again

'offline' means the socket opened but the camera stopped answering — usually sleep.
EOF
  exit 1
fi

echo "==> installing $(basename "$APK")"
# -r keeps existing app data, so stored recipes survive an update.
adb -s "$TARGET" install -r "$APK"

echo
echo "==> done. Open 'Recipe Lab' from the camera's Application List."
echo
cat <<EOF
Before you walk away:
  adb disconnect ${TARGET}
      drops this host only.
  Then turn ADB OFF in Tweak -> Developer on the camera.
      That is the step that actually stops the debug daemon listening on
      port ${PORT} to your whole network.
EOF
