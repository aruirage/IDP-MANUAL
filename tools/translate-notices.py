import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'manual' / 'index.html'
OUTPUT = ROOT / 'manual' / 'manual-notices.generated.json'


class Node:
    def __init__(self, tag='', attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs or []), parent, []


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root, self.current = Node('root'), None
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in {'br', 'img', 'input', 'meta', 'link', 'hr'}:
            self.current = node

    def handle_endtag(self, tag):
        node = self.current
        while node is not self.root:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


def walk(node):
    if isinstance(node, str):
        return
    yield node
    for child in node.children:
        yield from walk(child)


def render(node, labels):
    if isinstance(node, str):
        return node
    if 'ui-text' in node.attrs.get('class', '').split():
        token = f'[[UI_{len(labels) + 1:02d}]]'
        labels[token] = ''.join(render(child, {}) for child in node.children).strip()
        return token
    return ''.join(render(child, labels) for child in node.children)


def translate(text, target):
    query = urlencode({'q': text, 'langpair': f'ja|{target}', 'de': 'translator@example.com'})
    request = Request('https://api.mymemory.translated.net/get?' + query, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
    return re.sub(r'\s+', ' ', result['responseData']['translatedText']).strip()


parser = Parser()
parser.feed(SOURCE.read_text(encoding='utf-8'))
entries = []
for node in walk(parser.root):
    if node.tag != 'div' or 'notice' not in node.attrs.get('class', '').split():
        continue
    labels = {}
    source = re.sub(r'\s+', ' ', render(node, labels)).strip()
    if not re.search(r'[\u3040-\u30ff]', source):
        continue
    entries.append({'source_ja': source, 'ui_text': labels, 'zh-CN': translate(source, 'zh-CN'), 'en': translate(source, 'en')})
    time.sleep(0.2)

OUTPUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'translated {len(entries)} notice blocks')