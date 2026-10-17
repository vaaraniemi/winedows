#!/bin/sh
# Boots the ISO's kernel headless with winedows.selftest on the cmdline; the image's
# winedows-selftest.service prints SELFTEST lines on the serial console.
set -eu
iso=$(ls -t out/*.iso | head -1)
log=out/serial.log
tmp=$(mktemp -d)
# live-build names them vmlinuz-<kver> / initrd.img-<kver>; find whichever is there.
# xorriso -find prints quoted ISO paths, one per line.
find_live() {
  xorriso -indev "$iso" -find /live -name "$1" 2>/dev/null | tr -d "'" | sort | tail -1
}
kernel=$(find_live 'vmlinuz*')
initrd=$(find_live 'initrd.img*')
if [ -z "$kernel" ] || [ -z "$initrd" ]; then
  echo "FAIL: no kernel/initrd under /live in $iso:"
  xorriso -indev "$iso" -ls /live 2>&1 || true
  exit 1
fi
echo "using $kernel + $initrd"
xorriso -osirrox on -indev "$iso" -extract "$kernel" "$tmp/vmlinuz" \
  -extract "$initrd" "$tmp/initrd.img" >/dev/null
accel=""
[ -w /dev/kvm ] && accel="-enable-kvm -cpu host"
: > "$log"
# shellcheck disable=SC2086
timeout 900 qemu-system-x86_64 $accel -m 4096 -smp 2 -cdrom "$iso" \
  -kernel "$tmp/vmlinuz" -initrd "$tmp/initrd.img" \
  -append "boot=live components quiet console=ttyS0 winedows.selftest" \
  -display none -serial file:"$log" -monitor none >/dev/null 2>&1 &
pid=$!
for _ in $(seq 1 180); do
  grep -q 'WINEDOWS_SELFTEST_DONE' "$log" 2>/dev/null && break
  sleep 5
done
kill "$pid" 2>/dev/null || true
cat "$log"
for want in 'SELFTEST apt=absent' 'SELFTEST wine64=ok' 'SELFTEST wine32=ok' 'SELFTEST mime=ok'; do
  grep -q "$want" "$log" || { echo "FAIL: missing '$want'"; exit 1; }
done
echo "smoke test passed"
