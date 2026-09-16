#!/usr/bin/env python3
# PII
import pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
PATFILE = ROOT / "_build" / "pii_patterns.txt"
RULES = []
for ln in PATFILE.read_text(encoding="utf-8").splitlines():
    if "|" in ln:
        name, pat = ln.split("|", 1)
        RULES.append((name, re.compile(pat)))
def tracked():
    r = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True)
    return [f for f in r.stdout.split() if f]
bad = []
for f in tracked():
    p = ROOT / f
    if not p.is_file() or p.suffix.lower() not in (".html", ".md", ".xml", ".txt", ".json", ".toml", ".js", ".css"):
        continue
    if "pii_patterns" in f:
        continue
    try:
        t = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for name, rx in RULES:
        m = rx.search(t)
        if m:
            bad.append((f, name, m.group(0)[:40]))
if bad:
    print("PII GATE FAIL - push geumji. bangan:")
    for f, n, g in bad:
        print(" -", f, "|", n, "|", g)
    raise SystemExit(1)
print("PII GATE OK:", len(tracked()), "tracked files clean")
if __name__ == "__main__":
    pass
