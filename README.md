# circuitjs-mcp

Falstad **CircuitJS1** 回路シミュレータを AI エージェントから操作できるようにする MCP サーバーです。標準の stdio MCP サーバーなので、Claude Code、Codex CLI、Claude Desktop、Cursor など MCP 対応クライアントならどれでも使えます。

コンパイル済みの CircuitJS1 ウェブアプリ（`webapp/` に同梱、オフライン動作）をヘッドレス Chromium (Playwright) 内で起動し、その [JavaScript インターフェース](https://www.falstad.com/circuit/doc/js-interface.html) を MCP ツールとして公開します。シミュレータの状態はツール呼び出しをまたいで保持されます（回路を読み込む → 走らせる → 測る → 回路を書き換える、が対話的にできます）。

## セットアップ

前提: Node.js 18 以上。

```bash
cd circuitjs-mcp
npm install          # postinstall で Playwright の Chromium も入ります
npm test             # スモークテスト（RC回路の過渡応答が理論値と一致するか等を検証）
```

`playwright install chromium` が環境的に難しい場合は、既存の Chrome/Chromium を使えます:

```bash
export CIRCUITJS_CHROMIUM="/usr/bin/google-chrome"   # 例
```

## MCP クライアントへの登録

起動コマンドはどのクライアントでも共通です: `node /絶対パス/circuitjs-mcp/server.mjs`

環境変数 `CIRCUITJS_HEADFUL=1` を付けるとブラウザウィンドウが表示され、人間もエージェントと同じシミュレータを直接操作できます（共同作業モード）。以下の例はすべてこの変数付きです。不要なら外してください。

**Claude Code:**

```bash
claude mcp add circuitjs -e CIRCUITJS_HEADFUL=1 -- node /絶対パス/circuitjs-mcp/server.mjs
```

**Codex CLI:**

```bash
codex mcp add circuitjs --env CIRCUITJS_HEADFUL=1 -- node /絶対パス/circuitjs-mcp/server.mjs
```

**設定ファイル方式のクライアント**（Claude Desktop の `claude_desktop_config.json`、Cursor の `mcp.json` など）:

```json
{
  "mcpServers": {
    "circuitjs": {
      "command": "node",
      "args": ["/絶対パス/circuitjs-mcp/server.mjs"],
      "env": { "CIRCUITJS_HEADFUL": "1" }
    }
  }
}
```

`screenshot` ツールは MCP の画像コンテンツとして PNG を返します。画像表示に対応しないクライアントでは `save_path` 引数でファイルに保存する運用にしてください。

## ツール一覧

| ツール | 機能 |
|---|---|
| `circuit_load` | Falstad テキスト形式の回路を読み込む（検証付き）。要素一覧を返す |
| `circuit_state` | 時刻・全要素の電圧差/電流/端子電圧、ラベル付きノードの電圧を取得 |
| `run_transient` | 指定シミュレーション時間だけ走らせ、プローブ（ノード電圧・要素電流/電圧/電力）の時系列をサンプリングして返す |
| `sim_control` | run / stop / reset / status、最大タイムステップ設定、外部電圧源の値設定 |
| `circuit_export` | 回路を Falstad テキストまたは SVG でエクスポート |
| `circuit_link` | 現在の回路（または指定テキスト）を falstad.com でそのまま開けるURL（`?ctz=`リンク）として生成。ブラウザで対話的に確認・編集したいときに |
| `screenshot` | 現在の回路図の PNG スクリーンショット（画像として返却、ファイル保存も可） |
| `eval_js` | 上記で足りない操作用のエスケープハッチ。`sim` オブジェクトに対して任意の JS を実行 |

### 使用例（エージェントへの指示イメージ）

- 「1kΩと1µFのRCローパスを組んで、1kHz矩形波を入れたときの出力波形を5ms分取得して」
- 「この回路（テキスト貼り付け）を読み込んで、各抵抗の消費電力を一覧にして」
- 「回路のスクリーンショットを見せて」

測定したい箇所には **ラベル付きノード**（要素タイプ `207`、例: `207 336 128 400 128 4 out`）を置くと `{"node":"out"}` プローブや `circuit_state` の `nodes` で電圧を読めます。要素単位の電流・電圧は `circuit_load` / `circuit_state` が返す `index` で指定します。

## スクリプトからの直接操作

MCP クライアントを介さずスクリプトからツールを叩きたい場合は `drive.mjs` が使えます。サーバーを子プロセスとして起動し、コマンドディレクトリに置いた JSON ファイル（`cmd-1.json`, `cmd-2.json`, ...）を順に実行して結果を `res-N.json` に書き出します:

```bash
node drive.mjs /tmp/cjs-commands
# 別プロセスから: echo '{"tool":"circuit_state","args":{}}' > /tmp/cjs-commands/cmd-1.json
```

ファイルは一時名に書いてから rename で置くこと（書き込み途中の読み取りを避けるため）。

## 環境変数

| 変数 | 意味 |
|---|---|
| `CIRCUITJS_CHROMIUM` | 使用する Chrome/Chromium 実行ファイルのパス（既定: Playwright 管理の Chromium。失敗時はシステム Chrome にフォールバック） |
| `CIRCUITJS_URL` | 同梱 webapp の代わりに読み込む CircuitJS1 の URL（例: `https://www.falstad.com/circuit/circuitjs.html`） |
| `CIRCUITJS_HEADFUL` | `1` でブラウザウィンドウを表示（デバッグ用） |

## 制限事項

- `run_transient` のシミュレーション速度は回路の `$` 行のシミュレーション速度設定と CPU に依存します。実時間がかかりすぎる場合は `wallTimeoutMs` で打ち切られ、部分データが返ります（`reason` フィールドで判別可能）。
- 回路の「編集」は Falstad テキストを書き換えて `circuit_load` し直すのが基本です（インポートで時刻はリセットされます）。
- 過渡解析のみ（CircuitJS1 自体が AC 小信号解析等を持たないため）。周波数特性は周波数を振って `run_transient` を繰り返すことで得られます。

## ライセンス

本リポジトリ全体を **GPL-2.0-or-later** で提供します（`COPYING.txt`）。

- CircuitJS1 は Paul Falstad / Iain Sharp による GPLv2+ のソフトウェアです。`webapp/` はそのコンパイル済みビルド（無改変）で、対応するソースコードは [pfalstad/circuitjs1](https://github.com/pfalstad/circuitjs1)（原作）および [code4fukui/circuitjs1](https://github.com/code4fukui/circuitjs1) の `pages` ブランチ（本ビルドの取得元）で入手できます。
- サーバーコード（`server.mjs`, `drive.mjs`, `test-client.mjs`）© 2026 Suzu（涼鈴）、GPL-2.0-or-later。
