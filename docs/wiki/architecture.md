# Architecture
Debian live-build (`lb`) assembles a hybrid BIOS/UEFI ISO from `build/`.
1. `auto/config` → `lb config` (trixie, amd64, main+contrib, no d-i, iso-hybrid, no recommends).
2. Bootstrap, then `includes.chroot_before_packages` (adds `i386` arch), then package list install.
3. `includes.chroot` overlay is copied in, then `hooks/live/*.hook.chroot` run in order:
   `0100` setup (dconf, MIME, binfmt, test units, prompt) → `0200` branding (os-release, Edgy name/icons/autoconfig) → (binary stage) `9000` boot menu theme → `9990` remove apt from the squashfs (must stay last).
   `includes.binary/` is copied into the ISO tree (GRUB theme assets).
4. squashfs + ISO. At runtime live-boot/live-config create `user`, LightDM autologins into Cinnamon,
   `winedows-prefix.desktop` autostarts `wineboot -u`.
Key runtime files: `/usr/local/bin/winedows-run`, `/usr/share/applications/winedows-run.desktop`, `/etc/xdg/mimeapps.list`, `/etc/binfmt.d/winedows.conf`, `/etc/dconf/db/local.d/00-winedows`.

## Layout
- `build/`: live-build tree (run `lb` from here). `auto/` wrappers; `config/package-lists/` packages; `config/hooks/live/NNNN-*.hook.chroot|binary` hooks (numeric order); `config/includes.chroot/` overlaid on the rootfs; `config/includes.chroot_before_packages/` present before package install (enables `i386` via `/var/lib/dpkg/arch`); `config/includes.binary/` copied into the ISO tree.
- `docs/index.html`: project website (GitHub Pages from `/docs`; links the latest release). `docs/wiki/`: these pages.
- `scripts/`: host/container scripts. `.github/workflows/build.yml`: CI build, tests, release.
- Hook naming: `NNNN-name.hook.chroot` (or `.hook.binary`); 0xxx setup, 1xxx-8xxx features, **`9990-remove-apt.hook.binary` must stay last** and must fail the build if apt survives (`dpkg` stays on purpose, see apt-removal.md).
