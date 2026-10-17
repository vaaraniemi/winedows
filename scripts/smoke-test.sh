#!/bin/bash
# Boots the ISO's kernel headless with winedows.selftest on the cmdline; the image's
# winedows-selftest.service prints SELFTEST lines on the serial console.
set -euo pipefail
iso=$(find out -maxdepth 1 -name '*.iso' | sort | tail -1)
[ -n "$iso" ] || { echo "no ISO in out/" >&2; exit 1; }
log=out/serial.log
tmp=$(mktemp -d)

# live-build keeps versioned names (/live/vmlinuz-<ver>, /live/initrd.img-<ver>)
find_in_iso() { xorriso -indev "$iso" -find /live -name "$1" 2>/dev/null | tr -d "'" | grep '^/live/' | head -1; }
kernel=$(find_in_iso 'vmlinuz*')
initrd=$(find_in_iso 'initrd.img*')
echo "kernel=$kernel initrd=$initrd"
[ -n "$kernel" ] && [ -n "$initrd" ] || { xorriso -indev "$iso" -ls /live >&2 || true; echo "kernel/initrd not found in ISO" >&2; exit 1; }
xorriso -osirrox on -indev "$iso" -extract "$kernel" "$tmp/vmlinuz" -extract "$initrd" "$tmp/initrd.img" >&2

accel=()
[ -w /dev/kvm ] && accel=(-enable-kvm -cpu host)
echo "accel: ${accel[*]:-tcg (slow)}"
: > "$log"
# multi-user.target: skip the desktop, we only need the selftest unit
timeout 2400 qemu-system-x86_64 "${accel[@]}" -m 4096 -smp 2 -cdrom "$iso" \
  -kernel "$tmp/vmlinuz" -initrd "$tmp/initrd.img" \
  -append "boot=live components quiet console=ttyS0 systemd.unit=multi-user.target winedows.selftest" \
  -display none -serial file:"$log" -monitor none >/dev/null 2>&1 &
pid=$!
for _ in $(seq 1 480); do
  grep -q 'WINEDOWS_SELFTEST_DONE' "$log" 2>/dev/null && break
  kill -0 "$pid" 2>/dev/null || break
  sleep 5
done
kill "$pid" 2>/dev/null || true
cat "$log"
for want in 'SELFTEST apt=absent' 'SELFTEST wine64=ok' 'SELFTEST wine32=ok' 'SELFTEST mime=ok'; do
  grep -q "$want" "$log" || { echo "FAIL: missing '$want'"; exit 1; }
done
echo "smoke test passed"
