# apt removal
Hook `9990-remove-apt.hook.chroot` purges apt, apt-utils, libapt-pkg*, python3-apt, unattended-upgrades, etc. with `dpkg --purge --force-depends`, deletes `/etc/apt`, `/var/lib/apt`, `/var/cache/apt`, `/usr/lib/apt`, and fails the build if `apt`, `apt-get`, `apt-cache` or `aptitude` is still on PATH.
`dpkg` stays: removing it breaks the package database tools many maintainer scripts and initramfs hooks rely on. Users cannot fetch packages, which is the joke. Bash prints a cmd.exe-style "not recognized" message for any unknown command.
live-build runs built-in steps after hooks that only delete apt config; if a future live-build step needs apt after the hook, move removal to a later stage (binary hook) and record it in decisions.md.
