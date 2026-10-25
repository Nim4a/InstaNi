#!/usr/bin/env python3
"""Force-enable selected mod features by stubbing GOLD's native bool getters.

The mod gates features (save profile pic, save highlight cover, double-tap like,
etc.) behind com.OM7753.gold.GOLD.get*Bool() native methods in libProMods.so.
We can't flip the native side cheaply, but we CAN replace the Java (smali)
declaration with a stub that returns true — same trick as fix_devmsg.py:
drop 'native' and give the method a body.

We deliberately leave getAdsBool / getShoppingBoolEz native so ads stay off.
"""
import os, re, sys

GOLD = "com/OM7753/gold/GOLD.smali"
FORCE = ["getHighlightBool", "getMaxBoolEz", "getDirectBoolEz", "getDoubleBoolEz",
         "getStoriesBool", "getSPostBool", "getVideoBool", "getCommentsBool",
         "getMentionBool", "getDiscoverPeopleBool", "getExploreBool",
         "getstoriesSkipBoolEz"]

METHOD = re.compile(r"^\.method[^\n]*\n.*?^\.end method\s*$", re.M | re.S)


def repl(m):
    decl = m.group(0).split("\n", 1)[0]
    name = decl.split("(")[0].split()[-1]
    if name not in FORCE:
        return m.group(0)
    # strip 'native'
    decl = decl.replace(" native ", " ", 1)
    if decl.rstrip().endswith("native"):
        decl = decl.rstrip()[:-len("native")].rstrip()
    return (decl + "\n    .locals 1\n\n"
            "    const/4 v0, 0x1\n\n    return v0\n.end method")


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else r"Z:\hermes\instapro\decoded"
    p = os.path.join(base, "smali_classes20", GOLD)
    if not os.path.exists(p):
        print("MISSING", p); return
    txt = open(p, encoding="utf-8", errors="ignore").read()
    new, n = METHOD.subn(repl, txt)
    forced = sum(1 for name in FORCE if (name + "()Z") in new and ("const/4 v0, 0x1" in new))
    open(p, "w", encoding="utf-8", newline="").write(new)
    print(f"forced {len(FORCE)} bool getter(s) -> true in {GOLD}")


if __name__ == "__main__":
    main()
