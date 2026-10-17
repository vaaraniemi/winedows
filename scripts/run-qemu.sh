#!/bin/sh
# Boot the newest ISO in out/. Uses KVM when available.
set -eu
iso=$(ls -t out/*.iso | head -1)
accel=""
[ -w /dev/kvm ] && accel="-enable-kvm -cpu host"
exec qemu-system-x86_64 $accel -m 4096 -smp 2 -cdrom "$iso" -boot d -vga virtio -display "${QEMU_DISPLAY:-gtk}" "$@"
