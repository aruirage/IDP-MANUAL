#!/usr/bin/env python3
"""Add module-index nav and module-block sections; simplify layout."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "manual/index.html"

MODULE_META: dict[str, dict[str, str]] = {
    "admin-model-config": {
        "perm": '<span class="ui-text">admin</span>（<a class="jump-link" href="#overview-roles">ロール設定</a>）。<span class="ui-text">業務ルール設定</span> → <span class="ui-text">モデル設定</span>。',
        "effect": '<span class="ui-text">接続テスト</span> 成功後、<span class="ui-text">用途割当</span> 済みモデルが OCR・AI 検証などで呼び出されます。',
    },
    "admin-api-config": {
        "perm": '<span class="ui-text">admin</span>（<a class="jump-link" href="#overview-roles">ロール設定</a>）。',
        "func": "外部連携の <strong>Open API 入口と API Key</strong>。",
        "scene": "基幹・ポータルから自動アップロード／ステータス取得を始める前。",
        "impact": "API 経由アップロード後の処理は公開済み <span class="ui-text">業務シーン設定</span> に従います。",
        "effect": "外部システムから案件投入が可能になります。",
    },
    "admin-master-data-config": {
        "perm": '<span class="ui-text">admin</span>（<a class="jump-link" href="#overview-roles">ロール設定</a>）。',
        "effect": "OCR 値をマスター正規値へ書き戻し、表記ゆれを吸収します。",
    },
    "admin-doctype-config": {
        "perm": '<span class="ui-text">admin</span>（<a class="jump-link" href="#overview-roles">ロール設定</a>）。',
        "effect": "公開後、分類・OCR・前処理・後処理ルールが案件処理に適用されます。",
    },
    "admin-scene-config": {
        "perm": '<span class="ui-text">admin</span>（<a class="jump-link" href="#overview-roles">ロール設定</a>）。',
        "effect": "<span class="ui-text">公開</span> 後、操作員の <span class="ui-text">新規アップロード</span> にシーンが表示され、ワークフローが実行されます。",
    },
    "admin-data-mapping-config": {
        "perm": '<span class="ui-text">admin</span>（<a class="jump-link" href="#overview-roles">ロール設定</a>）。',
        "effect": "複数帳票の OCR 値が同一標準変数に集約され、横断検証の前提になります。",
    },
    "admin-ai-verification-config": {
        "perm": '<span class="ui-text">admin</span>（<a class="jump-link" href="#overview-roles">ロール設定</a>）。',
        "effect": "ルール命中時に <span class="code-text">verifyResult</span> が出力され、人工確認タスクや通知が発生します。",
    },
    "operator-upload-module": {
        "perm": '<span class="ui-text">操作員</span>（<a class="jump-link" href="#overview-roles">ロール設定</a>）。',
        "func": "公開済み <span class="ui-text">業務シーン</span> への資料投入と分類・案件集約の起動。",
        "scene": "新規案件の受付、または補件（案件一覧側）の前段。",
        "impact": "<span class="ui-text">案件一覧</span>・<span class="ui-text">マイタスク</span> の処理対象案件が生成されます。",
        "effect": "ファイルが分類され、案件集約ルールに従って案件 ID が付与されます。",
    },
    "operator-case-module": {
        "perm": '<span class="ui-text">操作員</span>、操作管理者（<a class="jump-link" href="#overview-roles">ロール設定</a>）。',
        "func": "集約済み案件・未集約ファイルの確認、詳細、割当、処理中止。",
        "scene": "アップロード後の進捗確認、例外対応、担当者変更。",
        "impact": "案件ステータス・担当者変更が <span class="ui-text">マイタスク</span> と通知に連動します。",
        "effect": "案件単位で処理経路とファイル OCR 進捗を把握できます。",
    },
    "operator-task-module": {
        "perm": '<span class="ui-text">操作員</span>、操作管理者（<a class="jump-link" href="#overview-roles">ロール設定</a>）。',
        "func": "OCR 人工確認、AI 検証確認、エクスポート。",
        "scene": "ワークフロー上 <span class="code-text">reviewRequired</span> 等でタスクが割り当てられたとき。",
        "impact": "確認結果が案件ステータスと出力データに反映されます。",
        "effect": "要確認項目を修正・承認し、案件を次工程または出力へ進めます。",
    },
    "system-user-management": {
        "perm": '<span class="ui-text">admin</span>（<span class="ui-text">システム設定</span>）。',
        "func": "ログインユーザーの作成・無効化・パスワードリセット。",
        "scene": "新メンバー追加、退職者アカウント停止時。",
        "impact": "ユーザー数上限・メニュー権限（権限管理）と連動します。",
        "effect": "有効ユーザーだけが NeosAI にログインできます。",
    },
    "system-role-management": {
        "perm": '<span class="ui-text">admin</span>（<span class="ui-text">システム設定</span>）。',
        "func": "権限テンプレートとメニュー権限の付与。",
        "scene": "admin / 操作員などロール別に見えるメニューを分けたいとき。",
        "impact": "<span class="ui-text">業務ルール設定</span> 各画面への到達可否を決めます。",
        "effect": "ロールごとに操作可能なモジュールが変わります。",
    },
    "system-security-settings": {
        "perm": '<span class="ui-text">admin</span>（<span class="ui-text">システム設定</span>）。',
        "func": "読取データ保存期限とアイドル自動ログアウト。",
        "scene": "セキュリティポリシー策定・監査対応時。",
        "impact": "期限超過データは復元不可。全ユーザーのセッションに適用。",
        "effect": "データ保持期間と無操作ログアウトがシステム全体で enforced されます。",
    },
}

INDEX_NAV = """          <nav class="module-index" aria-label="本章の目次">
            <a href="#{sid}-perm">権限</a>
            <a href="#{sid}-func">機能</a>
            <a href="#{sid}-scene">利用シーン</a>
            <a href="#{sid}-ops">操作</a>
            <a href="#{sid}-effect">効果</a>
            <a href="#{sid}-impact">影響</a>
          </nav>"""

BLOCK = """          <section class="module-block" id="{sid}-{kind}">
            <h3 class="module-block-title">{title}</h3>
            {body}
          </section>"""


def parse_config_guide(body: str) -> tuple[str, str, str, str]:
    func = scene = impact = ""
    match = re.search(r'<div class="config-guide">.*?</div>\s*', body, re.S)
    if not match:
        return body, func, scene, impact
    block = match.group(0)
    body = body.replace(block, "", 1)
    for key, target in (
        ("何を決めるか", "func"),
        ("いつ必要か", "scene"),
        ("影響範囲", "impact"),
    ):
        li = re.search(rf"<strong>{key}</strong>\s*—\s*(.*?)</li>", block, re.S)
        if li:
            if target == "func":
                func = li.group(1).strip()
            elif target == "scene":
                scene = li.group(1).strip()
            else:
                impact = li.group(1).strip()
    return body, func, scene, impact


def clean_body(body: str) -> str:
    body = re.sub(r'<div class="step-context">.*?</div>\s*', "", body, flags=re.S)
    body = re.sub(r"<h3>操作手順</h3>\s*", "", body)
    body = re.sub(r'<p class="shot-map-caption">.*?</p>\s*', "", body, flags=re.S)
    body = re.sub(
        r'<div class="notice (?:info|warning)">\s*<strong>適用ルール</strong>\s*(.*?)</div>\s*',
        r'<p class="module-note">\1</p>',
        body,
        flags=re.S,
    )
    return body.strip()


def split_tail_notes(body: str) -> tuple[str, str]:
    notes = re.findall(r'<p class="module-note">.*?</p>\s*', body, re.S)
    if not notes:
        return body, ""
    tail = "".join(notes)
    for note in notes:
        body = body.replace(note, "", 1)
    return body.strip(), tail


def transform_card(section_id: str, card_html: str) -> str:
    header = re.match(
        r"(?s)(<section class=\"section-card\" id=\"[^\"]+\">\s*"
        r"<p class=\"section-label\">.*?</p>\s*"
        r"<h2>.*?</h2>\s*)",
        card_html,
    )
    if not header:
        return card_html
    body = card_html[len(header.group(1)) :].removesuffix("</section>").strip()
    body, func, scene, impact = parse_config_guide(body)
    intro = re.search(r'<p class="intro-summary">(.*?)</p>\s*', body, re.S)
    if intro:
        if not func:
            func = intro.group(1).strip()
        body = body.replace(intro.group(0), "", 1)
    body = clean_body(body)
    body, tail_notes = split_tail_notes(body)

    meta = MODULE_META.get(section_id, {})
    perm = meta.get("perm", '<a class="jump-link" href="#overview-roles">ロール設定</a> を参照。')
    func = meta.get("func", func) or "—"
    scene = meta.get("scene", scene) or "—"
    impact = meta.get("impact", impact) or "—"
    effect = meta.get("effect", "設定内容が公開・有効化された時点以降の案件処理に反映されます。")

    impact_body = f"<p>{impact}</p>{tail_notes}"

    blocks = [
        BLOCK.format(sid=section_id, kind="perm", title="権限", body=f"<p>{perm}</p>"),
        BLOCK.format(sid=section_id, kind="func", title="機能", body=f"<p>{func}</p>"),
        BLOCK.format(sid=section_id, kind="scene", title="利用シーン", body=f"<p>{scene}</p>"),
        BLOCK.format(sid=section_id, kind="ops", title="操作", body=body),
        BLOCK.format(sid=section_id, kind="effect", title="効果", body=f"<p>{effect}</p>"),
        BLOCK.format(
            sid=section_id,
            kind="impact",
            title="影響",
            body=impact_body,
        ),
    ]

    return header.group(1) + INDEX_NAV.format(sid=section_id) + "\n" + "\n".join(blocks) + "\n        </section>"


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    pattern = re.compile(
        r'<section class="section-card" id="(admin-|operator-|system-)[^"]+">.*?</section>',
        re.S,
    )

    def repl(match: re.Match[str]) -> str:
        sid = match.group(1)
        # recover full id from match
        full_id = re.search(r'id="([^"]+)"', match.group(0)).group(1)
        return transform_card(full_id, match.group(0))

    html = pattern.sub(lambda m: transform_card(re.search(r'id="([^"]+)"', m.group(0)).group(1), m.group(0)), html)

    intro = re.search(
        r'(<p class="intro-summary">admin の設定順序：.*?)</p>',
        html,
        re.S,
    )
    if intro:
        html = html.replace(
            intro.group(0),
            intro.group(1)
            + "。各モジュール上部の<strong>本章目次</strong>から権限・機能・利用シーン・操作・効果・影響へ移動できます。</p>",
            1,
        )

    INDEX.write_text(html, encoding="utf-8")
    print("module-index applied")


if __name__ == "__main__":
    main()
