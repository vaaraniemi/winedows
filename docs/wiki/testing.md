# Testing
`make test` extracts the versioned `/live/vmlinuz-*` + `/live/initrd.img-*` (found with xorriso -find) from the ISO and boots QEMU headless with
`boot=live ... console=ttyS0 systemd.unit=multi-user.target winedows.selftest`. `winedows-selftest.service` (conditioned on that cmdline flag) writes to ttyS0:
`SELFTEST apt=absent`, `wine64=ok`, `wine32=ok`, `mime=ok`, then `WINEDOWS_SELFTEST_DONE`. `scripts/smoke-test.sh` greps `out/serial.log`. On a Wine failure the selftest also prints `SELFTEST diag <check>:` lines (tail of Wine's output, or a missing `user` account); the log is uploaded as the `serial-log` CI artifact.
Without KVM it is slow (up to ~15 min). GUI double-click behavior is verified manually (`make vm`): double-click "Totally Native Linux App.exe" on the Desktop; a message box should appear.
