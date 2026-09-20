#!/usr/bin/env python3
"""Assemble manual/index.html for single-page NeosAI manual."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANUAL = ROOT / "manual"
INDEX = MANUAL / "index.html"
CHUNKS = MANUAL / "scripts/transcript-chunks"

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
          <a class="toc-child" href="#admin-doctype-config">帳票タイプ設定</a>
          <a class="toc-child" href="#admin-master-data-config">マスターデータ設定</a>
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

OVERVIEW_HOME = """
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
              <div class="flow-node">帳票タイプ設定</div>
              <div class="flow-node">マスターデータ設定</div>
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
          <p>保険金請求のケースに沿って、推奨順序は <strong>モデル → API → 帳票タイプ → マスターデータ → 業務シーン設定 → データマッピング → AI検証設定</strong> です。</p>
          <p>各画面への到達順：<strong>モデル設定 → API設定 → 帳票タイプ設定 → マスターデータ設定 → 業務シーン設定 → データマッピング設定 → AI検証設定</strong>。各機能モジュールの操作手順と、画面だけでは分かりにくい適用タイミングを説明します。ロール詳細は <a class="jump-link" href="#overview-roles">ロール設定</a> を参照してください。</p>
        </section>
"""

MODEL_CONFIG = """
        <section class="section-card" id="admin-model-config">
          <p class="section-label">ルール設定モジュール</p>
          <h2>モデル設定</h2>
          <p>LLM への <span class="ui-text">API 接続</span> と <span class="ui-text">用途割当</span> を管理します。帳票タイプの AI 読取や業務シーン公開前に設定します。</p>
          <h3>操作手順</h3>
          <div class="figure-row">
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text"><span class="ui-text">業務ルール設定</span> → <span class="ui-text">モデル設定</span> を開き、<span class="ui-text">API 接続</span> タブで登録済み接続を確認します。新規は <span class="ui-text">接続を追加</span> をクリックします。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/model-api-add-flow.png" data-lightbox="manual-shots" aria-label="モデル設定 API 接続一覧">
                  <img src="assets/model-api-add-flow.png" alt="モデル設定 API 接続一覧">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text"><span class="ui-text">接続を追加</span> で <span class="ui-text">プロバイダ</span>、API ベース URL、API キー、モデル名を設定して <span class="ui-text">保存</span> します。独自エンドポイントは <span class="ui-text">カスタム（OpenAI 互換）</span> を選びます。保存後 <span class="ui-text">接続テスト</span> で <span class="ui-text">有効</span> にします。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/model-provider-select-flow.png" data-lightbox="manual-shots" aria-label="接続追加 プロバイダ選択">
                  <img src="assets/model-provider-select-flow.png" alt="接続追加 プロバイダ選択">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">3</span><span class="step-text"><span class="ui-text">用途割当</span> タブで OCR 抽出・AI 検証などの用途ごとにモデルを割り当てます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/model-usage-assignment-marked.png" data-lightbox="manual-shots" aria-label="モデル設定 用途割当">
                  <img src="assets/model-usage-assignment-marked.png" alt="モデル設定 用途割当">
                </a>
              </div>
            </figure>
          </div>
          </div>
        </section>
"""

API_CONFIG = """
        <section class="section-card" id="admin-api-config">
          <p class="section-label">ルール設定モジュール</p>
          <h2>API設定</h2>
          <p><span class="ui-text">Open API</span> のエンドポイントと <span class="ui-text">API Key</span> を管理します。<span class="ui-text">通知 URL</span> は <span class="ui-text">業務シーン設定</span> の <span class="ui-text">通知設定</span> で定義します。</p>
          <h3>操作手順</h3>
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

DOCTYPE_CONFIG = """
        <section class="section-card" id="admin-doctype-config" data-shot="admin-doctype-config">
          <p class="section-label">ルール設定モジュール</p>
          <h2>帳票タイプ設定</h2>
          <p>帳票タイプごとに <span class="ui-text">AI分類設定</span>、<span class="ui-text">AI読取設定</span>、<span class="ui-text">処理ルール設定</span>、<span class="ui-text">画像処理設定</span>、<span class="ui-text">効果テスト</span> の 5 ステップで設定します。保険金請求では <span class="ui-text">保険金請求書</span>、<span class="ui-text">診断書</span>、<span class="ui-text">診療明細書</span>、<span class="ui-text">領収書</span>、<span class="ui-text">調剤明細書</span> を順に設定します。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text"><span class="ui-text">+タイプ追加</span> で帳票タイプを選択し、<span class="ui-text">AI分類設定</span> で分類条件と説明文を整えます。図では、タイプ追加と分類設定の位置を確認します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/doctype-step-1-marked.png" data-lightbox="manual-shots" aria-label="帳票タイプ設定 AI分類設定">
                  <img src="assets/doctype-step-1-marked.png" alt="帳票タイプ設定 AI分類設定">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text"><span class="ui-text">AI読取設定</span> で項目とテーブルを定義します。設定アイコンから <span class="ui-text">読取モデル設定</span> でメイン／検証モデルを選びます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/doctype-step-2-model-settings.png" data-lightbox="manual-shots" aria-label="帳票タイプ設定 AI読取設定">
                  <img src="assets/doctype-step-2-model-settings.png" alt="帳票タイプ設定 AI読取設定">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">3</span><span class="step-text"><span class="ui-text">処理ルール設定</span> で表記ゆれ補正、日付変換、<span class="ui-text">マスタ照合</span> などの後処理を指定します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/doctype-step-3-marked.png" data-lightbox="manual-shots" aria-label="帳票タイプ設定 処理ルール設定">
                  <img src="assets/doctype-step-3-marked.png" alt="帳票タイプ設定 処理ルール設定">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">4</span><span class="step-text"><span class="ui-text">画像処理設定</span> で <span class="ui-text">画像組合</span> と <span class="ui-text">画像整列</span> を設定します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/doctype-step-4-enabled-marked.png" data-lightbox="manual-shots" aria-label="帳票タイプ設定 画像処理設定">
                  <img src="assets/doctype-step-4-enabled-marked.png" alt="帳票タイプ設定 画像処理設定">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">5</span><span class="step-text"><span class="ui-text">効果テスト</span> でテキスト読取とテーブル情報読取の結果を確認します。</span></p>
            <div class="figure-row">
              <figure class="screenshot-figure">
                <div class="shot-wrap">
                  <a class="shot-link" href="assets/doctype-step-5-text-marked.png" data-lightbox="manual-shots" aria-label="帳票タイプ設定 効果テスト テキスト">
                    <img src="assets/doctype-step-5-text-marked.png" alt="帳票タイプ設定 効果テスト テキスト">
                  </a>
                </div>
              </figure>
              <figure class="screenshot-figure">
                <div class="shot-wrap">
                  <a class="shot-link" href="assets/doctype-step-5-table-marked.png" data-lightbox="manual-shots" aria-label="帳票タイプ設定 効果テスト テーブル">
                    <img src="assets/doctype-step-5-table-marked.png" alt="帳票タイプ設定 効果テスト テーブル">
                  </a>
                </div>
              </figure>
            </div>
          </div>
          <div class="notice warning">
            <strong>適用ルール</strong>
            帳票タイプ設定は、ファイルアップロード後の分類、OCR 抽出、人工確認前の処理段階で適用されます。項目がデータマッピング、AI検証、出力設定から参照されている場合、削除や名称変更は下流設定に影響します。
          </div>
        </section>
"""

MASTER_DATA = """
        <section class="section-card" id="admin-master-data-config">
          <p class="section-label">ルール設定モジュール</p>
          <h2>マスターデータ設定</h2>
          <p><span class="ui-text">医療機関名</span>、<span class="ui-text">傷病名</span>、<span class="ui-text">薬品名</span>、<span class="ui-text">銀行</span>・<span class="ui-text">支店</span> などの表記ゆれをマスター表で管理し、<span class="ui-text">マスタ照合</span> や <span class="ui-text">標準データ整合性</span> 検証から参照します。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text"><span class="ui-text">+ マスター追加</span> でマスター表を作成します。</span></p>
          </div>
          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text"><span class="ui-text">列設定</span> で列名を定義し、照合列には <span class="ui-text">照会コード</span> を付けます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/master-data-column-settings.png" data-lightbox="manual-shots" aria-label="マスターデータ 列設定">
                  <img src="assets/master-data-column-settings.png" alt="マスターデータ 列設定">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">3</span><span class="step-text"><span class="ui-text">+ 項目追加</span> で 1 行ずつ登録するか、<span class="ui-text">一括インポート</span> で <span class="ui-text">追加更新</span> または <span class="ui-text">上書更新</span> します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/master-data-import-flow.png" data-lightbox="manual-shots" aria-label="マスターデータ 一括インポート">
                  <img src="assets/master-data-import-flow.png" alt="マスターデータ 一括インポート">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">4</span><span class="step-text">一覧で <span class="ui-text">編集</span>、<span class="ui-text">削除</span>、<span class="ui-text">再ベクトル化</span> を行います。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/master-data-table.png" data-lightbox="manual-shots" aria-label="マスターデータ 一覧">
                  <img src="assets/master-data-table.png" alt="マスターデータ 一覧">
                </a>
              </div>
            </figure>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/master-data-inline-edit.png" data-lightbox="manual-shots" aria-label="マスターデータ インライン編集">
                  <img src="assets/master-data-inline-edit.png" alt="マスターデータ インライン編集">
                </a>
              </div>
            </figure>
          </div>
          <figure class="screenshot-figure">
            <div class="shot-wrap">
              <a class="shot-link" href="assets/master-data-usage-marked.png" data-lightbox="manual-shots" aria-label="マスターデータ 利用箇所">
                <img src="assets/master-data-usage-marked.png" alt="マスターデータ 利用箇所">
              </a>
            </div>
          </figure>
        </section>
"""

DATA_MAPPING = """
        <section class="section-card" id="admin-data-mapping-config">
          <p class="section-label">ルール設定モジュール</p>
          <h2>データマッピング設定</h2>
          <p>複数帳票の OCR 項目を案件単位の <span class="ui-text">標準項目</span> へ整理します。各 <span class="ui-text">標準項目</span> に <span class="ui-text">参照元の帳票タイプ</span> と OCR 項目を紐付け、複数参照がある場合は <span class="ui-text">優先度</span> を設定します。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text"><span class="ui-text">マッピングルール生成</span> で <span class="ui-text">標準項目</span> を追加します。</span></p>
            <figure class="screenshot-figure" data-shot="admin-data-mapping-config">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/data-mapping-list.png" data-lightbox="manual-shots" aria-label="データマッピング設定">
                  <img src="assets/data-mapping-list.png" alt="データマッピング設定">
                </a>
              </div>
            </figure>
          </div>
          <div class="notice warning">
            <strong>適用ルール</strong>
            <span class="ui-text">データマッピング</span> は <span class="ui-text">業務シーン設定</span> の <span class="ui-text">ワークフロー設定</span> 内ノードで実行されます。<span class="ui-text">項目の競合</span> や整合性は <span class="ui-text">AI検証</span> で扱います。
          </div>
        </section>
"""

SCENE_CONFIG = """
        <section class="section-card" id="admin-scene-config">
          <p class="section-label">ルール設定モジュール</p>
          <h2>業務シーン設定</h2>
          <p><span class="ui-text">業務シーン・案件集約</span>、<span class="ui-text">ワークフロー設定</span>、<span class="ui-text">通知設定</span>、<span class="ui-text">エクスポート設定</span> の 4 ステップで <span class="ui-text">保険金請求</span> を構成します。</p>
          <p>案件集約ルールは、同一案件にまとめるかどうかを決めます。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text">Step1 — 案件集約で帳票集合と業務キーを定義し、<span class="ui-text">関連チェック</span> で到達性を確認します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/business-scene-basic-related-marked.png" data-lightbox="manual-shots" aria-label="業務シーン Step1 案件集約">
                  <img src="assets/business-scene-basic-related-marked.png" alt="業務シーン Step1 案件集約">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text">Step2 — <span class="ui-text">ワークフロー設定</span> で <span class="ui-text">開始</span> から OCR・<span class="ui-text">データマッピング</span>・AI 検証へ接続し、<span class="ui-text">IF/ELSE</span> で人工確認分岐を置きます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/business-scene-workflow-flow.png" data-lightbox="manual-shots" aria-label="業務シーン ワークフロー">
                  <img src="assets/business-scene-workflow-flow.png" alt="業務シーン ワークフロー">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">3</span><span class="step-text">Step3 — <span class="ui-text">通知設定</span> でイベントごとの通知先を登録します。<span class="ui-text">通知設定</span>は、実行時に該当ノードが存在し、イベント条件に一致した場合のみ起動します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/business-scene-notify-marked.png" data-lightbox="manual-shots" aria-label="業務シーン 通知設定">
                  <img src="assets/business-scene-notify-marked.png" alt="業務シーン 通知設定">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">4</span><span class="step-text">Step4 — <span class="ui-text">エクスポート設定</span> で出力項目を選び公開します。<span class="ui-text">エクスポート設定</span>は、<span class="ui-text">マイタスク</span> から取得する出力結果の範囲を決めます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/business-scene-export-marked.png" data-lightbox="manual-shots" aria-label="業務シーン エクスポート設定">
                  <img src="assets/business-scene-export-marked.png" alt="業務シーン エクスポート設定">
                </a>
              </div>
            </figure>
          </div>
        </section>
"""

AI_VERIFICATION = (CHUNKS / "admin-ai-verification-config-best-new.html").read_text(encoding="utf-8").replace(
    "AI検証ルールは、<span class=\"ui-text\">業務シーン設定</span> の <span class=\"ui-text\">ワークフロー設定</span> 内にある <span class=\"ui-text\">AI検証</span> ノードで適用されます。",
    "AI検証ルールは、業務シーンのワークフロー内にある <span class=\"ui-text\">AI検証</span> ノードで適用されます。",
)

OPERATOR_GUIDE = """
        <section class="chapter-page" id="operator-guide">
          <p class="chapter-label">業務操作モジュール</p>
          <h2>業務操作モジュール</h2>
          <p>操作員は同一の保険金請求案件を対象に、資料アップロード → 案件一覧での進捗確認 → <span class="ui-text">マイタスク</span> での人工確認、補足資料対応、出力結果の取得、までを行います。</p>
        </section>
"""

OPERATOR_UPLOAD = """
        <section class="section-card" id="operator-upload-module">
          <p class="section-label">業務操作モジュール</p>
          <h2>新規アップロード</h2>
          <p>公開済み <span class="ui-text">保険金請求</span> シーンを選び、PDF / 画像をアップロードして分類・案件集約を実行します。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text">サイドバー <span class="ui-text">新規アップロード</span> で <span class="ui-text">業務シーン</span> を選び、ファイルを追加して <span class="ui-text">分類・案件集約を実行</span> します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/operator-upload-main-marked.png" data-lightbox="manual-shots" aria-label="新規アップロード画面">
                  <img src="assets/operator-upload-main-marked.png" alt="新規アップロード画面">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text">アップロード前にプレビューで向き・解像度を確認できます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/operator-upload-preview.png" data-lightbox="manual-shots" aria-label="アップロードプレビュー">
                  <img src="assets/operator-upload-preview.png" alt="アップロードプレビュー">
                </a>
              </div>
            </figure>
          </div>
        </section>
"""

OPERATOR_CASE = """
        <section class="section-card" id="operator-case-module">
          <p class="section-label">業務操作モジュール</p>
          <h2>案件一覧</h2>
          <p><span class="ui-text">集約済み案件</span> と <span class="ui-text">未集約ファイル</span> を確認し、案件を展開すると、ファイル名・帳票タイプ・<span class="ui-text">ファイルステータス</span> を追跡できます。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text"><span class="ui-text">集約済み案件</span> タブで一覧を確認します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/case-list-overview-marked.png" data-lightbox="manual-shots" aria-label="案件一覧 集約済み">
                  <img src="assets/case-list-overview-marked.png" alt="案件一覧 集約済み">
                </a>
              </div>
            </figure>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/case-list-case-header.png" data-lightbox="manual-shots" aria-label="案件ヘッダー">
                  <img src="assets/case-list-case-header.png" alt="案件ヘッダー">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text">案件を展開すると、ファイル名、帳票タイプ、<span class="ui-text">ファイルステータス</span> など配下ファイルの一覧が表示されます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/case-list-expanded-files.png" data-lightbox="manual-shots" aria-label="展開後ファイル一覧">
                  <img src="assets/case-list-expanded-files.png" alt="展開後ファイル一覧">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">3</span><span class="step-text">詳細画面の <span class="ui-text">ファイル一覧</span> タブでプレビューを確認します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/case-list-file-detail-marked.png" data-lightbox="manual-shots" aria-label="案件詳細">
                  <img src="assets/case-list-file-detail-marked.png" alt="案件詳細">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">4</span><span class="step-text"><span class="ui-text">ワークフロー明細</span> で処理フローとノード進捗を確認します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/case-list-workflow.png" data-lightbox="manual-shots" aria-label="ワークフロー明細">
                  <img src="assets/case-list-workflow.png" alt="ワークフロー明細">
                </a>
              </div>
            </figure>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/case-list-workflow-nodes.png" data-lightbox="manual-shots" aria-label="ワークフローノード">
                  <img src="assets/case-list-workflow-nodes.png" alt="ワークフローノード">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">5</span><span class="step-text"><span class="ui-text">割当</span>、<span class="ui-text">処理中止</span>、ファイル <span class="ui-text">案件変更</span> の各ダイアログを利用します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/case-list-assign-modal.png" data-lightbox="manual-shots" aria-label="担当者割当">
                  <img src="assets/case-list-assign-modal.png" alt="担当者割当">
                </a>
              </div>
            </figure>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/case-list-change-modal.png" data-lightbox="manual-shots" aria-label="案件変更">
                  <img src="assets/case-list-change-modal.png" alt="案件変更">
                </a>
              </div>
            </figure>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/case-list-stop-modal.png" data-lightbox="manual-shots" aria-label="処理中止">
                  <img src="assets/case-list-stop-modal.png" alt="処理中止">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">6</span><span class="step-text"><span class="ui-text">未集約ファイル</span> タブで手動紐付けを行います。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/case-list-unaggregated.png" data-lightbox="manual-shots" aria-label="未集約ファイル">
                  <img src="assets/case-list-unaggregated.png" alt="未集約ファイル">
                </a>
              </div>
            </figure>
          </div>
        </section>
"""

OPERATOR_TASK = """
        <section class="section-card" id="operator-task-module">
          <p class="section-label">業務操作モジュール</p>
          <h2>マイタスク</h2>
          <p><span class="ui-text">マイタスク</span> はすべての人工確認タスクの入口です。<span class="ui-text">OCR確認</span>、<span class="ui-text">AI検証確認</span>、<span class="ui-text">補足資料対応</span>、<span class="ui-text">出力結果</span> の取得までをここから行います。出力項目は <span class="ui-text">出力設定・公開</span> で定義された範囲に従います。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text">未対応タスク一覧から <span class="ui-text">対応</span> を開きます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/operator-task-list-marked.png" data-lightbox="manual-shots" aria-label="マイタスク一覧">
                  <img src="assets/operator-task-list-marked.png" alt="マイタスク一覧">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text"><span class="ui-text">OCR確認</span> — 帳票画像と抽出結果を対照して修正します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/operator-task-ocr-position-marked.png" data-lightbox="manual-shots" aria-label="OCR確認">
                  <img src="assets/operator-task-ocr-position-marked.png" alt="OCR確認">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">3</span><span class="step-text"><span class="ui-text">AI検証確認</span> — 完備性・データ検証・印鑑署名の結果を確認します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/operator-task-ai-verify-flow.png" data-lightbox="manual-shots" aria-label="AI検証確認">
                  <img src="assets/operator-task-ai-verify-flow.png" alt="AI検証確認">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">4</span><span class="step-text"><span class="ui-text">補足資料対応</span> — ワークフロー上の <span class="ui-text">補件</span> 出口に従い、追加書類を案件へ直接アップロードします。</span></p>
          </div>
          <div class="operation-step">
            <p><span class="step-code">5</span><span class="step-text"><span class="ui-text">出力結果</span> — ワークフロー完了後、エクスポート内容を確認して提出します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/operator-task-export-marked.png" data-lightbox="manual-shots" aria-label="出力結果">
                  <img src="assets/operator-task-export-marked.png" alt="出力結果">
                </a>
              </div>
            </figure>
          </div>
        </section>
"""

SYSTEM_SETTINGS = """
        <section class="chapter-page" id="system-settings">
          <p class="chapter-label">システム設定モジュール</p>
          <h2>システム設定モジュール</h2>
          <p><span class="ui-text">ユーザー管理</span>、<span class="ui-text">権限管理</span>、<span class="ui-text">セキュリティ設定</span> で、アカウント・メニュー権限・データ保存期限を管理します。</p>
        </section>
"""

SYSTEM_USER = """
        <section class="section-card" id="system-user-management">
          <p class="section-label">システム設定モジュール</p>
          <h2>ユーザー管理</h2>
          <p>ユーザーの作成、<span class="ui-text">データ権限</span>、<span class="ui-text">パスワードリセット</span>、状態管理を行います。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text"><span class="ui-text">+ ユーザー追加</span> でユーザーを作成し、画面上部の <span class="ui-text">有効ユーザー数</span> で上限を確認します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/system-user-management-flow.png" data-lightbox="manual-shots" aria-label="ユーザー管理">
                  <img src="assets/system-user-management-flow.png" alt="ユーザー管理">
                </a>
              </div>
            </figure>
          </div>
        </section>
"""

SYSTEM_ROLE = """
        <section class="section-card" id="system-role-management">
          <p class="section-label">システム設定モジュール</p>
          <h2>権限管理</h2>
          <p>権限テンプレートを作成し、<span class="ui-text">メニュー権限</span> で機能モジュールへのアクセス範囲を設定します。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text"><span class="ui-text">+ 権限追加</span> でテンプレートを作成します。</span></p>
          </div>
          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text"><span class="ui-text">メニュー権限</span> を開き、付与するモジュールを選択して保存します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/system-role-menu-flow.png" data-lightbox="manual-shots" aria-label="権限管理 メニュー権限">
                  <img src="assets/system-role-menu-flow.png" alt="権限管理 メニュー権限">
                </a>
              </div>
            </figure>
          </div>
        </section>
"""

SYSTEM_SECURITY = """
        <section class="section-card" id="system-security-settings">
          <p class="section-label">システム設定モジュール</p>
          <h2>セキュリティ設定</h2>
          <p><span class="ui-text">データ保存期限設定</span> と <span class="ui-text">アイドルセッション設定</span> を管理します。</p>
          <h3>操作ポイント</h3>
          <div class="operation-step">
            <p><span class="step-code">1</span><span class="step-text"><span class="ui-text">データ保存期限設定</span> で読取データの自動削除サイクルを選びます。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/security-duration-flow.png" data-lightbox="manual-shots" aria-label="保存期限設定">
                  <img src="assets/security-duration-flow.png" alt="保存期限設定">
                </a>
              </div>
            </figure>
          </div>
          <div class="operation-step">
            <p><span class="step-code">2</span><span class="step-text"><span class="ui-text">アイドルセッション設定</span> で自動ログアウト時間を選び保存します。</span></p>
            <figure class="screenshot-figure">
              <div class="shot-wrap">
                <a class="shot-link" href="assets/security-idle-flow.png" data-lightbox="manual-shots" aria-label="アイドルセッション設定">
                  <img src="assets/security-idle-flow.png" alt="アイドルセッション設定">
                </a>
              </div>
            </figure>
          </div>
        </section>
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


def build() -> None:
    body = f"""<!DOCTYPE html>
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
{OVERVIEW_HOME}
{ADMIN_GUIDE}
{MODEL_CONFIG}
{API_CONFIG}
{DOCTYPE_CONFIG}
{MASTER_DATA}
{SCENE_CONFIG}
{DATA_MAPPING}
{AI_VERIFICATION}
{OPERATOR_GUIDE}
{OPERATOR_UPLOAD}
{OPERATOR_CASE}
{OPERATOR_TASK}
{SYSTEM_SETTINGS}
{SYSTEM_USER}
{SYSTEM_ROLE}
{SYSTEM_SECURITY}
  </main>
</div>
{LIGHTBOX_HTML}
{LIGHTBOX_SCRIPT}
</body>
</html>
"""
    INDEX.write_text(body, encoding="utf-8")
    print(f"Wrote {INDEX}")


if __name__ == "__main__":
    build()
