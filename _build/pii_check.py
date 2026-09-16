#!/usr/bin/env python3
# PII 게이트 — 공개 저장소에 운영자 개인정보가 섞이면 exit 1 (push 차단).
# 규칙 원본: AGENTS.md.  실명 등 민감 리터럴은 저장소 밖 로컬 파일에만 둔다(공개 금지).
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_PAT = ROOT / "_build" / "pii_patterns.txt"
LOCAL_PAT = pathlib.Path.home() / "Orca-P-Mac" / "p1" / "work" / "blog" / "ops" / "pii_local_patterns.txt"
SKIP = ("pii_patterns", "pii_local", "pii_check")


def load(path, required):
    if not path.is_file():
        if required:
            print(f"PII GATE FAIL — 필수 패턴 파일 없음: {path}")
            print("  (실명 등 민감 패턴은 저장소 밖 로컬 파일에만 둔다. 복원 후 다시 push)")
            raise SystemExit(1)
        return []
    out = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or "|" not in ln:
            continue
        name, pat = ln.split("|", 1)
        if not pat.strip():
            continue
        out.append((name, re.compile(pat)))
    return out


RULES = load(REPO_PAT, True) + load(LOCAL_PAT, True)


def tracked():
    r = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True)
    return [f for f in r.stdout.split() if f]


bad = []
for f in tracked():
    if any(s in f for s in SKIP):
        continue
    p = ROOT / f
    if not p.is_file() or p.suffix.lower() not in (".html", ".md", ".xml", ".txt", ".json", ".toml", ".js", ".css"):
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
    print("PII GATE FAIL — push 금지. 위반:")
    for f, n, g in bad:
        print(" -", f, "|", n, "|", g)
    raise SystemExit(1)
print("PII GATE OK:", len(tracked()), "tracked files clean")
