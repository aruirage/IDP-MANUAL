import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'manual' / 'index.html'
OUTPUT = ROOT / 'manual' / 'manual-copy-to-translate.json'

BLOCK_TAGS = {'p', 'li', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figcaption'}
ATTRIBUTE_NAMES = ('alt', 'aria-label', 'title', 'placeholder')


class Node:
    def __init__(self, tag='', attrs=None, parent=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.parent = parent
        self.children = []


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in {'meta', 'link', 'img', 'input', 'br', 'hr'}:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.current.tag == tag:
            self.current = self.current.parent

    def handle_endtag(self, tag):
        node = self.current
        while node is not self.root:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


def has_japanese(value):
    return bool(re.search(r'[\u3040-\u30ff]', value))


def has_block_child(node):
    return any(isinstance(child, Node) and child.tag in BLOCK_TAGS for child in node.children)


def render(node, labels):
    if isinstance(node, str):
        return re.sub(r'\s+', ' ', node)
    if 'ui-text' in node.attrs.get('class', '').split():
        label = ''.join(render(child, {}) for child in node.children).strip()
        token = f'[[UI_{len(labels) + 1:02d}]]'
        labels[token] = label
        return token
    return ''.join(render(child, labels) for child in node.children)


def walk(node):
    if isinstance(node, str):
        return
    yield node
    for child in node.children:
        yield from walk(child)


parser = DocumentParser()
parser.feed(SOURCE.read_text(encoding='utf-8'))
entries = []
seen = set()

for node in walk(parser.root):
    if node.tag not in BLOCK_TAGS or has_block_child(node):
        continue
    labels = {}
    source = re.sub(r'\s+', ' ', render(node, labels)).strip()
    if not source or not has_japanese(source):
        continue
    key = (source, tuple(labels.items()))
    if key in seen:
        continue
    seen.add(key)
    entries.append({
        'id': f'manual-{len(entries) + 1:04d}',
        'source_ja': source,
        'ui_text': labels,
        'zh-CN': '',
        'en': '',
    })

for node in walk(parser.root):
    if not isinstance(node, Node) or 'ui-text' in node.attrs.get('class', '').split():
        continue
    for name in ATTRIBUTE_NAMES:
        value = node.attrs.get(name, '').strip()
        if not has_japanese(value):
            continue
        key = (value, ())
        if key in seen:
            continue
        seen.add(key)
        entries.append({
            'id': f'manual-{len(entries) + 1:04d}',
            'source_ja': value,
            'ui_text': {},
            'zh-CN': '',
            'en': '',
        })

OUTPUT.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'exported {len(entries)} complete copy blocks to {OUTPUT}')
