# AGENT.md — Winedows

April Fools project: a Debian 13 (trixie) live ISO with **only** Cinnamon, Firefox and Wine,
themed like Windows. Double-clicking an `.exe` runs it through Wine. `apt` is removed.
The punchline: it has *better* binary compatibility than Windows. Keep the joke deadpan.

## Golden rules
1. **No apt.** `9990-remove-apt.hook.chroot` must remain the last hook and must fail the build if apt survives. `dpkg` stays on purpose (docs/wiki/apt-removal.md).
2. **Only Cinnamon + Firefox (branded "Edgy", spoofs Edge UA) + Wine** (plus the minimum to boot/run them). Do not add office suites, media players, software centers. The terminal exists only as "Command Prompt".
3. **Joke direction: mock Linux (Ubuntu) binary compatibility, not Windows (see joke-design.md).**
3b. **Parody only.** No Microsoft logos, fonts, wallpapers, sounds, or trademarked product artwork. Our names: Winedows, This PC, Recycle Bin, Edgy.
4. `.exe` files on the Desktop are mode `0644`; `.desktop` launchers are `0755`. Executable `.exe` would make Nemo try to exec natively.
5. Everything is built reproducibly in Docker (`--privileged`). Never rely on host packages.

## Commands
| Command | What |
|---|---|
| `make iso` | build builder image, cross-compile demo exes, build `out/winedows-YYYYMMDD.iso` |
| `make test` | boot ISO headless in QEMU with `winedows.selftest`, assert results on serial |
| `make vm` | boot newest ISO in a QEMU window |
| `make lint` | shellcheck all scripts/hooks |
| `make shell` | shell in the builder container |
| `make clean` | remove build state and `out/` |

## Layout
- `build/` live-build tree (run `lb` from here). `auto/` wrappers; `config/package-lists/` packages;
  `config/hooks/live/NNNN-*.hook.chroot` chroot hooks (numeric order); `config/includes.chroot/` files overlaid on the rootfs;
  `config/includes.chroot_before_packages/` files present before package install (enables `i386` via `/var/lib/dpkg/arch`).
- `docs/index.html` project website (GitHub Pages from `/docs`; auto-links latest release).
- `scripts/` host/container scripts. `docs/wiki/` deep-dive docs. `.github/workflows/build.yml` CI ISO build.

## Wiki index (read before touching the matching area)
- [architecture](docs/wiki/architecture.md) · [build](docs/wiki/build.md) · [testing](docs/wiki/testing.md)
- [wine-integration](docs/wiki/wine-integration.md) · [apt-removal](docs/wiki/apt-removal.md)
- [joke-design](docs/wiki/joke-design.md) · [decisions](docs/wiki/decisions.md)

## Workflow for agents
- Hook naming: `NNNN-name.hook.chroot`; 0xxx setup, 1xxx-8xxx features, **9990 apt removal last**.
- Change behavior → update the relevant wiki page and append to `decisions.md` in the same commit.
- Before committing: `sh -n` on edited scripts (and `make lint` if shellcheck exists), validate JSON/SVG you touched.
- The sandbox often has **no running Docker daemon / no KVM**. If so, only static validation is possible; say so rather than claiming a build was verified. CI (`build.yml`) is the real build check.
- Branch policy: develop on the branch named in your task; do not open PRs unless asked.
- Status: see "Verification status" in docs/wiki/build.md for what has/hasn't been built.
