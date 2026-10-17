#!/bin/bash
# Boots the ISO to the full desktop (graphical.target, autologin) with winedows.guitest;
# the image's winedows-guitest.service checks Cinnamon and opening the Desktop .exe and
# prints GUITEST lines on serial. A screenshot is saved to out/desktop.png.
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
: > "$log"
mon="$tmp/monitor.sock"
timeout 2400 qemu-system-x86_64 "${accel[@]}" -m 4096 -smp 2 -cdrom "$iso" \
  -kernel "$tmp/vmlinuz" -initrd "$tmp/initrd.img" \
  -append "boot=live components quiet console=ttyS0 username=user hostname=winedows winedows.guitest" \
  -vga std -display none -serial file:"$log" -monitor unix:"$mon",server,nowait >/dev/null 2>&1 &
pid=$!
for _ in $(seq 1 480); do
  grep -q 'WINEDOWS_GUITEST_DONE' "$log" 2>/dev/null && break
  kill -0 "$pid" 2>/dev/null || break
  sleep 5
done
# screenshot of whatever is on screen (the .exe's message box, if it opened)
echo "screendump $PWD/out/desktop.png -f png" | socat - UNIX-CONNECT:"$mon" >/dev/null 2>&1 || true
sleep 2
kill "$pid" 2>/dev/null || true
cat "$log"
for want in 'GUITEST cinnamon=ok' 'GUITEST desktop-icons=ok' 'GUITEST exe-open=ok'; do
  grep -q "$want" "$log" || { echo "FAIL: missing '$want'"; exit 1; }
done
echo "gui test passed"
