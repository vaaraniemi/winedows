#!/usr/bin/python3
"""Install Winedows: the Desktop app that puts the live system on a disk.

It asks one question (which disk), confirms that the disk gets erased, and runs
/usr/local/bin/winedows-install-disk as root, showing its progress.
"""
import subprocess
import threading

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk, Pango  # noqa: E402

BACKEND = "/usr/local/bin/winedows-install-disk"
LOGO = "/usr/share/winedows/logo.svg"
TITLE = "Install Winedows"

CSS = b"""
.wd-title { font-size: 18pt; font-weight: bold; color: #1b1b1f; }
.wd-text { color: #5c5f66; }
.wd-disk { padding: 10px 12px; border: 1px solid #dcdde1; background: #ffffff; }
.wd-disk:checked, .wd-disk.wd-picked { border-color: #0a4fd6; background: #eef3fd; }
.wd-error { color: #c22a55; }
progressbar progress { background: #0a4fd6; border: none; min-height: 8px; }
progressbar trough { min-height: 8px; }
"""


def human_size(n):
    return f"{n / 1e12:.1f} TB" if n >= 1e12 else f"{n / 1e9:.0f} GB"


def list_disks():
    try:
        out = subprocess.run([BACKEND, "--list"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    disks = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[1].isdigit():
            disks.append({"path": parts[0], "size": int(parts[1]), "name": parts[2]})
    return disks


def as_root(args):
    """sudo without a password works for the live user; pkexec is the fallback."""
    if subprocess.run(["sudo", "-n", "true"], capture_output=True).returncode == 0:
        return ["sudo", "-n"] + args
    return ["pkexec"] + args


class Installer(Gtk.Window):
    def __init__(self):
        super().__init__(title=TITLE)
        self.set_default_size(560, 460)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("winedows-install")
        self.connect("delete-event", self.on_close)
        self.busy = False
        self.disk = None

        style = Gtk.CssProvider()
        style.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18, margin=28)
        self.add(outer)
        try:
            from gi.repository import GdkPixbuf
            logo = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(LOGO, 260, 72, True))
            logo.set_halign(Gtk.Align.START)
            outer.pack_start(logo, False, False, 0)
        except GLib.Error:
            pass
        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE)
        outer.pack_start(self.stack, True, True, 0)
        self.buttons = Gtk.Box(spacing=8, halign=Gtk.Align.END)
        outer.pack_end(self.buttons, False, False, 0)
        self.show_pick()

    # helpers
    def label(self, text, cls="wd-text", wrap=True):
        lab = Gtk.Label(label=text, xalign=0, wrap=wrap)
        lab.get_style_context().add_class(cls)
        return lab

    def page(self, name, title, text):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.pack_start(self.label(title, "wd-title"), False, False, 0)
        if text:
            box.pack_start(self.label(text), False, False, 0)
        old = self.stack.get_child_by_name(name)
        if old:
            self.stack.remove(old)
        self.stack.add_named(box, name)
        return box

    def set_buttons(self, *specs):
        for child in self.buttons.get_children():
            self.buttons.remove(child)
        for text, cb, cls in specs:
            b = Gtk.Button(label=text)
            if cls:
                b.get_style_context().add_class(cls)
            b.connect("clicked", cb)
            self.buttons.pack_start(b, False, False, 0)
        self.buttons.show_all()

    def show(self, name):
        self.stack.show_all()
        self.stack.set_visible_child_name(name)

    # pages
    def show_pick(self, *_):
        disks = list_disks()
        if not disks:
            self.page("pick", "No disk found",
                      "Winedows needs a disk of at least 10 GB that is not the USB stick it is running from. "
                      "Connect one and try again.")
            self.set_buttons(("Close", lambda *_: self.destroy(), None),
                             ("Try again", self.show_pick, "suggested-action"))
            self.show("pick")
            return
        box = self.page("pick", "Where should Winedows go?",
                        "Pick a disk. That is the only question. Everything else is already perfect.")
        group = None
        for d in disks:
            text = f"{d['name']}\n{human_size(d['size'])} · {d['path']}"
            group = Gtk.RadioButton.new_with_label_from_widget(group, text)
            group.get_child().set_ellipsize(Pango.EllipsizeMode.END)
            group.get_style_context().add_class("wd-disk")
            group.connect("toggled", self.on_pick, d)
            box.pack_start(group, False, False, 0)
        self.disk = disks[0]
        self.set_buttons(("Cancel", lambda *_: self.destroy(), None),
                         ("Install", self.show_confirm, "suggested-action"))
        self.show("pick")

    def on_pick(self, button, disk):
        if button.get_active():
            self.disk = disk

    def show_confirm(self, *_):
        d = self.disk
        self.page("confirm", f"This erases everything on {d['name']}.",
                  f"{human_size(d['size'])} \u00b7 {d['path']}\n\n"
                  "All files on this disk will be gone for good and Winedows takes its place. "
                  "There is no undo.")
        self.set_buttons(("Back", self.show_pick, None),
                         ("Erase and install", self.start, "destructive-action"))
        self.show("confirm")

    def start(self, *_):
        box = self.page("work", "Installing Winedows",
                        "No product key, no account, no updates. Just a few minutes.")
        self.bar = Gtk.ProgressBar(show_text=False)
        self.status = self.label("Starting")
        box.pack_start(self.bar, False, False, 12)
        box.pack_start(self.status, False, False, 0)
        self.set_buttons()
        self.show("work")
        self.busy = True
        threading.Thread(target=self.run_backend, args=(self.disk["path"],), daemon=True).start()

    def run_backend(self, path):
        errors = []
        try:
            p = subprocess.Popen(as_root([BACKEND, "--install", path]), stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
            for line in p.stdout:
                parts = line.strip().split(" ", 2)
                if parts[0] == "STEP" and len(parts) == 3 and parts[1].isdigit():
                    GLib.idle_add(self.progress, int(parts[1]), parts[2])
            errors = p.stderr.read().splitlines()
            ok = p.wait() == 0
        except OSError as e:
            ok, errors = False, [f"ERROR {e}"]
        GLib.idle_add(self.finish, ok, errors)

    def progress(self, pct, text):
        self.bar.set_fraction(min(pct, 100) / 100)
        self.status.set_text(f"{text} ({pct}%)" if 5 < pct < 86 else text)

    def finish(self, ok, errors):
        self.busy = False
        if ok:
            self.page("done", "Winedows is installed",
                      "Remove the USB stick and restart. Winedows starts by itself, signed in and ready.")
            self.set_buttons(("Close", lambda *_: self.destroy(), None),
                             ("Restart now", self.restart, "suggested-action"))
        else:
            reason = next((e[6:] for e in errors if e.startswith("ERROR ")), "something went wrong")
            box = self.page("done", "Installation did not finish", f"Winedows could not be installed: {reason}.")
            details = "\n".join(e[4:] for e in errors if e.startswith("LOG "))
            if details:
                exp = Gtk.Expander(label="Details")
                lab = self.label(details, "wd-error")
                lab.set_selectable(True)
                exp.add(lab)
                box.pack_start(exp, False, False, 0)
            self.set_buttons(("Close", lambda *_: self.destroy(), None),
                             ("Try again", self.show_pick, "suggested-action"))
        self.show("done")

    def restart(self, *_):
        if subprocess.run(["systemctl", "reboot"]).returncode != 0:
            subprocess.run(as_root(["systemctl", "reboot"]))

    def on_close(self, *_):
        return self.busy  # no closing halfway through


if __name__ == "__main__":
    win = Installer()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
