# Architecture
Debian live-build (`lb`) assembles a hybrid BIOS/UEFI ISO from `build/`.
1. `auto/config` → `lb config` (trixie, amd64, main+contrib, no d-i, iso-hybrid, no recommends).
2. Bootstrap, then `includes.chroot_before_packages` (adds `i386` arch), then package list install.
3. `includes.chroot` overlay is copied in, then `hooks/live/*.hook.chroot` run in order:
   `0100` setup (dconf, MIME, binfmt, selftest unit, prompt) → `0200` branding → (binary stage) `9990` remove apt from the squashfs.
4. squashfs + ISO. At runtime live-boot/live-config create `user`, LightDM autologins into Cinnamon,
   `winedows-prefix.desktop` autostarts `wineboot -u`.
Key runtime files: `/usr/local/bin/winedows-run`, `/usr/share/applications/winedows-run.desktop`, `/etc/xdg/mimeapps.list`, `/etc/binfmt.d/winedows.conf`, `/etc/dconf/db/local.d/00-winedows`.
