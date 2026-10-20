"""manual-copy-to-translate.json に「カスタム関数」行の翻訳を追記する。

既存ファイルは ui_text が1行にインライン展開されている（例: "ui_text": {"[[UI_01]]": "..."}）。
json.dump で丸ごと書き直すと全件が複数行に展開されて diff が汚れるため、
末尾にテキストとして追記し、既存部分は一切触らない。
"""
import json
import re
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
json_path = root / 'manual-copy-to-translate.json'
html_path = root / 'index.html'
orig_path = Path('/tmp/mctt.orig.json')

NEW = [
    {
        "id": "manual-0504",
        "source_ja": "ファイル名を生成します。入力変数で受け取った値とスクリプトの記述内容から命名し、拡張子は元ファイルを引き継ぎます。既定のスクリプトはタイムスタンプ・証券番号・請求番号・帳票ごとのファイルコード・連番を組み合わせます。",
        "ui_text": {},
        "zh-CN": "生成文件名。根据输入变量接收到的值与脚本中的描述进行命名，扩展名沿用原文件。默认脚本组合时间戳、保单号、理赔编号、单据类型对应的文件代码与连番。",
        "en": "Generates file names. Names are built from the values received through the input variables and the logic written in the script, and the extension is carried over from the original file. The default script combines a timestamp, policy number, claim number, per-document-type file code, and a sequence number.",
    },
    {
        "id": "manual-0505",
        "source_ja": "files[]（改名後のファイル一覧）、renamedFileCount",
        "ui_text": {},
        "zh-CN": "files[]（改名后的文件列表）、renamedFileCount",
        "en": "files[] (list of renamed files), renamedFileCount",
    },
]


def normalize(value):
    return re.sub(r'\s+', ' ', value).strip()


def clean_td(inner):
    return normalize(re.sub(r'<[^>]+>', '', inner))


def fmt(item):
    return '\n'.join([
        '  {',
        f'    "id": {json.dumps(item["id"], ensure_ascii=False)},',
        f'    "source_ja": {json.dumps(item["source_ja"], ensure_ascii=False)},',
        '    "ui_text": {},',
        f'    "zh-CN": {json.dumps(item["zh-CN"], ensure_ascii=False)},',
        f'    "en": {json.dumps(item["en"], ensure_ascii=False)}',
        '  }',
    ])


html = html_path.read_text(encoding='utf-8')
td_sources = {clean_td(inner) for inner in re.findall(r'<td>(.*?)</td>', html, re.S)}
missing = [item['id'] for item in NEW if item['source_ja'] not in td_sources]
if missing:
    for item in NEW:
        mark = 'ok     ' if item['source_ja'] in td_sources else 'MISSING'
        print(f'{mark} {item["id"]}')
    raise SystemExit('index.html 側のテキストと一致しないため追記を中止しました')

# 追記先の元データ。git から取り直した原本を優先し、無ければ現行ファイルを使う。
base_path = orig_path if orig_path.exists() else json_path
base = base_path.read_text(encoding='utf-8')
if json_path.read_text(encoding='utf-8') != base:
    shutil.copyfile(base_path, json_path)

current = json_path.read_text(encoding='utf-8')
entries = json.loads(current)
existing_ids = {e['id'] for e in entries}
dup = [item['id'] for item in NEW if item['id'] in existing_ids]
if dup:
    raise SystemExit(f'already present: {dup}')

body = current.rstrip()
if not body.endswith(']'):
    raise SystemExit('unexpected tail: ' + body[-40:])
body = body[:-1].rstrip()
if not body.endswith('}'):
    raise SystemExit('unexpected tail before ]: ' + body[-40:])

out = body + ',\n' + ',\n'.join(fmt(item) for item in NEW) + '\n]\n'
parsed = json.loads(out)
if len(parsed) != len(entries) + len(NEW):
    raise SystemExit('entry count mismatch after append')

json_path.write_text(out, encoding='utf-8')
print('appended:', [item['id'] for item in NEW])
print('total:', len(parsed))
