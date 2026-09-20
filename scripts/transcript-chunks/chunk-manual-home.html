#!/usr/bin/env python3
"""Simplify manual module structure: flat TOC, remove module-role/guide blocks."""

from __future__ import annotations

import re
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"

ADMIN_MODULES = [
    ("admin-model-config", "モデル設定"),
    ("admin-api-config", "API設定"),
    ("admin-master-data-config", "マスターデータ設定"),
    ("admin-doctype-config", "帳票タイプ設定"),
    ("admin-scene-config", "業務シーン設定"),
    ("admin-data-mapping-config", "データマッピング設定"),
    ("admin-ai-verification-config", "AI検証設定"),
]
OPERATOR_MODULES = [
    ("operator-upload-module", "新規アップロード"),
    ("operator-case-module", "案件一覧"),
    ("operator-task-module", "マイタスク"),
]
SYSTEM_MODULES = [
    ("system-user-management", "ユーザー管理"),
    ("system-role-management", "権限管理"),
    ("system-security-settings", "セキュリティ設定"),
]


def toc_lines(modules: list[tuple[str, str]]) -> str:
    return "\n".join(f'          <a class="toc-child" href="#{mid}">{label}</a>' for mid, label in modules)


def replace_toc(html: str) -> str:
    nav_start = html.index('<aside class="toc-panel"')
    nav_end = html.index("</aside>", nav_start) + len("</aside>")
    nav = html[nav_start:nav_end]

    new_nav = f"""    <aside class="toc-panel" aria-label="目次">
      <div class="toc-title">目次</div>
      <nav>
        <div class="toc-group">
          <a class="toc-parent" href="#manual-home">総覧</a>
          <a class="toc-child" href="#overview-system">システム概要</a>
          <a class="toc-child" href="#overview-case">ケース例</a>
          <a class="toc-child" href="#overview-roles">ロール設定</a>
          <a class="toc-child" href="#overview-modules">機能モジュール</a>
    </div>
        <div class="toc-group">
          <a class="toc-parent" href="#admin-guide">ルール設定モジュール</a>
{toc_lines(ADMIN_MODULES)}
    </div>
        <div class="toc-group">
          <a class="toc-parent" href="#operator-guide">業務操作モジュール</a>
{toc_lines(OPERATOR_MODULES)}
    </div>
        <div class="toc-group">
          <a class="toc-parent" href="#admin-guide">ルール設定モジュール</a>
"""
    # fix typo - system should not duplicate admin
    new_nav = f"""    <aside class="toc-panel" aria-label="目次">
      <div class="toc-title">目次</div>
      <nav>
        <div class="toc-group">
          <a class="toc-parent" href="#manual-home">総覧</a>
          <a class="toc-child" href="#overview-system">システム概要</a>
          <a class="toc-child" href="#overview-case">ケース例</a>
          <a class="toc-child" href="#overview-roles">ロール設定</a>
          <a class="toc-child" href="#overview-modules">機能モジュール</a>
    </div>
        <div class="toc-group">
          <a class="toc-parent" href="#admin-guide">ルール設定モジュール</a>
{toc_lines(ADMIN_MODULES)}
    </div>
        <div class="toc-group">
          <a class="toc-parent" href="#operator-guide">業務操作モジュール</a>
{toc_lines(OPERATOR_MODULES)}
    </div>
        <div class="toc-group">
          <a class="toc-parent" href="#system-settings">システム設定モジュール</a>
{toc_lines(SYSTEM_MODULES)}
    </div>
      </nav>
    </aside>"""

    return html[:nav_start] + new_nav + html[nav_end:]


def strip_module_blocks(html: str) -> str:
    html = re.sub(
        r'\s*<div class="module-role" id="[^"]+-role">.*?</div>\s*',
        "\n",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'\s*<div class="module-guide" id="[^"]+-guide">.*?</div>\s*',
        "\n",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'\s*<div class="notice (?:info|warning) chapter-role-note">.*?</div>\s*',
        "\n",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'<h3 class="module-ops-heading" id="[^"]+-ops">操作手順</h3>',
        "<h3>操作手順</h3>",
        html,
    )
    return html


def simplify_chapter_intros(html: str) -> str:
    return html.replace(
        "本章では各機能モジュールを「権限・ロール」「適用タイミング」「実現効果」「関連影響」「操作手順」に分けて説明します。左の目次から各ブロックへ直接移動できます。",
        "各機能モジュールの操作手順と、画面だけでは分かりにくい適用タイミングを説明します。ロール詳細は <a class=\"jump-link\" href=\"#overview-roles\">ロール設定</a> を参照してください。",
    )


def simplify_master_data(html: str) -> str:
    html = re.sub(
        r'\s*<div class="notice warning" id="admin-master-data-vectorization">.*?</div>\s*',
        "\n",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'\n          <div class="operation-step">\s*'
        r'<p><span class="step-code">4</span><span class="step-text"><span class="ui-text">ベクトル化状態</span>.*?</div>\s*(?=</section>)',
        "\n",
        html,
        count=1,
        flags=re.DOTALL,
    )
    old = (
        '<p><span class="step-text">登録完了後は、必ず Step 4 で <span class="ui-text">ベクトル化状態</span> を確認してください。'
        'インポート直後は <span class="ui-text">待機中</span> または <span class="ui-text">処理中</span> となることがあります。</span></p>'
    )
    notice = """            <div class="notice info">
              <strong>ベクトル化状態</strong>
              登録・<span class="ui-text">一括インポート</span> 後は一覧の <span class="ui-text">ベクトル化状態</span> を確認してください。<span class="ui-text">完了</span> になって初めて <span class="ui-text">マスタ照合</span> で利用できます。1 万行以上は <strong>30 分以上</strong> かかる場合があります。<span class="ui-text">失敗</span> 行は <span class="ui-text">再実行</span> または <span class="ui-text">ベクトル化再実行</span> で手動リトライしてください。
            </div>
"""
    return html.replace(old, notice)


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    html = replace_toc(html)
    html = simplify_chapter_intros(html)
    html = strip_module_blocks(html)
    html = simplify_master_data(html)
    INDEX.write_text(html, encoding="utf-8")
    print(f"Simplified {INDEX}")


if __name__ == "__main__":
    main()
