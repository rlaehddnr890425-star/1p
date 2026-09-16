#!/usr/bin/env python3
# PII 게이트 생성기 — 마스킹-safe로 pii_check.py를 조립한다 (조각은 pii_patterns.txt에서)
import pathlib
HERE = pathlib.Path(__file__).resolve().parent
pats = (HERE / "pii_patterns.txt").read_text(encoding="utf-8").splitlines()
lines = []
push = lines.append
push("#!/usr/bin/env python3")
push("# 자