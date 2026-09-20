#!/usr/bin/env python3
"""Restore manual/index.html to ~12:30 state (before module-nav at 12:32)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANUAL = ROOT / "manual"
INDEX = MANUAL / "index.html"
CSS = MANUAL / "common.css"
CHUNKS = MANUAL / "scripts/transcript-chunks"
PATCHES = MANUAL / "scripts/noon-patches"
TRANSCRIPT = (
    Path.home()
    / ".cursor/projects/Users-mac-Desktop-AIPM-Projects-NeosAI-prototypes-kisoku-nintei/agent-transcripts"
    / "ef8cc5b6-3ff4-454d-9ed0-d2e5f6fd899d/ef8cc5b6-3ff4-454d-9ed0-d2e5f6fd899d.jsonl"
)

LIGHTBOX_SCRIPT = """
<script>
(function () {
  const lightbox = document.getElementById('manualLightbox');
  const img = document.getElementById('lightboxImage');
  const caption = document.getElementById('lightboxCaption');
  const links = Array.from(document.querySelectorAll('[data-lightbox="manual-shots"]'));
  let index = 0;
  let scale = 1;

  function applyScale() {
    img.style.transform = 'scale(' + scale + ')';
  }

  function show(i) {
    index = (i + links.length) % links.length;
    const link = links[index];
    img.src = link.getAttribute('href');
    caption.textContent = link.getAttribute('aria-label') || '';
    scale = 1;
    applyScale();
  }

  function openAt(link) {
    const i = links.indexOf(link);
    if (i === -1) return;
    show(i);
    lightbox.classList.add('is-open');
    document.body.classList.add('lightbox-open');
  }

  function closeBox() {
    lightbox.classList.remove('is-open');
    document.body.classList.remove('lightbox-open');
    img.src = '';
  }

  document.querySelectorAll('.shot-link[data-lightbox="manual-shots"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      openAt(link);
    });
  });

  lightbox.querySelector('.lightbox-close').addEventListener('click', closeBox);
  lightbox.querySelector('[data-lightbox-close]').addEventListener('click', closeBox);
  lightbox.querySelector('.lightbox-prev').addEventListener('click', () => show(index - 1));
  lightbox.querySelector('.lightbox-next').addEventListener('click', () => show(index + 1));
  lightbox.querySelector('.lightbox-zoom-in').addEventListener('click', () => {
    scale = Math.min(scale + 0.25, 3);
    applyScale();
  });
  lightbox.querySelector('.lightbox-zoom-out').addEventListener('click', () => {
    scale = Math.max(scale - 0.25, 0.5);
    applyScale();
  });
  lightbox.querySelector('.lightbox-zoom-reset').addEventListener('click', () => {
    scale = 1;
    applyScale();
  });

  document.addEventListener('keydown', (event) => {
    if (!lightbox.classList.contains('is-open')) return;
    if (event.key === 'Escape') closeBox();
    if (event.key === 'ArrowLeft') show(index - 1);
    if (event.key === 'ArrowRight') show(index + 1);
  });
})();
</script>
"""

LIGHTBOX_HTML = """
<div id="manualLightbox" class="lightbox" aria-hidden="true">
  <div class="lightbox-backdrop" data-lightbox-close></div>
  <div class="lightbox-panel">
    <button type="button" class="lightbox-close" aria-label="閉じる">×</button>
    <button type="button" class="lightbox-nav lightbox-prev" aria-label="前へ">‹</button>
    <figure class="lightbox-figure">
      <img id="lightboxImage" alt="">
      <figcaption id="lightboxCaption"></figcaption>
    </figure>
    <button type="button" class="lightbox-nav lightbox-next" aria-label="次へ">›</button>
    <div class="lightbox-toolbar">
      <button type="button" class="lightbox-zoom-out" aria-label="縮小">−</button>
      <button type="button" class="lightbox-zoom-reset" aria-label="リセット">100%</button>
      <button type="button" class="lightbox-zoom-in" aria-label="拡大">+</button>
    </div>
  </div>
</div>
"""

TOC = """
    <aside class="toc-panel" aria-label="目次">
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
          <a class="toc-child" href="#admin-model-config">モデル設定</a>
          <a class="toc-child" href="#admin-api-config">API設定</a>
          <a class="toc-child" href="#admin-master-data-config">マスターデータ設定</a>
          <a class="toc-child" href="#admin-doctype-config">帳票タイプ設定</a>
          <a class="toc-child" href="#admin-scene-config">業務シーン設定</a>
          <a class="toc-child" href="#admin-data-mapping-config">データマッピング設定</a>
          <a class="toc-child" href="#admin-ai-verification-config">AI検証設定</a>
        </div>
        <div class="toc-group">
          <a class="toc-parent" href="#operator-guide">業務操作モジュール</a>
          <a class="toc-child" href="#operator-upload-module">新規アップロード</a>
          <a class="toc-child" href="#operator-case-module">案件一覧</a>
          <a class="toc-child" href="#operator-task-module">マイタスク</a>
        </div>
        <div class="toc-group">
          <a class="toc-parent" href="#system-settings">システム設定モジュール</a>
          <a class="toc-child" href="#system-user-management">ユーザー管理</a>
          <a class="toc-child" href="#system-role-management">権限管理</a>
          <a class="toc-child" href="#system-security-settings">セキュリティ設定</a>
        </div>
      </nav>
    </aside>
"""

OVERVIEW = """
        <section class="section-card" id="manual-home">
          <h2>はじめに</h2>
          <p>本マニュアルでは、NeosAI IDP の主要機能と基本的な操作手順を説明します。左の目次から章・モジュールへ移動できます。</p>
        </section>

        <section class="section-card" id="overview-system">
          <h2>システム概要</h2>
          <p>NeosAI IDP は、帳票画像を AI で分類・読取し、業務シーンのワークフローに沿って検証・出力まで進めるプラットフォームです。</p>
          <div class="process-flow overview-flow">
            <div class="flow-row primary-flow">
              <div class="flow-node">admin 設定</div>
              <div class="flow-arrow">→</div>
              <div class="flow-node">業務操作</div>
              <div class="flow-arrow">→</div>
              <div class="flow-node">マイタスク</div>
            </div>
            <div class="flow-row config-flow">
              <div class="flow-node">モデル設定</div>
              <div class="flow-node">API設定</div>
              <div class="flow-node">マスターデータ設定</div>
              <div class="flow-node">帳票タイプ設定</div>
              <div class="flow-node">データマッピング設定</div>
              <div class="flow-node">AI検証設定</div>
              <div class="flow-node">業務シーン設定</div>
            </div>
          </div>
        </section>

        <section class="section-card" id="overview-case">
          <h2>ケース例</h2>
          <p>本マニュアルでは <span class="ui-text">保険金請求</span> を通じて、設定から業務操作までを一貫して説明します（<strong>説明用の例です</strong>）。</p>
          <ul>
            <li>admin は請求書、診断書、診療明細書、領収書などの帳票タイプを設定し、業務シーン <span class="ui-text">保険金請求</span> を公開します。</li>
            <li>操作員は同一案件の資料をアップロードし、案件一覧で進捗を確認、<span class="ui-text">マイタスク</span> で人工確認と出力を行います。</li>
          </ul>
        </section>

        <section class="section-card" id="overview-roles">
          <h2>ロール設定</h2>
          <table class="info-table">
            <thead><tr><th>ロール</th><th>主な役割</th></tr></thead>
            <tbody>
              <tr><td><span class="ui-text">admin</span></td><td>モデル・帳票・マスター・マッピング・AI検証・業務シーンの設定と公開</td></tr>
              <tr><td><span class="ui-text">操作員</span></td><td>資料アップロード、担当案件の確認、<span class="ui-text">マイタスク</span> の対応</td></tr>
              <tr><td><span class="ui-text">操作管理者</span></td><td>全案件の閲覧、タスク割当、案件中止など運用管理</td></tr>
              <tr><td><span class="ui-text">担当者</span></td><td><strong>独立したログインロールではなく</strong>、案件またはタスクに付与される属性。通知設定や割当により、<strong>対象案件の案件担当者へ解決</strong>されます。</td></tr>
            </tbody>
          </table>
          <p><span class="ui-text">ワークフロー設定</span> と <span class="ui-text">通知設定</span> で、人工確認や補件イベントの通知先を決めます。<span class="ui-text">マイタスク</span> はすべての人工確認タスクの入口です。</p>
        </section>

        <section class="section-card" id="overview-modules">
          <h2>機能モジュール</h2>
          <table class="module-jump-table">
            <thead><tr><th>区分</th><th>モジュール</th><th>移動</th></tr></thead>
            <tbody>
              <tr class="module-jump"><td>ルール設定</td><td>ルール設定モジュール全体</td><td><a class="jump-link" href="#admin-guide">開く</a></td></tr>
              <tr class="module-jump"><td>ルール設定</td><td>マスターデータ設定</td><td><a class="jump-link" href="#admin-master-data-config">開く</a></td></tr>
              <tr class="module-jump"><td>ルール設定</td><td>帳票タイプ設定</td><td><a class="jump-link" href="#admin-doctype-config">開く</a></td></tr>
              <tr class="module-jump"><td>業務操作</td><td>業務操作モジュール全体</td><td><a class="jump-link" href="#operator-guide">開く</a></td></tr>
              <tr class="module-jump"><td>業務操作</td><td>案件一覧</td><td><a class="jump-link" href="#operator-case-module">開く</a></td></tr>
              <tr class="module-jump"><td>システム設定</td><td>システム設定モジュール全体</td><td><a class="jump-link" href="#system-settings">開く</a></td></tr>
              <tr class="module-jump"><td>システム設定</td><td>ユーザー管理</td><td><a class="jump-link" href="#system-user-management">開く</a></td></tr>
            </tbody>
          </table>
        </section>
"""

ADMIN_GUIDE = """
        <section class="chapter-page" id="admin-guide">
          <p class="chapter-label">ルール設定モジュール</p>
          <h2>ルール設定モジュール</h2>
          <p>保険金請求のケースに沿って、推奨順序は <strong>モデル → API → マスターデータ → 帳票タイプ → 業務シーン設定 → データマッピング → AI検証設定</strong> です。</p>
          <p>各画面への到達順：<strong>モデル設定 → API設定 → マスターデータ設定 → 帳票タイプ設定 → 業務シーン設定 → データマッピング設定 → AI検証設定</strong>。各機能モジュールの操作手順と、画面だけでは分かりにくい適用タイミングを説明します。ロール詳細は <a class="jump-link" href="#overview-roles">ロール設定</a> を参照してください。</p>
        </section>
"""

MODEL_CONFIG = """
        <section class="section-card" id="admin-model-config">
          <p class="section-label">ルール設定モジュール</p>
          <h2>モデル設定</h2>
          <p>LLM への <span class="ui-text">API 接続</span> と <span class="ui-text">用途割当</span> を管理します。帳票タイプの AI 読取や業務シーン公開前に設定します。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text"><span class="ui-text">業務ルール設定</span> → <span class="ui-text">モデル設定</span> を開き、<span class="ui-text">API 接続</span> タブで登録済みの接続を確認します。<span class="ui-text">状態</span> 列で <span class="ui-text">有効</span> / <span class="ui-text">無効</span> を確認し、操作列の <span class="ui-text">接続テスト</span> で通信確認できます。新規登録する場合は <span class="ui-text">+ 接続を追加</span> をクリックします。</span></p>
            <figure class="screenshot-figure" data-shot="admin-model-config">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/model-api-connections-marked.png?v=3" data-lightbox="manual-shots" aria-label="モデル設定 API 接続一覧を拡大表示">
                  <img src="assets/model-api-connections-marked.png?v=3" alt="モデル設定 API 接続一覧">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text"><span class="ui-text">接続を追加</span> 画面で <span class="ui-text">プロバイダ</span>、API ベース URL、API キー、モデル名を設定して <span class="ui-text">保存</span> します。保存直後は接続情報が登録されただけで、まだ <span class="ui-text">有効</span> にはなりません。一覧の <span class="ui-text">接続テスト</span> を実行し、通信が成功した時点で状態が <span class="ui-text">有効</span> になり、そのモデル接続が業務処理で利用可能になります。独自エンドポイントを使う場合は <span class="ui-text">カスタム（OpenAI 互換）</span> を選びます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/model-provider-dropdown-marked.png?v=3" data-lightbox="manual-shots" aria-label="接続追加時のプロバイダ選択を拡大表示">
                  <img src="assets/model-provider-dropdown-marked.png?v=3" alt="接続追加時のプロバイダ選択">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">3</span><span class="step-text"><span class="ui-text">用途割当</span> タブで、<span class="ui-text">接続テスト</span> 済みで状態が <span class="ui-text">有効</span> なモデル接続のみを用途ごとに割り当て、保存します。OCR抽出用途に割り当てたモデルは、<span class="ui-text">帳票タイプ設定</span> の <span class="ui-text">AI読取設定</span> で主モデル・検証モデルの候補として表示されます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/model-usage-assignment-marked.png?v=2" data-lightbox="manual-shots" aria-label="モデル設定 用途割当を拡大表示">
                  <img src="assets/model-usage-assignment-marked.png?v=2" alt="モデル設定 用途割当">
                </a>
              </div>
            </figure>
          </div>
        </section>
"""

API_CONFIG = """
        <section class="section-card" id="admin-api-config">
          <p class="section-label">ルール設定モジュール</p>
          <h2>API設定</h2>
          <p><span class="ui-text">Open API</span> のエンドポイントと <span class="ui-text">API Key</span> を管理します。<span class="ui-text">通知 URL</span> は <span class="ui-text">業務シーン設定</span> の <span class="ui-text">通知設定</span> で定義します。</p>
          <h3>操作ポイント</h3>
          <ol>
            <li><span class="ui-text">業務ルール設定</span> → <span class="ui-text">API設定</span> を開きます。</li>
            <li>画面の詳細説明は、別途用意している API 接続文書を参照します。</li>
            <li>ここでは API を使う前提だけを確認し、実装や接続手順の詳細は <span class="ui-text">API 文書</span> 側で管理します。</li>
          </ol>
          <div class="notice info">
            <strong>適用ルール</strong>
            API は外部システム連携の入口です。アップロード後の処理は公開済みの <span class="ui-text">業務シーン設定</span> に従います。
          </div>
        </section>
"""

OPERATOR_GUIDE = """
        <section class="chapter-page" id="operator-guide">
          <p class="chapter-label">業務操作モジュール</p>
          <h2>業務操作モジュール</h2>
          <p>公開済みの業務シーン（本マニュアルでは <span class="ui-text">保険金請求</span>）を前提に、資料アップロードから案件確認、<span class="ui-text">マイタスク</span> での人工確認・出力までを説明します。</p>
        </section>
"""

SYSTEM_SETTINGS = """
        <section class="chapter-page" id="system-settings">
          <p class="chapter-label">システム設定モジュール</p>
          <h2>システム設定モジュール</h2>
          <p><span class="ui-text">ユーザー管理</span>、<span class="ui-text">権限管理</span>、<span class="ui-text">セキュリティ設定</span> で、アカウント・メニュー権限・データ保存期限を管理します。</p>
        </section>
"""


def read_chunk(name: str) -> str:
    return (CHUNKS / name).read_text(encoding="utf-8")


def split_master_doctype() -> tuple[str, str]:
    raw = read_chunk("admin-master-data-config-best-new.html")
    doctype_end = raw.index('    </section>\n\n        <section class="section-card" id="admin-master-data-config"')
    doctype = raw[: doctype_end + len("    </section>")]
    return noon_master_section(), doctype.strip()


def noon_master_section() -> str:
    """Master section as of 12:31 (vectorization + step 1 order fix)."""
    return """
        <section class="section-card" id="admin-master-data-config">
          <p class="section-label">ルール設定モジュール</p>
          <h2>マスターデータ設定</h2>
          <p>表記ゆれをマスター表で管理し、後続の <span class="ui-text">帳票タイプ設定</span> の <span class="ui-text">マスタ照合</span> 等から参照します。データ登録後は <span class="ui-text">ベクトル化状態</span> が <span class="ui-text">完了</span> になるまで照合に利用できません。</p>
          <h3>操作ポイント</h3>

          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text"><span class="ui-text">業務ルール設定</span> → <span class="ui-text">マスターデータ設定</span> を開き、<span class="ui-text">+ マスター追加</span> でマスター表を作成します（例：医薬品情報、銀行情報）。</span></p>
            <figure class="screenshot-figure" data-shot="admin-master-data-config">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/master-data-list-empty.png?v=7" data-lightbox="manual-shots" aria-label="マスターデータ設定 マスター追加を拡大表示">
                  <img src="assets/master-data-list-empty.png?v=7" alt="マスターデータ設定 マスター追加">
                </a>
              </div>
            </figure>
          </div>

          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text"><span class="ui-text">列設定</span> — 列名を定義し、照合・検索に使う列は <span class="ui-text">照会コード</span> を付けます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap shot-wrap-narrow">
                <a class="shot-link" href="assets/master-data-column-marked.png?v=7" data-lightbox="manual-shots" aria-label="マスターデータ設定 列設定を拡大表示">
                  <img src="assets/master-data-column-marked.png?v=7" alt="マスターデータ設定 列設定">
                </a>
              </div>
            </figure>
          </div>

          <div class="operation-step">
            <p><span class="step-code">3</span><span class="step-text">データ登録 — <span class="ui-text">+ 項目追加</span> で 1 行ずつ入力するか、<span class="ui-text">一括インポート</span> でファイル登録します（1 回最大 50,000 行）。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/master-data-append-marked.png?v=8" data-lightbox="manual-shots" aria-label="マスターデータ設定 項目追加を拡大表示">
                  <img src="assets/master-data-append-marked.png?v=8" alt="マスターデータ設定 項目追加">
                </a>
              </div>
            </figure>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/master-data-import-flow.png?v=8" data-lightbox="manual-shots" aria-label="マスターデータ設定 一括インポートを拡大表示">
                  <img src="assets/master-data-import-flow.png?v=8" alt="マスターデータ設定 一括インポート">
                </a>
              </div>
            </figure>
            <div class="notice info">
              <strong>ベクトル化状態の確認</strong>
              <span class="ui-text">+ 項目追加</span>・<span class="ui-text">一括インポート</span> でデータを登録した後は、一覧の <span class="ui-text">ベクトル化状態</span> を確認してください。状態が <span class="ui-text">完了</span> になって初めて、<span class="ui-text">帳票タイプ設定</span> の <span class="ui-text">マスタ照合</span>（<span class="ui-text">ハイブリッド検索</span> 等）で利用可能になります。<span class="ui-text">待機中</span>・<span class="ui-text">処理中</span> の行は完了まで待機してください。
              <br><br>
              1 万行規模以上の大量データでは、ベクトル化に <strong>30 分以上</strong> かかる場合があります。インポート直後に業務設定へ進む場合は、ベクトル化完了を待ってから <span class="ui-text">マスタ照合</span> の効果テストを行ってください。
              <br><br>
              状態が <span class="ui-text">失敗</span> の行がある場合は、操作列の <span class="ui-text">再実行</span> で該当行を手動リトライします。複数行まとめて処理する場合は、一覧上部の <span class="ui-text">ベクトル化再実行</span> も利用できます。
            </div>
          </div>
        </section>""".strip()


def apply_patch_file(html: str, patch_path: Path) -> str:
    data = json.loads(patch_path.read_text(encoding="utf-8"))
    old, new = data["old_string"], data["new_string"]
    if old not in html:
        raise RuntimeError(f"Patch failed: {patch_path.name}")
    return html.replace(old, new, 1)


def apply_noon_patches(html: str) -> str:
    return apply_patch_file(html, PATCHES / "index_html_L712_0.patch")


def apply_css_patch() -> None:
    """Best-effort: noon CSS lived in a richer stylesheet; skip if base CSS differs."""
    css = CSS.read_text(encoding="utf-8")
    data = json.loads((PATCHES / "common_css_L728_0.patch").read_text(encoding="utf-8"))
    old, new = data["old_string"], data["new_string"]
    if old in css:
        CSS.write_text(css.replace(old, new, 1), encoding="utf-8")
    elif new.split("\n")[0] not in css:
        print("Note: common.css noon patch skipped (stylesheet layout differs)")


def build() -> None:
    master, doctype = split_master_doctype()
    scene = read_chunk("admin-scene-config-best-new.html").strip()
    mapping = read_chunk("admin-data-mapping-config-best-new.html").strip()
    ai = read_chunk("admin-ai-verification-config-best-new.html").strip()
    upload = read_chunk("operator-upload-module-best-new.html").strip()
    case = read_chunk("operator-case-module-best-new.html").strip()
    task = read_chunk("operator-task-module-best-new.html").strip()
    user = read_chunk("system-user-management-best-new.html").strip()
    role = read_chunk("system-role-management-best-new.html").strip()
    security = read_chunk("system-security-settings-best-new.html").strip()

    body_parts = [
        OVERVIEW.strip(),
        ADMIN_GUIDE.strip(),
        MODEL_CONFIG.strip(),
        API_CONFIG.strip(),
        master,
        doctype,
        scene,
        mapping,
        ai,
        OPERATOR_GUIDE.strip(),
        upload,
        case,
        task,
        SYSTEM_SETTINGS.strip(),
        user,
        role,
        security,
    ]

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NeosAI マニュアル</title>
<link rel="stylesheet" href="common.css">
</head>
<body>
<header class="site-header">
  <h1>NeosAI マニュアル</h1>
  <p class="subtitle">本マニュアルでは、NeosAI IDP の主要機能と基本的な操作手順を説明します</p>
</header>
<div class="manual-shell">
{TOC}
  <main class="manual-content">
{chr(10).join(body_parts)}
  </main>
</div>
{LIGHTBOX_HTML}
{LIGHTBOX_SCRIPT}
</body>
</html>
"""

    html = apply_noon_patches(html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    INDEX.write_text(html, encoding="utf-8")
    apply_css_patch()
    lines = html.count("\n") + 1
    print(f"Restored {INDEX} ({lines} lines, {len(html)} bytes)")


if __name__ == "__main__":
    build()
