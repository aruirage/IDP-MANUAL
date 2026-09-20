import json
import re
import sys
import time
from urllib.error import HTTPError
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'manual' / 'index.html'
OUTPUT = ROOT / 'manual' / 'translations.generated.js'
CACHE = ROOT / 'manual' / '.translations-progress.json'
DEEPL_URL = 'https://www2.deepl.com/jsonrpc?method=LMT_handle_texts'


class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.ui_depth = 0
        self.values = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag in {'script', 'style', 'noscript'}:
            self.skip_depth += 1
        if 'ui-text' in attributes.get('class', '').split():
            self.ui_depth += 1
        if self.skip_depth == 0 and self.ui_depth == 0:
            for name in ('alt', 'aria-label', 'title', 'placeholder'):
                value = attributes.get(name, '')
                if re.search(r'[\u3040-\u30ff]', value):
                    self.values.add(value)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'noscript'} and self.skip_depth:
            self.skip_depth -= 1
        if self.ui_depth and tag not in {'meta', 'link', 'img', 'input', 'br'}:
            self.ui_depth -= 1

    def handle_data(self, data):
        if self.skip_depth or self.ui_depth:
            return
        value = data.strip()
        if value and re.search(r'[\u3040-\u30ff]', value):
            self.values.add(value)


def translate_batch(values, target):
    payload = {
        'jsonrpc': '2.0',
        'method': 'LMT_handle_texts',
        'params': {
            'texts': [{'text': value, 'requestAlternatives': 0} for value in values],
            'splitting': 'newlines',
            'lang': {'source_lang': 'JA', 'target_lang': target},
            'timestamp': int(time.time() * 1000),
        },
        'id': int(time.time() * 1000),
    }
    request = Request(
        DEEPL_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Origin': 'https://www.deepl.com',
            'User-Agent': 'Mozilla/5.0',
        },
    )
    for attempt in range(6):
        try:
            with urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
            return [item['text'] for item in result['result']['texts']]
        except HTTPError as error:
            if error.code != 429 or attempt == 5:
                raise
            delay = 5 * (attempt + 1)
            print(f'rate limited; retrying in {delay}s', file=sys.stderr)
            time.sleep(delay)


def translate_all(values, target):
    progress = {}
    if CACHE.exists():
        progress = json.loads(CACHE.read_text(encoding='utf-8')).get(target, {})
    translated = dict(progress)
    values = sorted(values)
    for start in range(0, len(values), 10):
        batch = values[start:start + 10]
        if all(value in translated for value in batch):
            continue
        for source, output in zip(batch, translate_batch(batch, target)):
            translated[source] = output
        cache = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
        cache[target] = translated
        CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')
        print(f'{target}: {min(start + len(batch), len(values))}/{len(values)}', file=sys.stderr)
        time.sleep(0.25)
    return translated


html = SOURCE.read_text(encoding='utf-8')
collector = TextCollector()
collector.feed(html)
values = sorted(collector.values)
translations = {
    'zh-CN': translate_all(values, 'ZH'),
    'en': translate_all(values, 'EN-US'),
}
OUTPUT.write_text(
    'window.manualGeneratedTranslations = ' + json.dumps(translations, ensure_ascii=False) + ';\n',
    encoding='utf-8',
)
if CACHE.exists():
    CACHE.unlink()
print(f'generated {len(values)} source strings -> {OUTPUT}')