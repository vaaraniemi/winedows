#!/bin/bash
# Boots the ISO to the full desktop (graphical.target, autologin) with winedows.guitest;
# the image's winedows-guitest.service checks Cinnamon and opening the Desktop .exe and
# prints GUITEST lines on serial. Screenshots: out/bootmenu.png, out/desktop.png, out/edgy.png.
set -euo pipefail
iso=$(find out -maxdepth 1 -name '*.iso' | sort | tail -1)
[ -n "$iso" ] || { echo "no ISO in out/" >&2; exit 1; }
log=out/serial-gui.log
tmp=$(mktemp -d)

find_in_iso() { xorriso -indev "$iso" -find /live -name "$1" 2>/dev/null | tr -d "'" | grep '^/live/' | head -1; }
kernel=$(find_in_iso 'vmlinuz*')
initrd=$(find_in_iso 'initrd.img*')
[ -n "$kernel" ] && [ -n "$initrd" ] || { echo "kernel/initrd not found in ISO" >&2; exit 1; }
xorriso -osirrox on -indev "$iso" -extract "$kernel" "$tmp/vmlinuz" -extract "$initrd" "$tmp/initrd.img" >/dev/null 2>&1

accel=()
[ -w /dev/kvm ] && accel=(-enable-kvm -cpu host)
echo "accel: ${accel[*]:-tcg (slow)}"
shot() { echo "screendump $PWD/out/$2.png -f png" | socat - UNIX-CONNECT:"$1" >/dev/null 2>&1 || true; sleep 2; }

# 1. Boot menu: boot the ISO itself (BIOS, GRUB) and photograph the menu
bmon="$tmp/boot.sock"
timeout 120 qemu-system-x86_64 "${accel[@]}" -m 1024 -cdrom "$iso" -boot d -vga std -display none \
  -monitor unix:"$bmon",server,nowait >/dev/null 2>&1 &
bpid=$!
sleep 7
shot "$bmon" bootmenu
kill "$bpid" 2>/dev/null || true
wait "$bpid" 2>/dev/null || true
: > "$log"
mon="$tmp/monitor.sock"
timeout 2400 qemu-system-x86_64 "${accel[@]}" -m 4096 -smp 2 -cdrom "$iso" \
  -kernel "$tmp/vmlinuz" -initrd "$tmp/initrd.img" \
  -append "boot=live components quiet console=ttyS0 username=user hostname=winedows winedows.guitest" \
  -vga std -display none -serial file:"$log" -monitor unix:"$mon",server,nowait >/dev/null 2>&1 &
pid=$!
took_desktop=""
for _ in $(seq 1 480); do
  if [ -z "$took_desktop" ] && grep -q 'GUITEST screenshot=desktop' "$log" 2>/dev/null; then
    shot "$mon" desktop; took_desktop=1   # the desktop with the .exe's window open
  fi
  grep -q 'WINEDOWS_GUITEST_DONE' "$log" 2>/dev/null && break
  kill -0 "$pid" 2>/dev/null || break
  sleep 5
done
# whatever is on screen now (Edgy, if it opened)
if [ -n "$took_desktop" ]; then shot "$mon" edgy; else shot "$mon" desktop; fi
kill "$pid" 2>/dev/null || true
cat "$log"
for want in 'GUITEST cinnamon=ok' 'GUITEST desktop-icons=ok' 'GUITEST exe-open=ok' \
            'GUITEST panels=none' 'GUITEST wmtheme=ok' 'GUITEST edgy=ok'; do
  grep -q "$want" "$log" || { echo "FAIL: missing '$want'"; exit 1; }
done
echo "gui test passed"
