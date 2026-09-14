#!/usr/bin/env bash
# Build SonySOOCRecipes.apk from catalog/filters.json.
#
#   tools/build_apk.sh [ --fork DIR ] [ --release ]
#   tools/build_apk.sh --pack leica                 # one brand pack, its own checkout
#   tools/build_apk.sh --all-packs                  # all-in-one + every pack
#
# Steps (per target):
#   1. make sure the upstream checkout exists and is on the pinned revision
#   2. for the all-in-one: apply the app icon from assets/app-icon/
#      for a pack: apply_pack.py owns the icon selection
#   3. generate Recipes.java from the catalog into it
#   4. run the upstream build (ndk-build, aapt, javac, d8, zipalign, apksigner)
#   5. copy the APK out
#
# Brand packs: the SAME app and the SAME catalog, built once per brand with its own
# Android package name so several can sit side by side on the camera. A pack transform is
# destructive and in place, so each pack gets its OWN checkout directory
# (build/recipe-lab-sony-pmca-<id>); the all-in-one keeps the original
# build/recipe-lab-sony-pmca. --fork still overrides either default.
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
UPSTREAM_REPO="https://github.com/voxivoid/recipe-lab-sony-pmca.git"
# Pinned rather than "development" on purpose — the same reason release.yml pins it: a tag
# must build the identical upstream code every time. This is the local-build copy of that
# pin, so a local `tools/build_apk.sh` and a tagged CI run now agree on what they compile.
# Bump it in lockstep with .github/workflows/release.yml and the fetched_rev in
# catalog/filters.json.
UPSTREAM_SHA=6b5c8aa2900019d98496c7047a90ce73d2d6a725
FORK_DEFAULT="$ROOT/build/recipe-lab-sony-pmca"
FORK="$FORK_DEFAULT"
RELEASE=0
PACK=""
ALL_PACKS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fork)      FORK="$2"; shift 2 ;;
    --pack)      PACK="$2"; shift 2 ;;
    --all-packs) ALL_PACKS=1; shift ;;
    --release)   RELEASE=1; shift ;;
    -h|--help)   sed -n '2,35p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
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

# --- prepare one upstream checkout: clone at the pinned revision, fetch jni/platform,
#     and rebrand voxivoid -> hairuoliu. Shared by the all-in-one and every pack so the
#     two paths cannot drift. Mirrors .github/workflows/release.yml exactly.
prepare_fork() {
  local fork="$1"
  if [[ ! -d "$fork/.git" ]]; then
    echo "==> cloning upstream into $fork"
    mkdir -p "$(dirname "$fork")"
    # Plain clone, NOT --recursive: jni/platform is upstream's only submodule and carries a
    # nested stlport submodule that no longer resolves; git recurses into it on init and
    # aborts. We fetch platform by hand (below) at the pinned revision instead.
    git clone "$UPSTREAM_REPO" "$fork"
  else
    echo "==> reusing upstream checkout at $fork"
  fi

  # Reset to the pinned revision, discarding any prior rebrand/pack edits, so the rebrand
  # below is always applied to clean upstream sources (and is safe to re-run).
  git -C "$fork" checkout -f --detach "$UPSTREAM_SHA"
  git -C "$fork" reset --hard "$UPSTREAM_SHA"
  git -C "$fork" clean -fdxq

  # jni/platform is required — Android.mk includes platform/vars.mk and compiles its driver
  # sources. Cloned directly rather than via `git submodule update --init`: OpenMemories-
  # Platform carries a nested submodule (stlport) that no longer resolves and aborts the
  # whole job. The NDK r16b stlport is what we link, so the nested copy is irrelevant.
  (
    cd "$fork"
    PLATFORM_SHA="$(git rev-parse "$UPSTREAM_SHA:jni/platform")"
    echo "==> jni/platform pinned at $PLATFORM_SHA"
    rm -rf jni/platform
    git clone https://github.com/ma1co/OpenMemories-Platform.git jni/platform
    git -C jni/platform checkout "$PLATFORM_SHA"
  )

  # Fetch the revision's own Recipes.java before the rebrand, so the fidelity gate below has
  # something real to compare against. Kept at the checkout root, outside src/, so the
  # rebrand's sed pass and gen_recipes both leave it alone.
  git -C "$fork" show "$UPSTREAM_SHA:src/com/voxivoid/recipelab/Recipes.java" \
    > "$fork/upstream-Recipes.java"

  # Rebrand only when the upstream tree is still voxivoid — once it has been rebranded the
  # source dir is gone, so this guard makes the step idempotent across re-runs.
  if [[ -d "$fork/src/com/voxivoid" ]]; then
    (
      cd "$fork"
      pattern=(
        -e 's/voxivoid/hairuoliu/g'
        -e 's/Recipe Lab/Sony SOOC Recipes/g'
        -e 's/RecipeLab/SonySOOCRecipes/g'
        -e 's/recipelab/sonysoocrecipes/g'
      )
      find src jni res -type f \
        \( -name '*.java' -o -name '*.cpp' -o -name '*.c' -o -name '*.h' \
           -o -name '*.mk' -o -name '*.xml' \) -exec sed -i "${pattern[@]}" {} +
      sed -i "${pattern[@]}" AndroidManifest.xml build.sh build.cmd tools/check-version.sh
      mkdir -p src/com/hairuoliu
      git mv src/com/voxivoid/recipelab src/com/hairuoliu/sonysoocrecipes
    )
  fi
}

# Build one target (all-in-one when $2 is empty, else pack id $2) into fork dir $1 and copy
# the resulting APK into dist/.
build_target() {
  local fork="$1"
  local pack="${2:-}"

  prepare_fork "$fork"

  if [[ -n "$pack" ]]; then
    echo "==> applying pack $pack"
    python "$ROOT/tools/apply_pack.py" --pack "$pack" --fork "$fork"
  else
    # A fresh clone carries upstream's icon; ours lives in assets/app-icon/ and is a build
    # input of this repository, exactly like catalog/filters.json. Same step the release
    # workflow runs for the all-in-one, so a local build and a tagged build look identical.
    echo "==> applying assets/app-icon into the fork"
    for d in mdpi hdpi xhdpi xxhdpi; do
      cp "$ROOT/assets/app-icon/ic_launcher-$d.png" "$fork/res/drawable-$d/ic_launcher.png"
    done
    cp "$ROOT/assets/app-icon/icon-512.png" "$fork/dist/icon-512.png"
  fi

  echo "==> generating Recipes.java from catalog/filters.json"
  if [[ -n "$pack" ]]; then
    python "$ROOT/tools/gen_recipes.py" --pack "$pack" --fork "$fork"
  else
    python "$ROOT/tools/gen_recipes.py" --fork "$fork"
  fi

  # Fidelity against upstream is meaningful only for the all-in-one. A pack is by
  # construction a SUBSET of the all-in-one's recipes, so comparing it against the full
  # upstream file would report every recipe the pack legitimately does not carry. What
  # guarantees a pack's values are unchanged is tests/test_packs.py, which asserts each
  # pack's recipe values are identical to the all-in-one's for the same ids.
  #
  # This step used to point at "$fork/src/.../Recipes.java.orig" — a file nothing in this
  # repository ever writes — so it printed a reassuring "verifying recipes against upstream"
  # and then did nothing at all. Do not restore a path without checking that it is produced.
  if [[ -n "$pack" ]]; then
    echo "==> skipping the upstream fidelity check for pack '$pack' (a pack is a subset; see tests/test_packs.py)"
  elif [[ -f "$fork/upstream-Recipes.java" ]]; then
    echo "==> verifying recipes against upstream"
    python "$ROOT/tools/check_fidelity.py" --upstream "$fork/upstream-Recipes.java"
  else
    echo "==> no upstream-Recipes.java in the checkout — skipping the fidelity check" >&2
  fi

  echo "==> building"
  (
    cd "$fork"
    if (( RELEASE )); then
      RELEASE=1 ./build.sh
    else
      ./build.sh
    fi
  )

  # The expected output name comes from the same place the release workflow gets it, so a
  # change to the naming rule cannot leave these two disagreeing.
  local want
  if [[ -n "$pack" ]]; then
    want="$(python "$ROOT/tools/build_matrix.py" --apk-for "$pack")"
  else
    want="$(python "$ROOT/tools/build_matrix.py" --apk-for all)"
  fi
  local apk="$fork/$want"
  if [[ ! -f "$apk" ]]; then
    # Fall back to a search: upstream's build.sh has moved its output directory before, and
    # failing a ten-minute build over a path is worse than looking for the file.
    apk="$(find "$fork" -name "$want" -print -quit 2>/dev/null || true)"
  fi
  if [[ -z "$apk" || ! -f "$apk" ]]; then
    echo "build finished but $want was not found under $fork" >&2
    exit 1
  fi

  mkdir -p "$ROOT/dist"
  cp "$apk" "$ROOT/dist/"
  echo
  echo "==> $(basename "$apk") -> dist/"
  echo "    install with docs/INSTALL.md"
}

# --- decide what to build --------------------------------------------------------
if [[ -n "$PACK" ]]; then
  # A pack gets its own checkout so the in-place transform cannot clobber the all-in-one.
  fork="${FORK_DEFAULT}-${PACK}"
  [[ "$FORK" != "$FORK_DEFAULT" ]] && fork="$FORK"   # --fork overrides
  build_target "$fork" "$PACK"
elif (( ALL_PACKS )); then
  # All-in-one first, then every pack. The list comes from tools/build_matrix.py --ids,
  # which reads catalog/packs.json — one definition of what a pack is, shared with the
  # release workflow, rather than a second copy of the rule here.
  build_target "$FORK" ""
  mapfile -t PACK_IDS < <(python "$ROOT/tools/build_matrix.py" --ids)
  for id in "${PACK_IDS[@]}"; do
    build_target "$ROOT/build/recipe-lab-sony-pmca-$id" "$id"
  done
else
  build_target "$FORK" ""
fi
