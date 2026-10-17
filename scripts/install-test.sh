#!/bin/bash
# Install test: boot the ISO with an empty virtual disk and winedows.installtest (the image's
# winedows-installtest.service runs the installer on that disk and powers off), then boot the
# disk alone, once with BIOS and once with UEFI (OVMF). The installed system runs the selftest.
set -euo pipefail
iso=$(find out -maxdepth 1 -name '*.iso' | sort | tail -1)
[ -n "$iso" ] || { echo "no ISO in out/" >&2; exit 1; }
tmp=$(mktemp -d -p "$PWD/out")
trap 'rm -rf "$tmp"' EXIT
disk=$tmp/disk.img
truncate -s 20G "$disk"

find_in_iso() { xorriso -indev "$iso" -find /live -name "$1" 2>/dev/null | tr -d "'" | grep '^/live/' | head -1; }
kernel=$(find_in_iso 'vmlinuz*')
initrd=$(find_in_iso 'initrd.img*')
[ -n "$kernel" ] && [ -n "$initrd" ] || { echo "kernel/initrd not found in ISO" >&2; exit 1; }
xorriso -osirrox on -indev "$iso" -extract "$kernel" "$tmp/vmlinuz" -extract "$initrd" "$tmp/initrd.img" >/dev/null 2>&1

accel=()
[ -w /dev/kvm ] && accel=(-enable-kvm -cpu host)
echo "accel: ${accel[*]:-tcg (slow)}"

# wait_for LOG PID MARKER SECONDS
wait_for() {
  for _ in $(seq 1 $(($4 / 5))); do
    grep -aq "$3" "$1" 2>/dev/null && return 0
    kill -0 "$2" 2>/dev/null || return 0
    sleep 5
  done
}
need() { # LOG LINES...
  local log=$1; shift
  for want in "$@"; do grep -aq "$want" "$log" || { echo "FAIL: missing '$want' in $log"; exit 1; }; done
}

# 1. install from the live system
log=out/serial-install.log
: > "$log"
timeout 2400 qemu-system-x86_64 "${accel[@]}" -m 4096 -smp 2 -cdrom "$iso" \
  -drive file="$disk",format=raw,if=virtio \
  -kernel "$tmp/vmlinuz" -initrd "$tmp/initrd.img" \
  -append "boot=live components quiet console=ttyS0 systemd.unit=multi-user.target winedows.installtest" \
  -display none -serial file:"$log" -monitor none >/dev/null 2>&1 &
pid=$!
wait_for "$log" "$pid" WINEDOWS_INSTALLTEST_DONE 2400
# it powers itself off; give it a moment to flush the disk, then make sure it is gone
for _ in $(seq 1 30); do kill -0 "$pid" 2>/dev/null || break; sleep 2; done
kill "$pid" 2>/dev/null || true
wait "$pid" 2>/dev/null || true
grep -a 'INSTALLTEST' "$log" || true
need "$log" 'INSTALLTEST install=ok'

# 2. boot the installed disk, no ISO: BIOS, then UEFI
selftest=('SELFTEST system=installed' 'SELFTEST apt=absent' 'SELFTEST wine64=ok' 'SELFTEST wine32=ok'
          'SELFTEST mime=ok' 'SELFTEST terminal=absent' 'SELFTEST branding=ok' 'SELFTEST desktop=ok')
boot_disk() { # NAME, extra qemu args...
  local name=$1; shift
  local log=out/serial-installed-$name.log
  : > "$log"
  timeout 1800 qemu-system-x86_64 "${accel[@]}" -m 4096 -smp 2 "$@" \
    -drive file="$disk",format=raw,if=virtio \
    -display none -serial file:"$log" -monitor none >/dev/null 2>&1 &
  local p=$!
  wait_for "$log" "$p" WINEDOWS_SELFTEST_DONE 1800
  kill "$p" 2>/dev/null || true
  wait "$p" 2>/dev/null || true
  grep -a 'SELFTEST' "$log" | sed "s/^/[$name] /" || true
  need "$log" "${selftest[@]}"
  echo "installed system boots with $name"
}
boot_disk bios

code=""; vars=""
for c in /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd; do [ -f "$c" ] && { code=$c; break; }; done
for v in /usr/share/OVMF/OVMF_VARS_4M.fd /usr/share/OVMF/OVMF_VARS.fd; do [ -f "$v" ] && { vars=$v; break; }; done
[ -n "$code" ] && [ -n "$vars" ] || { echo "FAIL: OVMF firmware not found"; exit 1; }
cp "$vars" "$tmp/vars.fd"
boot_disk uefi -machine q35 \
  -drive if=pflash,format=raw,unit=0,readonly=on,file="$code" \
  -drive if=pflash,format=raw,unit=1,file="$tmp/vars.fd"
echo "install test passed"
