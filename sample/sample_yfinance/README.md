# Stock Analysis Agent

このプロジェクトは、yfinanceを使用して株価データを取得し、Google ADKを利用して株価分析を行うAIエージェントを実装したものです。

## 機能

- yfinanceを使用した株価データの取得（AAPL, GOOGLの株価情報）
- Google ADKを使用した株価分析
  - 株価の全体的なトレンド分析
  - 重要な価格変動とその要因の分析
  - 取引量の変化の分析
  - 銘柄間の比較分析
- 分析結果のわかりやすい説明

## 必要要件

- Python 3.8以上
- uv（モダンなPythonパッケージマネージャー）

## インストール

1. uvのインストール（まだインストールしていない場合）:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 仮想環境の作成とアクティベート:
```bash
uv venv
source .venv/bin/activate  # Unix/macOS
# または
.venv\Scripts\activate  # Windows
```

3. 依存パッケージのインストール:
```bash
# uv.lockファイルから依存パッケージをインストール
uv sync
```

4. 環境変数の設定:
   - プロジェクトのルートディレクトリに`.env`ファイルを作成
   - 以下の内容を追加:
```
GOOGLE_API_KEY=your_api_key_here
```

## 使い方

1. プロジェクトのディレクトリに移動:
```bash
cd sample/sample_yfinance
```

2. スクリプトの実行:
```bash
uv python main.py
```

### 実行モード

スクリプトは2つのモードで実行できます：

1. 実際のデータを使用:
```python
stock_datas = get_stock_data(use_dummy_data=False)  # デフォルト
```

2. ダミーデータを使用（テスト用）:
```python
stock_datas = get_stock_data(use_dummy_data=True)
```

## 出力例

実行すると、以下のような形式で結果が表示されます：

```
=== 株価分析結果 ===
[AIエージェントによる分析結果がここに表示されます]
==================
```

## エラーハンドリング

スクリプトは以下のような状況を適切に処理します：

- GOOGLE_API_KEYが設定されていない場合のエラー表示
- 株価データの取得に失敗した場合のエラー処理
- エージェントの実行時のエラー処理

## 注意事項

- Google ADKを使用するには、有効なAPI keyが必要です
- yfinanceの利用規約に従って使用してください
- 株価データは実際の市場データとタイムラグがある可能性があります
- uvを使用することで、パッケージのインストールと実行が高速化されます
- uv.lockファイルにより、チーム間で同じバージョンのパッケージを使用できます
