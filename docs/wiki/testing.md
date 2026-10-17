# Testing
`make test` extracts the versioned `/live/vmlinuz-*` + `/live/initrd.img-*` (found with xorriso -find) from the ISO and boots QEMU headless with
`boot=live ... console=ttyS0 systemd.unit=multi-user.target winedows.selftest`. `winedows-selftest.service` (conditioned on that cmdline flag) writes to ttyS0:
`SELFTEST apt=absent`, `wine64=ok`, `wine32=ok`, `mime=ok`, then `WINEDOWS_SELFTEST_DONE`. `scripts/smoke-test.sh` greps `out/serial.log`. On a Wine failure the selftest also prints `SELFTEST diag <check>:` lines (tail of Wine's output, or a missing `user` account); the log is uploaded as the `serial-log` CI artifact.
Without KVM it is slow (up to ~15 min).

`make guitest` (`scripts/gui-test.sh`) boots the full graphical target with autologin and `winedows.guitest`. `winedows-guitest.service` waits for the user's `cinnamon` and `nemo-desktop` processes, then opens the Desktop .exe with `gio open` inside the session's environment (the same default-app lookup a Nemo double-click does) and checks the exe's Wine process appears. It prints `GUITEST cinnamon=ok`, `desktop-icons=ok`, `exe-open=ok`, then `WINEDOWS_GUITEST_DONE`; QEMU's monitor saves `out/desktop.png` (uploaded with the `serial-log` CI artifact). It does not move a real mouse, so Nemo's own click handling and the message box contents are still checked by eye in the screenshot or with `make vm`.
