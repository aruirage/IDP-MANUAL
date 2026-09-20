#!/usr/bin/env python3
"""Restructure modules: 5 sections, richer content, NeosAI module-nav."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "manual/index.html"

MODULE_IDS = [
    "admin-model-config",
    "admin-api-config",
    "admin-master-data-config",
    "admin-doctype-config",
    "admin-scene-config",
    "admin-data-mapping-config",
    "admin-ai-verification-config",
    "operator-upload-module",
    "operator-case-module",
    "operator-task-module",
    "system-user-management",
    "system-role-management",
    "system-security-settings",
]

SECTIONS = [
    ("perm", "ロールと権限", "誰がこの画面を操作できるか"),
    ("ops", "画面操作", "ボタン・画面の操作手順"),
    ("scene", "利用タイミング", "いつ・何のために設定するか"),
    ("effect", "実現効果", "設定前後で何が変わるか"),
    ("impact", "他モジュールとの連動", "影響する／影響されるモジュール"),
]

MODULE: dict[str, dict[str, str]] = {
    "admin-model-config": {
        "perm": """<table class="role-table">
              <thead><tr><th>ロール</th><th>操作できること</th><th>操作できないこと</th></tr></thead>
              <tbody>
                <tr><td><span class="ui-text">admin</span></td><td><span class="ui-text">API 接続</span> の追加・編集、<span class="ui-text">接続テスト</span>、<span class="ui-text">用途割当</span></td><td>—</td></tr>
                <tr><td><span class="ui-text">操作員</span> / 操作管理者</td><td>—（本画面へのアクセス不可）</td><td>モデル接続の変更</td></tr>
              </tbody>
            </table>
            <p class="module-note">メニュー到達可否は <a class="jump-link" href="#system-role-management">権限管理</a> のメニュー権限で制御します。詳細は <a class="jump-link" href="#overview-roles">ロール設定</a> を参照。</p>""",
        "scene": """<ul class="scene-list">
              <li><strong>初回環境構築時</strong> — OCR・AI 検証を動かす前に LLM 接続を登録・テスト。<span class="ui-text">+ 接続を追加</span> → 入力 → <span class="ui-text">保存</span> → <span class="ui-text">接続テスト</span> → <span class="ui-text">用途割当</span>。</li>
              <li><strong>モデル変更・障害復旧時</strong> — キー／プロバイダ更新後は <span class="ui-text">接続テスト</span> を必ず再実行。未テスト接続は読取モデル候補に出ません。</li>
            </ul>""",
        "effect": """<div class="effect-compare">
              <div class="effect-col"><p class="effect-col-title">設定前</p><p>接続未登録・未テストのため <span class="ui-text">読取モデル設定</span> が空。OCR・AI 検証が実行不可。</p></div>
              <div class="effect-col is-after"><p class="effect-col-title">設定後</p><p><span class="ui-text">有効</span> かつ用途割当済みモデルが OCR 抽出・AI 検証・帳票読取で呼び出される。</p></div>
            </div>""",
        "impact": """<ul class="module-links">
              <li><strong>影響する</strong> — <a class="jump-link" href="#admin-doctype-config">帳票タイプ設定</a>、<a class="jump-link" href="#admin-ai-verification-config">AI検証設定</a>、<a class="jump-link" href="#admin-scene-config">業務シーン設定</a></li>
              <li><strong>影響を受ける</strong> — 変更は有効化以降の新規モデル呼び出しから反映（処理中案件は開始時点の設定を継続）</li>
            </ul>
            <p class="module-note">モデル設定の変更は、有効化後に新しく発生するモデル呼び出しから適用されます。すでに開始済みの案件、投入済みの非同期タスク、再実行していない OCR／AI検証リクエストには、開始時点のモデル設定が引き続き使用されます。</p>""",
    },
    "admin-api-config": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作できること</th></tr></thead>
              <tbody>
                <tr><td><span class="ui-text">admin</span></td><td><span class="ui-text">API設定</span> 閲覧・API Key 確認（詳細は API 文書）</td></tr>
                <tr><td>その他</td><td>—</td></tr>
              </tbody></table>""",
        "scene": """<ul class="scene-list">
              <li><strong>基幹連携開始前</strong> — <span class="ui-text">業務ルール設定</span> → <span class="ui-text">API設定</span> を開き、Open API 入口と Key を確認。実装手順は API 接続文書を参照。</li>
            </ul>""",
        "effect": """<div class="effect-compare">
              <div class="effect-col"><p class="effect-col-title">設定前</p><p>手動アップロードのみ。</p></div>
              <div class="effect-col is-after"><p class="effect-col-title">設定後</p><p>API 経由で案件・ファイル投入が可能。</p></div>
            </div>""",
        "impact": """<ul class="module-links">
              <li><strong>連動</strong> — 投入後の処理は <a class="jump-link" href="#admin-scene-config">業務シーン設定</a> に従う</li>
              <li><strong>通知</strong> — 通知 URL は業務シーン <span class="ui-text">通知設定</span> のイベントで起動</li>
            </ul>
            <p class="module-note">API の接続先やリクエスト仕様は、このマニュアルではなく API 文書を参照してください。</p>""",
    },
    "admin-master-data-config": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody><tr><td><span class="ui-text">admin</span></td><td>マスター作成・<span class="ui-text">列設定</span>・<span class="ui-text">一括インポート</span>・<span class="ui-text">ベクトル化再実行</span></td></tr></tbody></table>""",
        "scene": """<ul class="scene-list">
              <li><strong>マスタ照合前</strong> — <span class="ui-text">+ マスター追加</span> → <span class="ui-text">列設定</span> → データ登録。<span class="ui-text">ベクトル化状態</span> が <span class="ui-text">完了</span> 後に帳票側で照合設定。</li>
            </ul>""",
        "effect": """<div class="effect-compare">
              <div class="effect-col"><p class="effect-col-title">設定前</p><p>OCR 値に表記ゆれが残る。</p></div>
              <div class="effect-col is-after"><p class="effect-col-title">設定後</p><p>照合成功時にマスター正規値を書き戻す。</p></div>
            </div>""",
        "impact": """<ul class="module-links">
              <li><strong>影響先</strong> — <a class="jump-link" href="#admin-doctype-config">帳票タイプ設定</a> <span class="ui-text">マスタ照合</span>、<a class="jump-link" href="#admin-ai-verification-config">AI検証設定</a></li>
            </ul>""",
    },
    "admin-doctype-config": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody><tr><td><span class="ui-text">admin</span></td><td>帳票タイプ 5 ステップ設定・公開・効果テスト</td></tr></tbody></table>""",
        "scene": """<ul class="scene-list">
              <li><strong>新帳票取込</strong> — <span class="ui-text">+ タイプ追加</span> から AI分類 → AI読取 → 処理ルール → 画像処理 → 効果テスト。</li>
              <li><strong>業務シーン連携前</strong> — タイプを公開してから <a class="jump-link" href="#admin-scene-config">業務シーン設定</a> に帳票を追加。</li>
            </ul>""",
        "effect": """<div class="effect-compare">
              <div class="effect-col"><p class="effect-col-title">設定前</p><p>分類・読取未定義。<span class="ui-text">未集約ファイル</span> が増えやすい。</p></div>
              <div class="effect-col is-after"><p class="effect-col-title">設定後</p><p>分類・OCR・前処理・後処理が公開版どおり実行される。</p></div>
            </div>""",
        "impact": """<ul class="module-links">
              <li><strong>前提</strong> — <a class="jump-link" href="#admin-model-config">モデル設定</a>、<a class="jump-link" href="#admin-master-data-config">マスターデータ設定</a></li>
              <li><strong>影響先</strong> — <a class="jump-link" href="#admin-scene-config">業務シーン設定</a>、<a class="jump-link" href="#admin-data-mapping-config">データマッピング設定</a>、<a class="jump-link" href="#admin-ai-verification-config">AI検証設定</a>、<a class="jump-link" href="#operator-task-module">マイタスク</a></li>
            </ul>""",
    },
    "admin-scene-config": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody><tr><td><span class="ui-text">admin</span></td><td>4 ステップ編集・<span class="ui-text">公開</span></td></tr></tbody></table>""",
        "scene": """<ul class="scene-list">
              <li><strong>帳票タイプ公開後</strong> — 案件集約 → ワークフロー → 通知 → 出力を設定し <span class="ui-text">設定チェック</span> → <span class="ui-text">公開</span>。</li>
            </ul>""",
        "effect": """<div class="effect-compare">
              <div class="effect-col"><p class="effect-col-title">公開前</p><p>操作員の <span class="ui-text">新規アップロード</span> にシーン非表示。</p></div>
              <div class="effect-col is-after"><p class="effect-col-title">公開後</p><p>アップロードから出力までワークフローが実行される。</p></div>
            </div>""",
        "impact": """<ul class="module-links">
              <li><strong>前提</strong> — <a class="jump-link" href="#admin-doctype-config">帳票タイプ設定</a>、<a class="jump-link" href="#admin-data-mapping-config">データマッピング設定</a>、<a class="jump-link" href="#admin-ai-verification-config">AI検証設定</a></li>
              <li><strong>影響先</strong> — <a class="jump-link" href="#operator-upload-module">新規アップロード</a>、<a class="jump-link" href="#operator-case-module">案件一覧</a>、<a class="jump-link" href="#operator-task-module">マイタスク</a></li>
            </ul>""",
    },
    "admin-data-mapping-config": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody><tr><td><span class="ui-text">admin</span></td><td>マッピングルール生成・編集</td></tr></tbody></table>""",
        "scene": """<ul class="scene-list">
              <li><strong>横断検証前</strong> — 帳票タイプで読取項目定義後、<span class="ui-text">マッピングルール生成</span> で標準変数へ集約。</li>
            </ul>""",
        "effect": """<div class="effect-compare">
              <div class="effect-col"><p class="effect-col-title">設定前</p><p>帳票ごとにフィールド名がバラバラ。</p></div>
              <div class="effect-col is-after"><p class="effect-col-title">設定後</p><p>標準変数へ OCR 値が集約され横断参照可能。</p></div>
            </div>""",
        "impact": """<ul class="module-links">
              <li><strong>前提</strong> — <a class="jump-link" href="#admin-doctype-config">帳票タイプ設定</a></li>
              <li><strong>影響先</strong> — <a class="jump-link" href="#admin-ai-verification-config">AI検証設定</a>、<a class="jump-link" href="#admin-scene-config">業務シーン設定</a> 出力項目</li>
            </ul>""",
    },
    "admin-ai-verification-config": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody><tr><td><span class="ui-text">admin</span></td><td>6 種検証ルールの追加・編集</td></tr></tbody></table>""",
        "scene": """<ul class="scene-list">
              <li><strong>自動検証導入時</strong> — 帳票・マッピング設定後、必須フィールド・必要書類・整合性ルール等を登録。</li>
            </ul>""",
        "effect": """<div class="effect-compare">
              <div class="effect-col"><p class="effect-col-title">設定前</p><p>提出漏れ・矛盾はすべて人工確認。</p></div>
              <div class="effect-col is-after"><p class="effect-col-title">設定後</p><p>ルール命中で <span class="code-text">verifyResult</span> 出力。例外のみ <span class="ui-text">マイタスク</span>。</p></div>
            </div>""",
        "impact": """<ul class="module-links">
              <li><strong>実行場所</strong> — <a class="jump-link" href="#admin-scene-config">業務シーン設定</a> <span class="ui-text">AI検証</span> ノード</li>
              <li><strong>影響先</strong> — <a class="jump-link" href="#operator-task-module">マイタスク</a> AI 検証確認</li>
            </ul>
            <p class="module-note">AI検証ルールは、<span class="ui-text">業務シーン設定</span> の <span class="ui-text">ワークフロー設定</span> 内にある <span class="ui-text">AI検証</span> ノードで適用されます。</p>""",
    },
    "operator-upload-module": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody>
                <tr><td><span class="ui-text">操作員</span></td><td>公開済みシーンへ資料アップロード</td></tr>
                <tr><td>操作管理者</td><td>同上</td></tr>
              </tbody></table>""",
        "scene": """<ul class="scene-list">
              <li><strong>新規受付</strong> — <span class="ui-text">新規アップロード</span> → シーン選択 → ファイル投入 → 分類・案件集約が自動起動。</li>
            </ul>""",
        "effect": """<div class="effect-compare">
              <div class="effect-col"><p class="effect-col-title">前</p><p>案件未生成。</p></div>
              <div class="effect-col is-after"><p class="effect-col-title">後</p><p>案件 ID 付与・ワークフロー起動。</p></div>
            </div>""",
        "impact": """<ul class="module-links">
              <li><strong>前提</strong> — <a class="jump-link" href="#admin-scene-config">業務シーン設定</a> 公開済み</li>
              <li><strong>次工程</strong> — <a class="jump-link" href="#operator-case-module">案件一覧</a>、<a class="jump-link" href="#operator-task-module">マイタスク</a></li>
            </ul>""",
    },
    "operator-case-module": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody>
                <tr><td><span class="ui-text">操作員</span></td><td>進捗確認・詳細・補件</td></tr>
                <tr><td>操作管理者</td><td>＋担当者変更・処理中止</td></tr>
              </tbody></table>""",
        "scene": """<ul class="scene-list">
              <li><strong>進捗確認</strong> — アップロード後、集約済み案件・<span class="ui-text">未集約ファイル</span> を一覧で確認。</li>
            </ul>""",
        "effect": """<p>案件単位で OCR 進捗とワークフロー状態を把握できる。</p>""",
        "impact": """<ul class="module-links">
              <li><strong>連動</strong> — 担当者・ステータス変更は <a class="jump-link" href="#operator-task-module">マイタスク</a> へ反映</li>
            </ul>""",
    },
    "operator-task-module": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody>
                <tr><td><span class="ui-text">操作員</span></td><td>OCR 人工確認・AI 検証確認・エクスポート</td></tr>
                <tr><td>操作管理者</td><td>同上（担当者として割当時）</td></tr>
              </tbody></table>""",
        "scene": """<ul class="scene-list">
              <li><strong>要確認タスク発生時</strong> — <span class="code-text">reviewRequired</span> 等で <span class="ui-text">マイタスク</span> にタスク表示 → 確認・修正 → 次工程。</li>
            </ul>""",
        "effect": """<div class="effect-compare">
              <div class="effect-col"><p class="effect-col-title">確認前</p><p>人工確認ノードで停止。</p></div>
              <div class="effect-col is-after"><p class="effect-col-title">確認後</p><p>ワークフロー再開・エクスポート可能。</p></div>
            </div>""",
        "impact": """<ul class="module-links">
              <li><strong>トリガー</strong> — <a class="jump-link" href="#admin-scene-config">業務シーン設定</a>、<a class="jump-link" href="#admin-doctype-config">帳票タイプ設定</a>、<a class="jump-link" href="#admin-ai-verification-config">AI検証設定</a></li>
            </ul>""",
    },
    "system-user-management": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody><tr><td><span class="ui-text">admin</span></td><td>ユーザー追加・無効化・パスワードリセット</td></tr></tbody></table>""",
        "scene": """<ul class="scene-list"><li><strong>入退社時</strong> — <span class="ui-text">+ ユーザー追加</span> または無効化。</li></ul>""",
        "effect": """<p>有効ユーザーのみログイン可能。</p>""",
        "impact": """<ul class="module-links"><li><strong>連動</strong> — <a class="jump-link" href="#system-role-management">権限管理</a>、全業務モジュール</li></ul>""",
    },
    "system-role-management": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody><tr><td><span class="ui-text">admin</span></td><td>権限テンプレート・メニュー権限編集</td></tr></tbody></table>""",
        "scene": """<ul class="scene-list"><li><strong>メニュー分離</strong> — admin / 操作員で見えるメニューを切り分け。</li></ul>""",
        "effect": """<p>ロールごとに到達可能な画面が変わる。</p>""",
        "impact": """<ul class="module-links"><li><strong>影響</strong> — 全 admin / operator モジュールのメニュー表示</li></ul>""",
    },
    "system-security-settings": {
        "perm": """<table class="role-table"><thead><tr><th>ロール</th><th>操作</th></tr></thead>
              <tbody><tr><td><span class="ui-text">admin</span></td><td>保存期限・セッション設定</td></tr></tbody></table>""",
        "scene": """<ul class="scene-list"><li><strong>ポリシー策定時</strong> — データ保持期限と無操作ログアウトを設定。</li></ul>""",
        "effect": """<p>期限超過データは削除（復元不可）。全ユーザーに適用。</p>""",
        "impact": """<ul class="module-links"><li><strong>影響</strong> — 全ユーザー・全案件データ</li></ul>""",
    },
}

NAV_ITEM = '              <li><a href="#{sid}-{kind}"><span class="module-nav-label">{title}</span><span class="module-nav-desc">{desc}</span></a></li>'
BLOCK = """          <section class="module-block" id="{sid}-{kind}">
            <h3 class="module-block-title">{title}</h3>
            {body}
          </section>"""


def extract_block_body(html: str, sid: str, kind: str) -> str:
    pattern = rf'<section class="module-block" id="{re.escape(sid)}-{kind}">\s*<h3[^>]*>.*?</h3>\s*(.*?)\s*</section>'
    matches = re.findall(pattern, html, re.S)
    if not matches:
        return ""
    if kind == "ops":
        for body in reversed(matches):
            if "operation-step" in body or "operation-substep" in body:
                return body.strip()
    return matches[-1].strip()


def extract_card_header(html: str, sid: str) -> str:
    m = re.search(
        rf'(<section class="section-card" id="{re.escape(sid)}"[^>]*>\s*'
        rf'<p class="section-label">.*?</p>\s*'
        rf"<h2>.*?</h2>\s*)",
        html,
        re.S,
    )
    return m.group(1) if m else ""


def build_card(sid: str, html: str) -> str:
    header = extract_card_header(html, sid)
    if not header:
        return ""
    meta = MODULE.get(sid, {})
    ops = extract_block_body(html, sid, "ops") or "<p>—</p>"
    nav_items = "\n".join(NAV_ITEM.format(sid=sid, kind=k, title=t, desc=d) for k, t, d in SECTIONS)
    nav = f"""          <nav class="module-nav" aria-label="本章の構成">
            <ul class="module-nav-list">
{nav_items}
            </ul>
          </nav>"""
    blocks = []
    for kind, title, _desc in SECTIONS:
        body = ops if kind == "ops" else meta.get(kind, extract_block_body(html, sid, kind) or "<p>—</p>")
        blocks.append(BLOCK.format(sid=sid, kind=kind, title=title, body=body))
    return header + nav + "\n" + "\n".join(blocks) + "\n        </section>"


def remove_orphans(html: str) -> str:
    for sid in MODULE_IDS:
        html = re.sub(
            rf"(</section>\s*)(<section class=\"module-block\" id=\"{re.escape(sid)}-(?:func|scene|ops|effect|impact|perm)\">.*?</section>\s*)+(?=<section class=\"section-card\")",
            r"\1",
            html,
            flags=re.S,
        )
    html = re.sub(r"\s*</section>\s*</section>\s*(?=<section class=\"section-card\")", "\n        </section>\n\n        ", html)
    return html


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    html = remove_orphans(html)
    for sid in MODULE_IDS:
        card = build_card(sid, html)
        if not card:
            continue
        html = re.sub(
            rf'<section class="section-card" id="{re.escape(sid)}"[^>]*>.*?(?=<section class="section-card" id=|</section>\s*</section>\s*<section class="chapter-page"|</section>\s*<section class="chapter-page"|\Z)',
            card + "\n\n        ",
            html,
            count=1,
            flags=re.S,
        )
    html = html.replace(
        "各モジュール上部の<strong>目次</strong>から権限・機能・利用シーン・操作・効果・影響へ移動できます。",
        "各モジュール上部の<strong>構成ナビ</strong>から、ロール・画面操作・利用タイミング・効果・連動へ移動できます。",
    )
    html = html.replace(
        "各モジュール上部の<strong>本章目次</strong>から権限・機能・利用シーン・操作・効果・影響へ移動できます。",
        "各モジュール上部の<strong>構成ナビ</strong>から、ロール・画面操作・利用タイミング・効果・連動へ移動できます。",
    )
    INDEX.write_text(html, encoding="utf-8")
    print("module v2 applied (fixed)")


if __name__ == "__main__":
    main()
