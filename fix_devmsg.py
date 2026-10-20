#!/usr/bin/env python3
"""Neutralise the mod's promo/ad machinery (DevMsg classes + UrlOpenActivity).

The mod opens ad sites in the browser on launch through two independent paths:

  classes20  DevMsg classes fetch a JSON config from the SamMods CDN
             (instapro.top / instapro.click) and open the ad link.
  classes21  UrlOpenActivity fetches a remote config after a delay
             (scheduleRemoteOpen -> RemoteFetchCoordinator -> openUrl) and
             launches the browser with the ad URL. OriginalUpdateController
             drives the update banner/popup from the same place.

Both are Java, so both can be killed: every method that can show a promo or
open the browser becomes a no-op, and the config hostnames are blanked
(same length) so no config is fetched at all.

Edits are body-only / length-preserving, so the dex layout is untouched.
"""
import os
import re
import sys

# '/' works as a separator on both Windows and Linux; os.path.join normalizes.
CLASSES20 = ["com/sammods4h/task/DevMsg.smali",
              "com/sammods4h/task/DevMsg$FetchConfigTask.smali",
              "com/apksam/task/DevMsg.smali",
              "com/apksam2/task/DevMsg.smali",
              "com/OM7753/task/DevMsg.smali"]
CLASSES21 = ["com/OM7753/gold/UrlOpenActivity.smali",
              "com/msr/instapro/OriginalUpdateController.smali"]

KILL20 = re.compile(
    r"^(?:showMessage|show|showDialog|showTheDialog|fetchTheData|"
    r"onButton1Click|onButton2Click|onPostExecute|"
    r"lambda\$showDialog\$0|lambda\$showMessage\S*|-\$\$Nest\$smshowDialog)$")
KILL21 = re.compile(r"^(?:scheduleRemoteOpen|openUrl|checkPopup|checkVersion)$")

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


def make_repl(kill):
    def repl(m):
        decl = m.group(0).split("\n", 1)[0]
        if not kill.match(method_name(decl)) or not returns_void(decl):
            return m.group(0)
        # a native (Dex2C) method cannot keep a body: drop the keyword first
        decl = decl.replace(" native ", " ", 1)
        if decl.rstrip().endswith("native"):
            decl = decl.rstrip()[: -len("native")].rstrip()
        return decl + "\n    .locals 0\n\n    return-void\n.end method"
    return repl


def patch_dir(root, files, kill, blank_hosts):
    for rel in files:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            print(f"  MISSING {rel}")
            continue
        txt = open(p, encoding="utf-8", errors="ignore").read()
        new, n = METHOD.subn(make_repl(kill), txt)
        hosts = 0
        if blank_hosts:
            for old, dead in HOSTS.items():
                if old in new:
                    hosts += new.count(old)
                    new = new.replace(old, dead)
        if new != txt:
            open(p, "w", encoding="utf-8", newline="").write(new)
        print(f"  {rel}: {n} method(s) killed, {hosts} config host(s) blanked")


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else r"Z:\hermes\instapro\decoded"
    patch_dir(os.path.join(base, "smali_classes20"), CLASSES20, KILL20, True)
    patch_dir(os.path.join(base, "smali_classes21"), CLASSES21, KILL21, False)


if __name__ == "__main__":
    main()
