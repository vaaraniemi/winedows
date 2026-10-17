# Build
| Command | What |
|---|---|
| `make iso` | build the builder image, cross-compile the demo exes, build `out/winedows-YYYYMMDD.iso` |
| `make test` | boot the ISO headless in QEMU with `winedows.selftest`, assert results on serial |
| `make guitest` | boot to the Cinnamon desktop with `winedows.guitest`, open the Desktop .exe, screenshots in `out/` |
| `make installtest` | install the ISO onto an empty virtual disk with `winedows.installtest`, then boot that disk with BIOS and UEFI and run the selftest on it |
| `make vm` | boot the newest ISO in a QEMU window |
| `make lint` | shellcheck all scripts and hooks |
| `make shell` | shell in the builder container |
| `make clean` | remove build state and `out/` |

Everything is built reproducibly in Docker (`--privileged`); never rely on host packages.

## Working on this repo
- Change behavior: update the matching wiki page and append to `decisions.md` in the same commit.
- Before committing: `sh -n` edited scripts, `make lint` if shellcheck exists, validate JSON/SVG you touched, and run the naming-rule check (joke-design.md "Rules").
- Develop on the branch your task names; don't open PRs unless asked. What has been built and booted so far: "Verification status" below.
- Agent sandboxes often have no Docker daemon or KVM: only static validation is possible there, so say so rather than claiming a build was verified. CI (`build.yml`) is the real build check; release assets (`screenshot-*.png`) show the boot menu, desktop and Edgy.

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
- CI run 21 (2026-10-17): ISO builds and boots under KVM in ~10 s; selftest `apt=absent`, `mime=ok`, but `wine64`/`wine32`=FAIL. Suspected missing live user (D11).
- CI run 22 (2026-10-17): with `user-setup` installed all selftests pass (`apt=absent`, `wine64`, `wine32`, `mime`); release `iso-22` published. Desktop/GUI (multi-user target only in CI) is not covered yet: needs a manual `make vm` check.
- CI run 23 (2026-10-17): desktop test passes too (`cinnamon`, `desktop-icons`, `exe-open` ok); release `iso-23`. Screenshot in the run's `serial-log` artifact.
- **Static only so far** (historical) (shell syntax, JSON, SVG). The first sandbox had no Docker daemon, so the ISO has *never been built or booted* by an agent. First real build is expected to need fixes (likely candidates: i386 arch timing, package names, dconf keys, `lb config` flags). Update this section after each real build.
