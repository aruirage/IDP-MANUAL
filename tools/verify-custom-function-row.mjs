// 「カスタム関数」行が 3 言語でどう描画されるかを実機で確認する。
// manual リポジトリには playwright が無いので workflow-ph2 側の依存を相対参照する。
// 使い方: node tools/verify-custom-function-row.mjs   (4321 で manual を配信しておく)
import { chromium } from '../../../workflow-ph2/node_modules/playwright/index.mjs';

const BASE = process.env.MANUAL_URL || 'http://127.0.0.1:4321/';

const browser = await chromium.launch({ channel: 'chrome' });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errors = [];
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));

const fails = [];
const check = (name, cond, detail) => {
  if (!cond) fails.push(`${name} :: ${JSON.stringify(detail)}`);
  console.log(`${cond ? 'ok  ' : 'FAIL'} ${name}${cond ? '' : ` :: ${JSON.stringify(detail)}`}`);
};

const ROW = `(() => {
  const tr = [...document.querySelectorAll('tr')].find((t) => /カスタム関数|自定义函数|Custom function/.test(t.textContent));
  if (!tr) return null;
  return [...tr.children].map((td) => td.textContent.replace(/\\s+/g, ' ').trim());
})()`;

const EXPECT = {
  ja: ['カスタム関数', 'ファイル名を生成します。', 'files[]（改名後のファイル一覧）、renamedFileCount'],
  'zh-CN': ['自定义函数', '生成文件名。', 'files[]（改名后的文件列表）、renamedFileCount'],
  en: ['Custom function', 'Generates file names.', 'files[] (list of renamed files), renamedFileCount'],
};

await page.goto(BASE, { waitUntil: 'networkidle' });
await page.waitForTimeout(500);

for (const lang of ['ja', 'zh-CN', 'en']) {
  await page.evaluate((value) => localStorage.setItem('neosai-manual-language', value), lang);
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(700);
  const row = await page.evaluate(ROW);
  console.log(`\n[${lang}]`, JSON.stringify(row, null, 0));
  const expect = EXPECT[lang];
  check(`${lang}: 行が存在する`, !!row, row);
  if (!row) continue;
  check(`${lang}: ノード名`, row[0] === expect[0], { got: row[0], want: expect[0] });
  check(`${lang}: 用途の冒頭`, row[1].startsWith(expect[1]), { got: row[1].slice(0, 40), want: expect[1] });
  check(`${lang}: 出力変数`, row[2] === expect[2], { got: row[2], want: expect[2] });
  check(`${lang}: 未置換トークンが残っていない`, !/\[\[UI_|\[\[LINK_|\*\*/.test(row.join(' ')), row.join(' '));
  try {
    await page.locator('tr').filter({ hasText: expect[0] }).first()
      .screenshot({ path: `/tmp/manual-custom-function-${lang}.png` });
  } catch (error) {
    console.log(`  (screenshot skipped: ${String(error.message).split('\n')[0]})`);
  }
}

console.log('\nconsole errors:', errors.length ? errors : 'none');
console.log(fails.length ? `\n${fails.length} 件 FAIL:\n${fails.join('\n')}` : '\nすべて PASS');
await browser.close();
process.exit(fails.length || errors.length ? 1 : 0);
