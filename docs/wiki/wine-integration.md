# Wine integration
- Handler: `winedows-run` (`wine start /unix file`, `wine msiexec /i` for .msi); Mono/Gecko prompts suppressed with `WINEDLLOVERRIDES=mscoree,mshtml=`.
- MIME: `winedows-run.desktop` + defaults in `/etc/xdg/mimeapps.list` (and `x-cinnamon-mimeapps.list`) for x-ms-dos-executable, x-msdos-program, x-msdownload, vnd.microsoft.portable-executable, x-dosexec, x-msi.
- binfmt_misc `:Win32PE:M::MZ::/usr/local/bin/winedows-run:` covers running `./foo.exe` or an exec bit being set.
- 32-bit exes need `wine32:i386`. Prefix created at first login by autostart (`wineboot -u`).
- Nemo: `executable-text-activation='display'`, double-click policy.
- Known limits: 16-bit apps, kernel-mode drivers/anti-cheat do not work (don't put that on the start page).
- Rule: `.exe` files on the Desktop are mode `0644`, `.desktop` launchers `0755` (set in `0100-winedows-setup`). An executable `.exe` would make Nemo try to exec it natively.
