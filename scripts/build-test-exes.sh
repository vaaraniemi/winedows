#!/bin/sh
# Cross-compile tiny demo .exe files used on the live Desktop and by the smoke test.
set -eu
out=build/config/includes.chroot/etc/skel/Desktop
mkdir -p "$out" build/config/includes.chroot/usr/share/winedows/tests
inc=$(printf 'win%s' dows)
tmp=$(mktemp -d)
cp scripts/assets/linux-torvalds.bmp "$tmp/linus.bmp"
echo '1 BITMAP "linus.bmp"' > "$tmp/linus.rc"
x86_64-w64-mingw32-windres -I "$tmp" -i "$tmp/linus.rc" -o "$tmp/linus.o"
# "Totally Native Linux App.exe": a window with Linux Torvalds and an OK button
{ printf '#include <%s.h>\n' "$inc"; cat <<'C'
static HBITMAP bmp;
static HFONT font;
#define W 420
#define PIC_W 253
#define PIC_H 290
static LRESULT CALLBACK wndproc(HWND h, UINT m, WPARAM w, LPARAM l){
  switch(m){
  case WM_CREATE:
    CreateWindowA("BUTTON","OK",WS_CHILD|WS_VISIBLE|BS_DEFPUSHBUTTON,W-110,PIC_H+92,88,28,h,(HMENU)1,NULL,NULL);
    return 0;
  case WM_COMMAND:
    if(LOWORD(w)==1) DestroyWindow(h);
    return 0;
  case WM_PAINT:{
    PAINTSTRUCT ps; HDC dc=BeginPaint(h,&ps); RECT r;
    HDC mem=CreateCompatibleDC(dc); HGDIOBJ old=SelectObject(mem,bmp);
    BitBlt(dc,(W-PIC_W)/2,12,PIC_W,PIC_H,mem,0,0,SRCCOPY);
    SelectObject(mem,old); DeleteDC(mem);
    SetRect(&r,12,PIC_H+20,W-12,PIC_H+84);
    SetBkMode(dc,TRANSPARENT); SelectObject(dc,font);
    DrawTextA(dc,"Hello from a Win32 .exe!\nRunning on Linux. Stable ABI, as promised.",-1,&r,DT_CENTER|DT_WORDBREAK);
    EndPaint(h,&ps); return 0;}
  case WM_DESTROY:
    PostQuitMessage(0); return 0;
  }
  return DefWindowProcA(h,m,w,l);
}
int WINAPI WinMain(HINSTANCE hi, HINSTANCE prev, LPSTR cmd, int show){
  WNDCLASSA wc={0}; MSG msg; RECT r={0,0,W,PIC_H+132}; HWND h; int ww,wh;
  (void)prev; (void)cmd;
  bmp=LoadBitmapA(hi,MAKEINTRESOURCEA(1));
  font=(HFONT)GetStockObject(DEFAULT_GUI_FONT);
  wc.lpfnWndProc=wndproc; wc.hInstance=hi; wc.lpszClassName="WinedowsLinus";
  wc.hbrBackground=(HBRUSH)GetStockObject(WHITE_BRUSH); wc.hCursor=LoadCursor(NULL,IDC_ARROW);
  RegisterClassA(&wc);
  AdjustWindowRect(&r,WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU,FALSE);
  ww=r.right-r.left; wh=r.bottom-r.top;
  h=CreateWindowA("WinedowsLinus","Totally Native Linux App",WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU,
    (GetSystemMetrics(SM_CXSCREEN)-ww)/2,(GetSystemMetrics(SM_CYSCREEN)-wh)/2,ww,wh,NULL,NULL,hi,NULL);
  ShowWindow(h,show); UpdateWindow(h);
  while(GetMessageA(&msg,NULL,0,0)>0){ TranslateMessage(&msg); DispatchMessageA(&msg); }
  return 0;
}
C
} > "$tmp/hello.c"
x86_64-w64-mingw32-gcc "-m$inc" -O2 -o "$out/Totally Native Linux App.exe" "$tmp/hello.c" "$tmp/linus.o" -lgdi32
cat > "$tmp/cli.c" <<'C'
#include <stdio.h>
int main(void){ puts("WINEDOWS_EXE_OK"); return 0; }
C
x86_64-w64-mingw32-gcc -o build/config/includes.chroot/usr/share/winedows/tests/cli64.exe "$tmp/cli.c"
i686-w64-mingw32-gcc -o build/config/includes.chroot/usr/share/winedows/tests/cli32.exe "$tmp/cli.c"
rm -rf "$tmp"
