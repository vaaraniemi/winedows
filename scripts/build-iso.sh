#!/bin/sh
# Runs inside the builder container (needs --privileged).
set -eu
cd /work/build
lb clean --purge >/dev/null 2>&1 || true
lb config
lb build 2>&1 | tee /work/build/build.log
mkdir -p /work/out
mv -f ./*.iso "/work/out/winedows-$(date +%Y%m%d).iso"
ls -lh /work/out
