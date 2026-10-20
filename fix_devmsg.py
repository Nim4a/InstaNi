#!/usr/bin/env python3
"""Neutralise the mod's promo/ad machinery (DevMsg classes + config hosts).

The mod fetches a JSON config from the SamMods CDN (instapro.top / instapro.click)
and uses it to show a promo dialog and to open ad sites in the browser. The
native part of the mod calls these Java methods directly, so killing only
show()/showMessage() still let a browser tab pop up on launch.

Two things happen here:
  * every VOID method that can show a promo or open a browser becomes a no-op
    (non-void methods are left alone: a void return would not compile)
  * the config hostnames are blanked (same length) so no config is fetched

Both edits are length-preserving / body-only, so the dex layout is untouched.
"""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else r"Z:\hermes\instapro\decoded\smali_classes20"
# '/' works as a separator on both Windows and Linux; os.path.join normalizes.
FILES = ["com/sammods4h/task/DevMsg.smali",
         "com/sammods4h/task/DevMsg$FetchConfigTask.smali",
         "com/apksam/task/DevMsg.smali",
         "com/apksam2/task/DevMsg.smali",
         "com/OM7753/task/DevMsg.smali"]

# Method names that can display a promo or launch the browser.
KILL = re.compile(
    r"^(?:showMessage|show|showDialog|showTheDialog|fetchTheData|"
    r"onButton1Click|onButton2Click|onPostExecute|"
    r"lambda\$showDialog\$0|lambda\$showMessage\S*|-\$\$Nest\$smshowDialog)$")

METHOD = re.compile(r"^\.method[^\n]*\n.*?^\.end method\s*$", re.M | re.S)

# Config hosts -> same-length dead host (keeps the string table intact).
HOSTS = {"instapro.top": "instapro.zzp", "instapro.click": "instapro.zzz"}


def method_name(decl):
    head = decl.split("(", 1)[0]
    parts = head.split()
    return parts[-1] if parts else ""


def returns_void(decl):
    tail = decl.rsplit(")", 1)[-1].strip()
    return tail == "V"


def repl(m):
    decl = m.group(0).split("\n", 1)[0]
    if not KILL.match(method_name(decl)) or not returns_void(decl):
        return m.group(0)
    # a native (Dex2C) method cannot keep a body: drop the keyword first
    decl = decl.replace(" native ", " ", 1)
    if decl.rstrip().endswith("native"):
        decl = decl.rstrip()[: -len("native")].rstrip()
    return decl + "\n    .locals 0\n\n    return-void\n.end method"


def main():
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print(f"  MISSING {rel}")
            continue
        txt = open(p, encoding="utf-8", errors="ignore").read()
        new, n = METHOD.subn(repl, txt)
        hosts = 0
        for old, dead in HOSTS.items():
            if old in new:
                hosts += new.count(old)
                new = new.replace(old, dead)
        if new != txt:
            open(p, "w", encoding="utf-8", newline="").write(new)
        print(f"  {rel}: {n} method(s) killed, {hosts} config host(s) blanked")


if __name__ == "__main__":
    main()
