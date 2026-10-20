#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix P2 entries whose [[UI_nn]] tokens or **bold** markers were corrupted by
the first registration pass (MyMemory dropped the private-use sentinel
boundaries). Re-translates only the broken entries with the corrected pipeline
that keeps [[UI_nn]] literal and shields **bold** via [[BLD_nn]] placeholders.
"""
import json
import re
import time
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / 'manual-copy-to-translate.json'
REPORT = ROOT / '.p2-extract-report.json'
CACHE = ROOT / '.p2-fix-cache.json'
EMAIL = 'translator@example.com'

BOLD_RE = re.compile(r'\*\*([^*]+)\*\*')
TOK_RE = re.compile(r'\[\[UI_\d+\]\]')
CACHE_DATA = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}


def normalize(v):
    return re.sub(r'\s+', ' ', v).strip()


def tr(text, lang):
    if not text.strip():
        return text
    key = f'{text}::{lang}'
    if key in CACHE_DATA:
        return CACHE_DATA[key]
    params = {'q': text, 'langpair': f'ja|{lang}', 'de': EMAIL}
    url = 'https://api.mymemory.translated.net/get?' + urlencode(params)
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    out = None
    for attempt in range(4):
        try:
            with urlopen(req, timeout=30) as resp:
                d = json.loads(resp.read().decode('utf-8'))
            out = (d.get('responseData') or {}).get('translatedText')
            if out is not None:
                break
            time.sleep(1.5 * (attempt + 1))
        except (URLError, TimeoutError, Exception):
            time.sleep(2 * (attempt + 1))
    if out is None:
        out = text
    out = re.sub(r'\s+', ' ', out).strip()
    CACHE_DATA[key] = out
    return out


def block(source, lang):
    bmap = {}
    btrans = {}

    def rb(m):
        inner = m.group(1)
        if inner not in bmap:
            k = f'[[BLD{len(bmap):02d}]]'
            bmap[inner] = k
            btrans[k] = f'**{tr(inner, lang)}**'
        return bmap[inner]

    s = BOLD_RE.sub(rb, source)
    s = tr(s, lang)
    for k, v in btrans.items():
        s = s.replace(k, v)
    return s


def needs_fix(entry, orig_source):
    ja = entry['source_ja']
    st = set(TOK_RE.findall(ja))
    zt = set(TOK_RE.findall(entry['zh-CN']))
    et = set(TOK_RE.findall(entry['en']))
    tok_bad = (st != zt) or (st != et)
    had_bold = orig_source and ('**' in orig_source)
    bold_bad = bool(had_bold) and ('**' not in entry['zh-CN'] or '**' not in entry['en'])
    return tok_bad or bold_bad


def main():
    data = json.loads(JSON.read_text(encoding='utf-8'))
    rep = json.loads(REPORT.read_text(encoding='utf-8'))
    src_map = {normalize(s['source_ja_key']): s for s in rep['unique_new_sources']}

    new = data[-265:]
    by_key = {}
    for idx, e in enumerate(data):
        by_key.setdefault(normalize(e['source_ja']), idx)

    fixed = 0
    for e in new:
        ja = e['source_ja']
        orig = src_map.get(normalize(ja))
        orig_source = orig['source'] if orig else None
        if not needs_fix(e, orig_source):
            continue
        src = orig_source if orig_source else ja
        zh = block(src, 'zh-CN')
        en = block(src, 'en')
        idx = by_key[normalize(ja)]
        data[idx]['zh-CN'] = zh
        data[idx]['en'] = en
        fixed += 1
        if fixed % 5 == 0:
            CACHE.write_text(json.dumps(CACHE_DATA, ensure_ascii=False), encoding='utf-8')
            JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print(f'  fixed {fixed}')

    CACHE.write_text(json.dumps(CACHE_DATA, ensure_ascii=False), encoding='utf-8')
    JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'fixed={fixed} total={len(data)}')


if __name__ == '__main__':
    main()
