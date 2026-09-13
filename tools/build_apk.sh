#!/usr/bin/env bash
# Build SonySOOCRecipes.apk from catalog/filters.json.
#
#   tools/build_apk.sh [ --fork DIR ] [ --release ]
#
# Steps:
#   1. make sure the upstream checkout exists and is on the pinned revision
#   2. generate Recipes.java from the catalog into it
#   3. run the upstream build (ndk-build, aapt, javac, d8, zipalign, apksigner)
#   4. copy the APK out
#
# Toolchain, and there is no way around it: JDK 17, Android SDK build-tools 30.0.3,
# platform API 28, and NDK r16b. r16b is the LAST NDK with the GCC toolchain this
# Android 2.3.7 target needs, so a newer NDK will not build it. About 3 GB installed.
# Upstream's docs/DEVELOPMENT.md has a root-free setup script.
#
# Signing: with no keystore configured the upstream build makes a throwaway one. An APK
# signed with a different key CANNOT be installed over an existing install — the camera
# would need the app removed first. To update a camera that already has it, export the
# same four variables upstream CI uses:
#
#   ANDROID_KEYSTORE_B64  base64 -w0 <keystore>
#   ANDROID_KEYSTORE_PASSWORD
#   ANDROID_KEY_ALIAS
#   ANDROID_KEY_PASSWORD
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FORK="$ROOT/build/recipe-lab-sony-pmca"
UPSTREAM_REPO="https://github.com/voxivoid/recipe-lab-sony-pmca.git"
RELEASE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fork)    FORK="$2"; shift 2 ;;
    --release) RELEASE=1; shift ;;
    -h|--help) sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

# --- 1. make sure the toolchain is visible ------------------------------------------
missing=()
[[ -z "${JAVA_HOME:-}" ]] && missing+=(JAVA_HOME)
[[ -z "${ANDROID_SDK:-}" ]] && missing+=(ANDROID_SDK)
[[ -z "${ANDROID_NDK:-}" ]] && missing+=(ANDROID_NDK)
if (( ${#missing[@]} )); then
  echo "not set: ${missing[*]}" >&2
  echo "see this script's header, and upstream docs/DEVELOPMENT.md" >&2
  exit 1
fi

if [[ -n "${ANDROID_NDK:-}" && "$ANDROID_NDK" != *r16b* && "$ANDROID_NDK" != *16.1.* ]]; then
  echo "warning: ANDROID_NDK=$ANDROID_NDK" >&2
  echo "         this target needs r16b (16.1.4479499) — later NDKs dropped the GCC" >&2
  echo "         toolchain that android-14 / APP_STL=stlport_static requires." >&2
fi

# --- 2. fetch or update the upstream checkout ---------------------------------------
if [[ ! -d "$FORK/.git" ]]; then
  echo "==> cloning upstream into $FORK"
  mkdir -p "$(dirname "$FORK")"
  git clone --recursive "$UPSTREAM_REPO" "$FORK"
else
  echo "==> upstream checkout already at $FORK"
fi

# --- 3. generate Recipes.java from the catalog --------------------------------------
echo "==> generating Recipes.java from catalog/filters.json"
python "$ROOT/tools/gen_recipes.py" --fork "$FORK"

echo "==> verifying recipes against upstream"
python "$ROOT/tools/check_fidelity.py" \
  --upstream "$FORK/src/com/hairuoliu/sonysoocrecipes/Recipes.java.orig" 2>/dev/null || true

# --- 4. build ------------------------------------------------------------------------
echo "==> building"
pushd "$FORK" >/dev/null
if (( RELEASE )); then
  RELEASE=1 ./build.sh
else
  ./build.sh
fi
popd >/dev/null

APK="$(find "$FORK/out" "$FORK/dist" -name '*.apk' -print -quit 2>/dev/null || true)"
if [[ -z "$APK" ]]; then
  echo "build finished but no APK was found under $FORK/out or $FORK/dist" >&2
  exit 1
fi

mkdir -p "$ROOT/dist"
cp "$APK" "$ROOT/dist/"
echo
echo "==> $(basename "$APK") -> dist/"
echo "    install with docs/INSTALL.md"
