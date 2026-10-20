#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract translatable blocks from the P2 sections of index.html,
faithfully replicating the browser's blockSource() + normalizeCopy().

Phase 1 (this script): read-only. Prints per-section counts and writes a
review JSON of unique NEW sources (not yet in manual-copy-to-translate.json).
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'index.html'
JSON = ROOT / 'manual-copy-to-translate.json'

# Sections to scan.
P2_SECTIONS = [
    'p2-model', 'p2-api', 'p2-doctype', 'p2-scene', 'p2-case', 'p2-mytask',
    'phase2-overview', 'phase2-guide',
]
# Also count every other section's P2-tagged blocks? No — only the above.

BLOCK_TAGS = {'p', 'li', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figcaption'}


class Node:
    __slots__ = ('tag', 'classes', 'attrs', 'children')

    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.classes = set((self.attrs.get('class') or '').split())
        self.children = []


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('#root', {})
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        # pop until we find matching tag
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def normalize(value):
    return re.sub(r'\s+', ' ', value).strip()


def block_source(node):
    ui_index = [0]

    def read(n):
        if isinstance(n, str):
            return n
        if 'ui-text' in n.classes:
            ui_index[0] += 1
            return f'[[UI_{ui_index[0]:02d}]]'
        inner = ''.join(read(c) for c in n.children)
        if n.tag in ('strong', 'b'):
            return f'**{inner}**'
        return inner

    return normalize(''.join(read(c) for c in node.children))


def is_block(node):
    if not isinstance(node, Node):
        return False
    if node.tag in BLOCK_TAGS:
        return True
    if node.tag == 'div' and 'notice' in node.classes:
        return True
    return False


def ui_labels(node):
    """DOM-order list of .ui-text text content (mirrors blockSource numbering)."""
    out = []

    def walk(n):
        if isinstance(n, str):
            return
        if 'ui-text' in n.classes:
            out.append(''.join(c for c in n.children if isinstance(c, str)))
        for c in n.children:
            walk(c)

    walk(node)
    return out


def find_sections(root, ids):
    found = {}

    def walk(n, in_target):
        if isinstance(n, str):
            return
        sid = n.attrs.get('id')
        if sid in ids:
            found[sid] = n
            in_target = False  # stop descending into other sections
        for c in n.children:
            walk(c, in_target)

    walk(root, False)
    return found


def collect_blocks(section_node):
    blocks = []

    def walk(n):
        if isinstance(n, str):
            return
        if is_block(n):
            src = block_source(n)
            if src:  # skip empty
                labels = ui_labels(n)
                ui_text = {}
                for i, lab in enumerate(labels, 1):
                    ui_text[f'[[UI_{i:02d}]]'] = lab
                blocks.append({
                    'source': src,
                    'source_ja_key': src.replace('**', ''),
                    'ui_text': ui_text,
                })
        for c in n.children:
            walk(c)

    walk(section_node)
    return blocks


def main():
    html = HTML.read_text(encoding='utf-8')
    builder = TreeBuilder()
    builder.feed(html)
    sections = find_sections(builder.root, set(P2_SECTIONS))

    data = json.loads(JSON.read_text(encoding='utf-8'))
    existing_keys = set()
    for entry in data:
        existing_keys.add(normalize(entry.get('source_ja', '')))

    report = {'per_section': {}, 'total_blocks': 0, 'total_new': 0,
              'new_unique': 0, 'unique_new_sources': []}
    seen_unique = set()
    unique_new = []

    for sid in P2_SECTIONS:
        node = sections.get(sid)
        if not node:
            report['per_section'][sid] = {'blocks': 0, 'new': 0}
            continue
        blocks = collect_blocks(node)
        new = [b for b in blocks if normalize(b['source_ja_key']) not in existing_keys]
        report['per_section'][sid] = {'blocks': len(blocks), 'new': len(new)}
        report['total_blocks'] += len(blocks)
        report['total_new'] += len(new)
        for b in new:
            key = normalize(b['source_ja_key'])
            if key not in seen_unique:
                seen_unique.add(key)
                unique_new.append(b)

    report['new_unique'] = len(unique_new)
    report['unique_new_sources'] = unique_new

    out = ROOT / '.p2-extract-report.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"total_blocks={report['total_blocks']} total_new={report['total_new']} "
          f"new_unique={report['new_unique']}")
    for sid, info in report['per_section'].items():
        print(f"  {sid:16s} blocks={info['blocks']:3d} new={info['new']:3d}")
    print(f"report -> {out}")


if __name__ == '__main__':
    main()
