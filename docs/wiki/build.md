# Build
`make iso` → Docker image `winedows-builder` (Dockerfile) → `scripts/build-test-exes.sh` (mingw demo exes into the overlay) → `scripts/build-iso.sh` (`lb clean/config/build`) → `out/winedows-DATE.iso`.
Requires a running Docker daemon and `--privileged` (loop devices, mounts, debootstrap). Log: `build/build.log`.

## Debugging
- Inspect `build/chroot/` after a failed build; re-run `lb build` inside `make shell` (`cd build && lb build`).
- Hook failures print the hook name; hooks run with `set -e`.
- Package not found: wine/firefox-esr come from trixie `main`/`contrib`; check `build/config/package-lists/`.
- i386 packages not found: confirm `/var/lib/dpkg/arch` exists in chroot before the first `apt-get update` (see decisions.md D3).

## Verification status
- Agent sandbox (2026-10): dockerd can be started manually (`dockerd &`), but egress to deb.debian.org / security.debian.org / snapshot.debian.org is blocked by the network policy (only archive.ubuntu.com resolves), so containers cannot `apt-get` and `lb build` cannot bootstrap trixie. Ask the user to allow those hosts, or rely on CI.
- Host Ubuntu's `live-build` is 3.0~a57 (ancient): `lb config` there rejects `--bootloaders`/`--updates`, which are valid in trixie's live-build 20250505. Do not use it to validate flags.
- **Static only so far** (shell syntax, JSON, SVG). The first sandbox had no Docker daemon, so the ISO has *never been built or booted* by an agent. First real build is expected to need fixes (likely candidates: i386 arch timing, package names, dconf keys, `lb config` flags). Update this section after each real build.
