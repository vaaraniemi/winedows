# Decisions
- **D1** live-build + Docker rather than a handmade debootstrap: standard, reproducible ISO tooling.
- **D2** Live ISO first; installer (Calamares) is a stretch goal.
- **D3** i386 via `includes.chroot_before_packages/var/lib/dpkg/arch` so 32-bit exes work. UNVERIFIED that live-build applies it before the first apt update; fallback: a bootstrap-stage hook or `lb config --apt-options`.
- **D4** apt removed in the last chroot hook; dpkg retained.
- **D5** Terminal kept but renamed "Command Prompt" (agents/users need an escape hatch).
- **D6** Self-test is a systemd unit gated on kernel cmdline `winedows.selftest`; inert in normal boots.
- **D7** Autologin as `user`/`live` (live-config defaults).
