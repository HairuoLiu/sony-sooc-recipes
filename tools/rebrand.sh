#!/usr/bin/env bash
# Rebrand one upstream checkout from voxivoid -> hairuoliu, in place.
#
#   tools/rebrand.sh <fork-dir>
#
# The upstream tree hard-codes its package, native library and product names well beyond
# the Java sources: res/layout names custom views by fully-qualified class, jni.cpp looks
# the exception class up by path, and build.sh / build.cmd name both the .so and the output
# APK. Miss any one and the build dies, or the app crashes on launch.
#
# This used to be two copies of the same sed block — one in tools/build_apk.sh and one in
# the release workflow, which no longer exists — which is exactly how two callers drift
# apart. One script, called by anyone who needs it, is the fix.
#
# 'voxivoid' -> 'hairuoliu' in a single pass rewrites every separator form
# (com.voxivoid.recipelab, com/voxivoid/recipelab, com\voxivoid\recipelab,
# com_voxivoid_recipelab) without relying on sed backslash escaping, which silently
# mis-handled the Windows form in build.cmd.
set -euo pipefail

fork="$1"
if [[ -z "$fork" || ! -d "$fork/.git" ]]; then
  echo "usage: tools/rebrand.sh <upstream-checkout>" >&2
  exit 2
fi

cd "$fork"

# Idempotent guard: once rebranded the voxivoid source dir is gone. Skip rather than fail
# so a re-run (or a partial prior run) resumes cleanly.
if [[ ! -d src/com/voxivoid ]]; then
  echo "rebrand: already done (no src/com/voxivoid)"
  exit 0
fi

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
# git mv leaves the now-empty voxivoid/ behind; drop it so the tree stays clean.
rmdir src/com/voxivoid 2>/dev/null || true

echo "rebrand: voxivoid -> hairuoliu done"
