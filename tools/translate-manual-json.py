import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'manual' / 'manual-copy-to-translate.json'
CACHE = ROOT / 'manual' / '.manual-translation-cache.json'
EMAIL = 'translator@example.com'


def translate(text, target):
    params = {
        'q': text,
        'langpair': f'ja|{target}',
        'de': EMAIL,
    }
    url = 'https://api.mymemory.translated.net/get?' + urlencode(params)
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for attempt in range(6):
        try:
            with urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
            break
        except (HTTPError, URLError, TimeoutError) as error:
            if attempt == 5:
                raise
            delay = 3 * (attempt + 1)
            print(f'translation request failed ({error}); retrying in {delay}s')
            time.sleep(delay)
    if result.get('responseStatus') != 200:
        raise RuntimeError(result.get('responseDetails') or result)
    return result['responseData']['translatedText']


items = json.loads(PATH.read_text(encoding='utf-8'))
cache = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
targets = [('zh-CN', 'zh-CN'), ('en', 'en')]

for field, target in targets:
    for index, item in enumerate(items, 1):
        if item.get(field):
            continue
        source = item['source_ja']
        cache_key = f'{item["id"]}:{field}'
        if cache_key not in cache:
            translated = translate(source, target)
            translated = re.sub(r'\s+', ' ', translated).strip()
            for token in re.findall(r'\[\[UI_\d+\]\]', source):
                if token not in translated:
                    translated = translated + ' ' + token
            cache[cache_key] = translated
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')
            time.sleep(0.15)
        item[field] = cache[cache_key]
        if index % 10 == 0:
            PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print(f'{field}: {index}/{len(items)}')
    PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

if CACHE.exists():
    CACHE.unlink()
print('translation complete')