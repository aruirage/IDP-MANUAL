import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'manual' / 'index.html'
OUTPUT = ROOT / 'manual' / 'manual-ui-translations.generated.json'


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.values = set()
        self.current = False

    def handle_starttag(self, tag, attrs):
        if 'ui-text' in dict(attrs).get('class', '').split():
            self.depth += 1
            self.current = True

    def handle_endtag(self, tag):
        if self.depth and tag == 'span':
            self.depth -= 1
            self.current = bool(self.depth)

    def handle_data(self, data):
        if self.current and data.strip():
            self.values.add(re.sub(r'\s+', ' ', data).strip())


def translate(text, target):
    query = urlencode({'q': text, 'langpair': f'ja|{target}', 'de': 'translator@example.com'})
    request = Request('https://api.mymemory.translated.net/get?' + query, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())['responseData']['translatedText'].strip()


parser = Parser()
parser.feed(SOURCE.read_text(encoding='utf-8'))
values = sorted(parser.values)
result = {}
for value in values:
    result[value] = {'zh-CN': translate(value, 'zh-CN'), 'en': translate(value, 'en')}
    time.sleep(0.15)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'translated {len(result)} ui-text labels')