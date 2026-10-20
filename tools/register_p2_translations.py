#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Register P2 section translations into manual-copy-to-translate.json.

Reads .p2-extract-report.json (unique new sources), translates each from JA
to zh-CN / en via MyMemory, preserving [[UI_nn]] tokens and **bold** markers,
and appends entries to the JSON. Idempotent + resumable via a cache file.
Finally bumps the ?v= cache-busting version in index.html (17 -> 18).
"""
import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / 'manual-copy-to-translate.json'
HTML = ROOT / 'index.html'
REPORT = ROOT / '.p2-extract-report.json'
CACHE = ROOT / '.p2-translation-cache.json'
EMAIL = 'translator@example.com'

TOKEN_RE = re.compile(r'\[\[UI_\d+\]\]')
BOLD_RE = re.compile(r'\*\*([^*]+)\*\*')
WARN_COUNT = 0


def normalize(value):
    return re.sub(r'\s+', ' ', value).strip()


def translate_text(text, lang):
    if not text.strip():
        return text
    key = f'{text}::{lang}'
    if key in CACHE_DATA:
        return CACHE_DATA[key]
    params = {'q': text, 'langpair': f'ja|{lang}', 'de': EMAIL}
    url = 'https://api.mymemory.translated.net/get?' + urlencode(params)
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    out = None
    last_detail = None
    for attempt in range(4):
        try:
            with urlopen(request, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
            out = (result.get('responseData') or {}).get('translatedText')
            last_detail = result.get('responseDetails')
            if result.get('responseStatus') != 200 or out is None:
                out = None
                time.sleep(1.5 * (attempt + 1))
                continue
            break
        except (HTTPError, URLError, TimeoutError) as err:
            last_detail = err
            time.sleep(2 * (attempt + 1))
    if out is None:
        # Best-effort fallback: keep the (Japanese) source so rendering still works.
        global WARN_COUNT
        WARN_COUNT += 1
        print(f'  WARN translate None ({lang}): {text[:50]!r} detail={last_detail}')
        out = text
    out = re.sub(r'\s+', ' ', out).strip()
    CACHE_DATA[key] = out
    return out


def translate_block(source, lang):
    """Preserve [[UI_nn]] and **bold** while translating Japanese prose."""
    tok_map = {}

    def rt(m):
        t = m.group(0)
        if t not in tok_map:
            tok_map[t] = f'\uE000{len(tok_map)}\uE001'
        return tok_map[t]

    s = TOKEN_RE.sub(rt, source)

    bold_map = {}
    bold_trans = {}

    def rb(m):
        inner = m.group(1)
        if inner not in bold_map:
            sen = f'\uE010{len(bold_map)}\uE011'
            bold_map[inner] = sen
            bt = translate_text(inner, lang)
            bold_trans[sen] = f'**{bt}**'
        return bold_map[inner]

    s = BOLD_RE.sub(rb, s)
    s = translate_text(s, lang)
    for sen, val in bold_trans.items():
        s = s.replace(sen, val)
    for t, sen in tok_map.items():
        s = s.replace(sen, t)
    return s


def main():
    global CACHE_DATA
    data = json.loads(JSON.read_text(encoding='utf-8'))
    CACHE_DATA = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    sources = report['unique_new_sources']

    existing_keys = {normalize(e.get('source_ja', '')) for e in data}
    existing_ids = [int(re.sub(r'\D', '', e['id'])) for e in data if re.fullmatch(r'manual-\d+', e['id'])]
    next_id = max(existing_ids) + 1 if existing_ids else 1

    added = 0
    skipped = 0
    try:
        for b in sources:
            key = normalize(b['source_ja_key'])
            if key in existing_keys:
                skipped += 1
                continue
            src = b['source']  # with ** and [[UI_nn]]
            zh = translate_block(src, 'zh-CN')
            en = translate_block(src, 'en')
            data.append({
                'id': f'manual-{next_id:04d}',
                'source_ja': b['source_ja_key'],
                'ui_text': b['ui_text'],
                'zh-CN': zh,
                'en': en,
            })
            existing_keys.add(key)
            next_id += 1
            added += 1
            if added % 5 == 0:
                CACHE.write_text(json.dumps(CACHE_DATA, ensure_ascii=False), encoding='utf-8')
                JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                print(f'  progress: added {added} (next id manual-{next_id:04d})')
            if WARN_COUNT > 25:
                print('  too many translation failures; stopping early')
                break
    except Exception as exc:
        print(f'  ERROR: {exc}')

    CACHE.write_text(json.dumps(CACHE_DATA, ensure_ascii=False), encoding='utf-8')
    JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # bump cache-busting version 17 -> 18
    html = HTML.read_text(encoding='utf-8')
    new_html = html.replace('manual-copy-to-translate.json?v=17', 'manual-copy-to-translate.json?v=18')
    new_html = new_html.replace('manual-notices.generated.json?v=17', 'manual-notices.generated.json?v=18')
    HTML.write_text(new_html, encoding='utf-8')
    bumped = new_html != html

    print(f'added={added} skipped={skipped} total_entries={len(data)} v_bumped={bumped}')


if __name__ == '__main__':
    main()
