# Joke design
Tone: deadpan. The OS never admits it is Linux except in tiny places (wallpaper caption, start page footer, os-release `ID_LIKE`).
Joke direction: we poke fun at Linux binary compatibility (vs Ubuntu), never at Windows. Reference: https://blog.hiler.eu/win32-the-only-stable-abi/
Look: bottom panel, Start-style menu applet at left, grouped window list, tray + clock at right; wallpaper `wallpaper.svg`; Papirus icons; desktop icons "This PC", "Recycle Bin", "Edgy", "Command Prompt", demo exe.
Start page (`start.html`) has the "compatibility benchmark" (the butt of the joke is native Linux/Ubuntu ABI instability, NOT Windows; Win32 via Wine is the stable ABI; ref: blog.hiler.eu/win32-the-only-stable-abi/). Keep claims obviously silly; no real company logos/assets; avoid claims that could read as a factual statement about a real product.
Stretch ideas: fake BSOD screensaver, "Updates are available" popup that is a no-op, GRUB entry rename, icon extraction from exes with `wrestool`.

## Branding & site
Product brand is "GigaHard Winedows" (parody of a certain Redmond company). Logo: `docs/logo.svg` (copied to `/usr/share/winedows/logo.svg` in the image): four panes, two wine-red (glass, grapes), two blue (swoosh). Website (`docs/index.html`) is deliberately flat and corporate: white/light-grey, blue accent, top nav, cards and a table, no gradients, dark mode via `prefers-color-scheme`. Keep it that way.
