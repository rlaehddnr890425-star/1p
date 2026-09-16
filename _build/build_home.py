# -*- coding: utf-8 -*-
"""build_home: data/*.json -> index.html. 유효성 게이트 실패 시 SystemExit(1).
원칙: 카드·표의 수치는 JSON에만 존재하고, LLM/사람이 HTML에 수치를 직접 쓰지 않는다."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FUNDS = json.loads((ROOT / 'data' / 'funds.json').read_text())
NOTICES = json.loads((ROOT / 'data' / 'notices.json').read_text())

STAMP_KEYS = ('verified_at', 'source', 'apply', 'status', 'who', 'amount', 'rate', 'term', 'method', 'title', 'category', 'channel')
FUND_KEYS = ('name', 'channel', 'who', 'amount', 'rate', 'term', 'guide')

def validate():
    errs = []
    for n in NOTICES['funds']:
        miss = [k for k in STAMP_KEYS if not n.get(k)]
        if miss:
            errs.append('notice ' + n.get('id','?') + ' 필드 누락: ' + ','.join(miss))
    for f in FUNDS['funds']:
        miss = [k for k in FUND_KEYS if not f.get(k)]
        if miss:
            errs.append('fund ' + f.get('name','?') + ' 필드 누락: ' + ','.join(miss))
    if not re.match(r'^\d{4}-\d\d-\d\d \d\d:\d\d$', NOTICES['updated_at']):
        errs.append('notices.updated_at 형식 오류')
    if len(FUNDS['funds']) != 13:
        errs.append('funds 수불일: ' + str(len(FUNDS['funds'])))
    return errs

def notice_cards():
    out = []
    for n in NOTICES['funds']:
        rows = ''.join('<div><dt>' + k + '</dt><dd>' + n[a] + '</dd></div>'
                          for k, a in (('누가','who'),('얼마','amount'),('금리','rate'),('기간','term'),('방식','method')))
        out.append('<div class="ncard"><div class="nhead"><span class="st">' + n['status']
            + '</span><span class="cat">' + n['category'] + ' · ' + n['channel'] + '</span></div><h3>'
            + n['title'] + '</h3><dl>' + rows + '</dl><div class="nfoot"><a class="btn sm" href="'
            + n['apply'] + '" rel="nofollow">신청처</a><a class="ghost" href="posts/policy-fund-map.html">자격·요건 보기</a></div>'
            + '<p class="vstamp">원문 ' + n['source'][:14] + ' · 검증 ' + n['verified_at'] + '</p></div>')
    return chr(10).join(out)

def fund_rows():
    out = []
    for f in FUNDS['funds']:
        cls = 'd' if f['channel'] == '직접' else 'a'
        out.append('<tr><td><b>' + f['name'] + '</b><span class="chan ' + cls + '">' + f['channel']
            + '</span></td><td class="dim">' + f['who'] + '</td><td>' + f['amount']
            + '</td><td class="num">' + f['rate'] + '</td><td class="dim">' + f['term'] + '</td></tr>')
    return chr(10).join(out)

def main():
    errs = validate()
    if errs:
        print('BUILD FAIL:'); [print(' -', e) for e in errs]
        raise SystemExit(1)
    tpl = (ROOT / 'templates' / 'home.tpl.html').read_text()
    html = (tpl.replace('{{NOTICE_CARDS}}', notice_cards())
                .replace('{{FUND_ROWS}}', fund_rows())
                .replace('{{VERIFIED_AT}}', NOTICES['updated_at'])
                .replace('{{N_OPEN}}', str(len(NOTICES['funds'])))
                .replace('{{N_FUNDS}}', str(len(FUNDS['funds']))))
    if '{{' in html:
        print('BUILD FAIL: 미대체 템플릿 토큰 잔존'); raise SystemExit(1)
    (ROOT / 'index.html').write_text(html)
    print('index.html built:', len(html), 'chars,', len(NOTICES['funds']), 'cards,', len(FUNDS['funds']), 'funds')

if __name__ == '__main__':
    main()
