#!/usr/bin/env python3
"""Inject module-role, module-guide, and TOC sub-links into manual/index.html."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

MODULES = [
    {
        "id": "admin-model-config",
        "toc_label": "モデル設定",
        "role": '<span class="ui-text">admin</span> が利用します。<span class="ui-text">システム設定</span> → <span class="ui-text">権限管理</span> で <span class="ui-text">業務ルール設定</span> メニューが付与されたユーザーのみアクセスできます。詳細は <a class="jump-link" href="#overview-roles">ロール設定</a> を参照してください。',
        "scenario": "環境構築時、モデル接続の追加・変更時、OCR／AI検証など各用途のモデル割当を見直すときに設定します。帳票タイプや業務シーンを公開する前段階で整備します。",
        "effect": "API 接続の登録・接続テスト・用途別割当により、OCR 抽出、AI 検証、データマッピング、Master 照合などが参照するモデル接続を一元管理します。",
        "impact": "有効化後の接続は <span class="ui-text">帳票タイプ設定</span> の読取モデル候補に反映されます。設定変更は新規に開始するモデル呼び出しから適用され、進行中案件・投入済み非同期タスクには開始時点の設定が維持されます。",
    },
    {
        "id": "admin-api-config",
        "toc_label": "API設定",
        "role": '<span class="ui-text">admin</span> が利用します。外部連携の入口設定のため、<span class="ui-text">業務ルール設定</span> メニュー権限が必要です。',
        "scenario": "外部システムから資料アップロード・案件状態取得・補足資料追加・出力取得を行う連携を構築・更新するときに設定します。",
        "effect": "Open API のエンドポイント、API Key、通知 URL を管理し、外部から保険金請求資料の入出力連携を可能にします。",
        "impact": "API 経由のアップロード後に実行される分類・OCR・マッピング・AI 検証・通知・出力は、公開済み <span class="ui-text">業務シーン設定</span> に従います。接続仕様の詳細は API 文書を参照してください。",
    },
    {
        "id": "admin-master-data-config",
        "toc_label": "マスターデータ設定",
        "role": '<span class="ui-text">admin</span> が利用します。<span class="ui-text">業務ルール設定</span> → <span class="ui-text">マスターデータ設定</span> へのアクセス権が必要です。',
        "scenario": "表記ゆれの正規化、金融機関・医薬品などの参照表を整備するとき、または帳票タイプで <span class="ui-text">マスタ照合</span> を使う前に登録します。",
        "effect": "マスター表・列設定・照会コード・データ行を管理し、ベクトル化完了後に OCR 値の照合・正規値書き戻しの参照元となります。",
        "impact": "<span class="ui-text">帳票タイプ設定</span> の <span class="ui-text">マスタ照合</span> が参照する表・列を決定します。ベクトル化未完了・失敗行があると照合に利用できません。",
    },
    {
        "id": "admin-doctype-config",
        "toc_label": "帳票タイプ設定",
        "role": '<span class="ui-text">admin</span> が利用します。帳票ルール定義の中核機能のため、業務ルール設定権限が必要です。',
        "scenario": "新帳票タイプの追加、読取項目・処理ルール・画像処理の調整、効果テストと公開前の見直し時に設定します。",
        "effect": "帳票ごとに AI 分類、OCR 読取、処理ルール（マスタ照合等）、画像処理、効果テストを 5 ステップで定義し、読取精度と後処理を制御します。",
        "impact": "業務シーンの OCR ノード、操作員の OCR 人工確認、Master 照合 UI、AI 検証のフィールド参照に波及します。<span class="ui-text">モデル設定</span>・<span class="ui-text">マスターデータ設定</span> の整備状況に依存します。",
    },
    {
        "id": "admin-scene-config",
        "toc_label": "業務シーン設定",
        "role": '<span class="ui-text">admin</span> が利用します。案件フロー全体を束ねるため、業務ルール設定の全サブメニュー利用権が前提です。',
        "scenario": "マスター・帳票タイプ・マッピング・AI 検証を組み合わせた実行フローを新規作成・改訂・公開するときに設定します。操作員向けシーン公開前の最終段階です。",
        "effect": "案件集約、ワークフロー、通知、出力項目を 4 ステップで構成し、<span class="ui-text">保険金請求</span> などの業務を操作員が利用できる公開バージョンとして確定します。",
        "impact": "<span class="ui-text">新規アップロード</span> のシーン候補、<span class="ui-text">案件一覧</span> の集約ルール、<span class="ui-text">マイタスク</span> のタスク生成・エクスポート項目、API 連携後の処理経路すべてに影響します。",
        "inject_before": "保険金請求ケース構成",
    },
    {
        "id": "admin-data-mapping-config",
        "toc_label": "データマッピング設定",
        "role": '<span class="ui-text">admin</span> が利用します。<span class="ui-text">業務ルール設定</span> → <span class="ui-text">データマッピング設定</span> へのアクセス権が必要です。',
        "scenario": "複数帳票にまたがる同一意味項目（被保険者名、請求金額等）を案件標準変数に統一するとき、ワークフローにマッピングノードを置く前に設定します。",
        "effect": "OCR 項目を標準変数へマッピングし、案件単位の構造化データと AI 検証の整合性判定の基盤を作ります。",
        "impact": "業務シーン <span class="ui-text">ワークフロー設定</span> の <span class="ui-text">データマッピング</span> ノード、<span class="ui-text">AI検証設定</span> の標準データ整合性、エクスポートの <span class="ui-text">標準フィールド</span> に連動します。",
    },
    {
        "id": "admin-ai-verification-config",
        "toc_label": "AI検証設定",
        "role": '<span class="ui-text">admin</span> が利用します。検証ルール定義のため、業務ルール設定権限が必要です。',
        "scenario": "必須項目・必要書類・帳票間整合・テキスト／数値ルール・署名印鑑検証を追加・変更するとき、業務シーン公開前に設定します。",
        "effect": "6 種類の AI 検証ルールをシーン・帳票単位で管理し、ワークフロー AI 検証ノード実行時の判定基準を定義します。",
        "impact": "要確認時は <span class="ui-text">マイタスク</span> の AI 検証確認タスクが生成されます。<span class="ui-text">データマッピング設定</span>・<span class="ui-text">業務シーン設定</span> ワークフローとセットで機能します。",
    },
    {
        "id": "operator-upload-module",
        "toc_label": "新規アップロード",
        "role": '<span class="ui-text">操作員</span> が主に利用します。公開済み業務シーンへ資料を投入する権限が必要です。<span class="ui-text">操作管理者</span> も同様に利用できます。admin は設定確認目的で参照可能です。',
        "scenario": "新規案件の資料を初回投入するとき、または <span class="ui-text">案件一覧</span> から <span class="ui-text">補件</span> 案件へ追加書類をアップロードするときに利用します。",
        "effect": "業務シーンを選びファイルを追加し、分類・案件集約を実行して後続ワークフローを起動します。",
        "impact": "処理結果は <span class="ui-text">案件一覧</span>（集約済み／未集約）と <span class="ui-text">マイタスク</span> に反映されます。利用可能シーンは admin の業務シーン公開内容に限定されます。",
    },
    {
        "id": "operator-case-module",
        "toc_label": "案件一覧",
        "role": '<span class="ui-text">操作員</span>・<span class="ui-text">操作管理者</span> が利用します。案件の閲覧・割当・補正には業務操作メニュー権限が必要です。',
        "scenario": "案件進捗の確認、ファイル詳細・ワークフロー経路の照会、担当者割当、誤集約ファイルの手動校正、処理中止が必要なときに利用します。",
        "effect": "集約済み案件と未集約ファイルを一覧・展開・詳細表示し、案件／ファイル単位の操作とワークフロー可視化を提供します。",
        "impact": "担当者変更は <span class="ui-text">マイタスク</span> の割当先に影響します。手動校正・案件変更は集約結果と後続 OCR／検証対象を変えます。",
    },
    {
        "id": "operator-task-module",
        "toc_label": "マイタスク",
        "role": '<span class="ui-text">操作員</span> が割当タスクを処理します。<span class="ui-text">操作管理者</span> はタスク割当の変更も可能です。各タスク種別はワークフロー上の権限・通知設定に従います。',
        "scenario": "OCR 要確認、AI 検証要確認、ワークフロー完了後のエクスポートなど、ワークフローから起票されたタスクに対応するときに利用します。",
        "effect": "OCR 抽出確認・AI 検証確認で人工修正と完了／補件／中止を確定し、エクスポートで構造化結果を出力します。",
        "impact": "タスク完了はワークフロー後続ノードと案件ステータスを進めます。エクスポート内容は <span class="ui-text">業務シーン設定</span> Step4 と <span class="ui-text">データマッピング設定</span> に依存します。",
    },
    {
        "id": "system-user-management",
        "toc_label": "ユーザー管理",
        "role": '<span class="ui-text">admin</span> が利用します。<span class="ui-text">システム設定</span> → <span class="ui-text">ユーザー管理</span> メニュー権限が必要です。',
        "scenario": "新規ユーザーの招待、権限テンプレートの割当、退職・休止ユーザーの無効化、パスワードリセットが必要なときに設定します。",
        "effect": "ログイン可能なユーザーと有効ユーザー数上限を管理し、各ユーザーに権限テンプレートを紐付けます。",
        "impact": "ユーザーがアクセスできる業務ルール設定・業務操作・システム設定メニューは、割当権限テンプレート（<a class="jump-link" href="#system-role-management">権限管理</a>）で決まります。",
    },
    {
        "id": "system-role-management",
        "toc_label": "権限管理",
        "role": '<span class="ui-text">admin</span> が利用します。<span class="ui-text">システム設定</span> → <span class="ui-text">権限管理</span> メニュー権限が必要です。',
        "scenario": "admin／操作員／操作管理者などロール別のメニュー到達範囲を定義・変更するとき、または新機能モジュール追加後に権限テンプレートを更新するときに設定します。",
        "effect": "権限テンプレートと <span class="ui-text">メニュー権限</span> により、各ロールが利用できる機能モジュールを制御します。",
        "impact": "本マニュアル各章の「権限・ロール」で示す利用可否は、ここで付与されたメニューに依存します。<a class="jump-link" href="#overview-roles">ロール設定</a> の役割分担と合わせて設計してください。",
    },
    {
        "id": "system-security-settings",
        "toc_label": "セキュリティ設定",
        "role": '<span class="ui-text">admin</span> が利用します。<span class="ui-text">システム設定</span> → <span class="ui-text">セキュリティ設定</span> メニュー権限が必要です。',
        "scenario": "読取データの保存期限や、操作端末のアイドル自動ログアウト方針を組織ポリシーに合わせて設定・見直すときに利用します。",
        "effect": "データ保存期限とアイドルセッション（自動ログアウト）を設定し、保存データのライフサイクルとセッション管理を制御します。",
        "impact": "保存期限超過後の読取データは復元できません。全ユーザーのセッション挙動に影響するため、業務時間帯を考慮して変更してください。",
    },
]

ADMIN_IDS = [m["id"] for m in MODULES if m["id"].startswith("admin-")]
OPERATOR_IDS = [m["id"] for m in MODULES if m["id"].startswith("operator-")]
SYSTEM_IDS = [m["id"] for m in MODULES if m["id"].startswith("system-")]


def module_block(m: dict) -> str:
    mid = m["id"]
    return f"""          <div class="module-role" id="{mid}-role">
            <h3 class="module-meta-heading">権限・ロール</h3>
            <p>{m["role"]}</p>
          </div>
          <div class="module-guide" id="{mid}-guide">
            <div class="module-guide-item" id="{mid}-scenario">
              <h4>適用タイミング</h4>
              <p>{m["scenario"]}</p>
            </div>
            <div class="module-guide-item" id="{mid}-effect">
              <h4>実現効果</h4>
              <p>{m["effect"]}</p>
            </div>
            <div class="module-guide-item" id="{mid}-impact">
              <h4>関連影響</h4>
              <p>{m["impact"]}</p>
            </div>
          </div>
"""


def toc_block(modules: list[dict]) -> str:
    lines = []
    for m in modules:
        mid = m["id"]
        label = m["toc_label"]
        lines.append(f'          <div class="toc-module-block">')
        lines.append(f'            <a class="toc-child" href="#{mid}">{label}</a>')
        lines.append(f'            <a class="toc-sub" href="#{mid}-role">権限</a>')
        lines.append(f'            <a class="toc-sub" href="#{mid}-scenario">適用タイミング</a>')
        lines.append(f'            <a class="toc-sub" href="#{mid}-effect">実現効果</a>')
        lines.append(f'            <a class="toc-sub" href="#{mid}-impact">関連影響</a>')
        lines.append(f'            <a class="toc-sub" href="#{mid}-ops">操作手順</a>')
        lines.append(f"          </div>")
    return "\n".join(lines)


def chapter_role_note(chapter: str, body: str) -> str:
    return f"""          <div class="notice info chapter-role-note">
            <strong>権限・ロール（{chapter}）</strong>
            {body}
          </div>
"""


def patch_sections(html: str) -> str:
    for m in MODULES:
        mid = m["id"]
        block = module_block(m)

        section_pat = rf'(<section class="section-card" id="{re.escape(mid)}">.*?<h2>[^<]+</h2>\s*)'
        if m.get("inject_before"):
            anchor = f'<h3>{m["inject_before"]}</h3>'
            html = re.sub(
                section_pat + re.escape(anchor),
                r"\1" + block + anchor,
                html,
                count=1,
                flags=re.DOTALL,
            )
        else:
            # Insert after h2 and optional intro paragraph, before 操作ポイント
            html = re.sub(
                section_pat + r'(?:<p>.*?</p>\s*)?<h3>操作ポイント</h3>',
                r"\1" + block + r'<h3 class="module-ops-heading" id="' + mid + r'-ops">操作手順</h3>',
                html,
                count=1,
                flags=re.DOTALL,
            )

        # Scene config also has 操作ポイント later
        html = html.replace(
            f'<h3>操作ポイント</h3>',
            f'<h3 class="module-ops-heading" id="{mid}-ops">操作手順</h3>',
            1,
        )

    return html


def patch_toc(html: str) -> str:
    admin_toc = toc_block([m for m in MODULES if m["id"] in ADMIN_IDS])
    operator_toc = toc_block([m for m in MODULES if m["id"] in OPERATOR_IDS])
    system_toc = toc_block([m for m in MODULES if m["id"] in SYSTEM_IDS])

    html = re.sub(
        r'(<a class="toc-parent" href="#admin-guide">ルール設定モジュール</a>\s*).*?(</div>\s*<div class="toc-group">\s*<a class="toc-parent" href="#operator-guide">)',
        r"\1\n" + admin_toc + r"\n        \2",
        html,
        count=1,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'(<a class="toc-parent" href="#operator-guide">業務操作モジュール</a>\s*).*?(</div>\s*<div class="toc-group">\s*<a class="toc-parent" href="#system-settings">)',
        r"\1\n" + operator_toc + r"\n        \2",
        html,
        count=1,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'(<a class="toc-parent" href="#system-settings">システム設定モジュール</a>\s*).*?(</div>\s*</nav>)',
        r"\1\n" + system_toc + r"\n        \2",
        html,
        count=1,
        flags=re.DOTALL,
    )
    return html


def patch_chapter_intros(html: str) -> str:
    html = html.replace(
        "本章では各機能モジュール、操作ポイント、画面だけでは分かりにくいルール適用タイミングを説明します。",
        "本章では各機能モジュールを「権限・ロール」「適用タイミング」「実現効果」「関連影響」「操作手順」に分けて説明します。左の目次から各ブロックへ直接移動できます。",
    )
    admin_note = chapter_role_note(
        "ルール設定モジュール",
        '本章の機能は <span class="ui-text">admin</span> が利用します。<span class="ui-text">システム設定</span> → <span class="ui-text">権限管理</span> で <span class="ui-text">業務ルール設定</span> 配下メニューが付与されたユーザーのみアクセスできます。操作員向け機能は <a class="jump-link" href="#operator-guide">業務操作モジュール</a>、ロール詳細は <a class="jump-link" href="#overview-roles">ロール設定</a> を参照してください。',
    )
    html = re.sub(
        r'(<section class="chapter-page" id="admin-guide">.*?<p class="intro-summary">.*?</p>\s*)',
        r"\1" + admin_note,
        html,
        count=1,
        flags=re.DOTALL,
    )
    operator_note = chapter_role_note(
        "業務操作モジュール",
        '本章は <span class="ui-text">操作員</span>・<span class="ui-text">操作管理者</span> が主に利用します。公開済み業務シーンが前提です。ルール変更は <a class="jump-link" href="#admin-guide">ルール設定モジュール</a> で行います。',
    )
    html = re.sub(
        r'(<section class="chapter-page" id="operator-guide">.*?<p class="intro-summary">.*?</p>\s*)',
        r"\1" + operator_note,
        html,
        count=1,
        flags=re.DOTALL,
    )
    system_note = chapter_role_note(
        "システム設定モジュール",
        '本章は <span class="ui-text">admin</span> が利用します。ユーザー・権限・セキュリティの設定は、業務ルールそのものではなく「誰がどの機能にアクセスできるか」を決めます。',
    )
    html = re.sub(
        r'(<section class="chapter-page" id="system-settings">.*?<p class="intro-summary">.*?</p>\s*)',
        r"\1" + system_note,
        html,
        count=1,
        flags=re.DOTALL,
    )
    return html


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    if "module-guide" in html:
        print("module-guide already present; skipping")
        return
    html = patch_chapter_intros(html)
    html = patch_sections(html)
    html = patch_toc(html)
    INDEX.write_text(html, encoding="utf-8")
    print(f"Updated {INDEX}")


if __name__ == "__main__":
    main()
