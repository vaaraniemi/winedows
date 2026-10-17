#!/bin/sh
# Cross-compile tiny demo .exe files used on the live Desktop and by the smoke test.
set -eu
out=build/config/includes.chroot/etc/skel/Desktop
mkdir -p "$out" build/config/includes.chroot/usr/share/winedows/tests
cat > /tmp/hello.c <<'C'
#include <windows.h>
int main(void){
  MessageBoxA(NULL,"Hello from a real Windows .exe!\n\n(Psst: it is Linux.)","Winedows",MB_OK|MB_ICONINFORMATION);
  return 0;
}
C
x86_64-w64-mingw32-gcc -mwindows -o "$out/Totally Real Windows App.exe" /tmp/hello.c
cat > /tmp/cli.c <<'C'
#include <stdio.h>
int main(void){ puts("WINEDOWS_EXE_OK"); return 0; }
C
x86_64-w64-mingw32-gcc -o build/config/includes.chroot/usr/share/winedows/tests/cli64.exe /tmp/cli.c
i686-w64-mingw32-gcc -o build/config/includes.chroot/usr/share/winedows/tests/cli32.exe /tmp/cli.c
