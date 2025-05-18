# Asset Securities Report Agent

このエージェントは、有価証券報告書の分析を行うエージェントです。EDINETから取得した有価証券報告書を解析し、経営戦略、財務状況、リスク、コーポレートガバナンス、ESGなどの観点から分析を行います。

## 機能

- 企業名からEDINETの有価証券報告書を検索
- 有価証券報告書の自動分析
- 分析結果のレポート生成

### 分析観点

1. 経営戦略と事業内容
   - 企業のビジョン、ミッション、経営理念
   - 主要な事業セグメントとその内容
   - 市場における競争優位性
   - 今後の事業展開の方向性
   - 事業ポートフォリオ分析

2. 財務状況
   - 収益性、安全性、効率性の分析
   - キャッシュフロー分析
   - 財務指標の推移分析

3. リスク
   - 事業リスクの分析
   - リスク管理体制の評価
   - 潜在的リスクの特定

4. コーポレートガバナンス
   - ガバナンス体制の分析
   - 取締役会の構成
   - 株主との関係
   - コンプライアンス体制

5. ESG
   - 環境への取り組み
   - 社会貢献活動
   - 企業統治の状況
   - サステナビリティへの取り組み

6. 株価状況
   - 直近1年の株価推移分析
   - 財務・事業との相関分析

## 必要要件

- Python 3.12以上
- Docker
- Google Cloud Platform アカウント
  - Artifact Registry API の有効化
  - Cloud Run API の有効化
  - Vertex AI API の有効化
  - BigQuery API の有効化
- EDINET API キー
- 必要な環境変数:
  - `GCP_PROJECT`: GCPプロジェクトID
  - `GCP_LOCATION`: GCPロケーション（例: asia-northeast1）
  - `EDINET_API_KEY`: EDINET APIキー
  - `GCS_LOG_BUCKET_NAME`: ログを保存するGCSのバケット名
  - `GOOGLE_API_KEY`: geminiのAPIキー
  - `LLM_MODEL_NAME`: geminiのモデル名

## セットアップと実行

すべての操作は`make`コマンドを通じて行います。

### ローカル環境での実行

1. Dockerイメージのビルド:
   ```bash
   make build
   ```

2. ローカルでのコンテナ実行:
   ```bash
   make run
   ```

3. ローカルコンテナのテスト:
   ```bash
   make test-local
   ```

4. ローカルコンテナの停止と削除:
   ```bash
   make clean
   ```

### Cloud Runへのデプロイ

1. Artifact Registryへのプッシュ:
   ```bash
   make push
   ```

2. Cloud Runへのデプロイ:
   ```bash
   make deploy
   ```

3. Cloud Runのテスト:
   ```bash
   BASE_URL=<cloud-run-url> make test-cloud-run
   ```

4. Cloud Runサービスの削除:
   ```bash
   make clean-cloud-run
   ```

## エラーハンドリング

- 企業が見つからない場合: 企業名が正確であることを確認してください
- API制限エラー: API呼び出しの制限に達した場合は、しばらく時間をおいて再試行してください
- 有価証券報告書が取得できない場合: EDINETの状態を確認し、再度実行してください

## 注意事項

- 有価証券報告書の取得には、EDINETの利用規約に従う必要があります
- APIキーは適切に管理し、公開リポジトリにコミットしないように注意してください
- 分析結果は参考情報であり、投資判断の根拠としては使用しないでください
