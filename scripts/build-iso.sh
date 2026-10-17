#!/bin/bash
# Runs inside the builder container (needs --privileged).
set -euo pipefail
cd /work/build
# build number: CI passes the run number (same N as the iso-N release); local builds say "local"
build="${WINEDOWS_BUILD:+b$WINEDOWS_BUILD}"
build="${build:-local}"
date=$(date +%Y%m%d)
printf 'WINEDOWS_BUILD=%s\nWINEDOWS_DATE=%s\n' "$build" "$date" > config/includes.chroot/etc/winedows-build
lb clean --purge >/dev/null 2>&1 || true
lb config
lb build 2>&1 | tee /work/build/build.log
mkdir -p /work/out
mv -f ./*.iso "/work/out/winedows-$date-$build.iso"
ls -lh /work/out
