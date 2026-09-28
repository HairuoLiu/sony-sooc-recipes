#!/usr/bin/env bash
# Build EVERY target locally: the all-in-one plus all eleven brand packs, the publish:false
# ones included. `tools/build_apk.sh --all-packs` deliberately stops at the public set, so
# this is the script to reach for when the APKs that go INSIDE the Windows installer have to
# be rebuilt — the installer carries all twelve, held-back packs and all.
# Nothing here is committed; dist/*.apk is gitignored (*.apk).
#
# Prereqs — the same toolchain tools/build_apk.sh requires (it hard-exits without them):
#   export JAVA_HOME=...        # JDK 17
#   export ANDROID_SDK=...      # build-tools 30.0.3 + platform API 28
#   export ANDROID_NDK=...      # NDK r16b (16.1.4479499) — later NDKs dropped the GCC
#                               # toolchain this android-14 / stlport target needs
# Run from the repo root. Output lands in dist/.
#
# WHY A SHORT BUILD DIR — read this before "simplifying" it back to build/:
# ndk-build r16b mirrors the whole absolute source path into the object path:
#   out/obj/local/armeabi/objs/<mod>/D_/<absolute-source-path>/foo.o.d
# Built inside this repository's own long path, that .d lands around 263 chars and blows
# past Windows' 260-char MAX_PATH, so ndk-build dies with
#   "fatal error: opening dependency file ...: No such file or directory"
# even though every tool is installed correctly. So every target is built through
# --fork into a deliberately short work dir. Override it if you like — just keep it SHORT.
set -euo pipefail
cd "$(dirname "$0")/.."

WORK="${LOCAL_BUILD_WORK:-/d/b/f}"

echo "==> all-in-one"
tools/build_apk.sh --fork "$WORK"

echo
echo "==> the brand packs (every id in catalog/packs.json, publish:false ones included)"
PACK_IDS="$(python -c "
import json
d = json.load(open('catalog/packs.json'))
ps = d.get('packs', d if isinstance(d, list) else [])
print(' '.join(p['id'] for p in ps))
")"
for id in $PACK_IDS; do
  echo "==> pack $id"
  tools/build_apk.sh --pack "$id" --fork "$WORK"
done

echo
echo "==> done. APKs in dist/:"
ls -1 dist/*.apk 2>/dev/null || echo "(no apks found — check the toolchain exports above)"
