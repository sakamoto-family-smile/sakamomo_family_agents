# GitHub MCP Server GCP Deployment

このプロジェクトは、GitHub MCPサーバーをGoogle Cloud Platform (GCP) のCloud Run上にデプロイするためのMakefileを提供します。

## 概要

GitHub MCPサーバーは、GitHubのリポジトリ、イシュー、プルリクエストなどの情報にアクセスするためのMCP (Model Context Protocol) サーバーです。このプロジェクトでは、公式のDockerイメージを使用してGCP Cloud Run上にサーバーレスでデプロイします。

## 前提条件

- Google Cloud SDK (gcloud CLI)
- Docker
- GitHub Personal Access Token
- GCPプロジェクト

## セットアップ

### 1. 前提条件の確認

```bash
make check-prerequisites
```

### 2. Google Cloud認証

```bash
make auth
```

### 3. 設定ファイルの作成

```bash
make setup-config
```

作成された `config/config.template.env` を `config/config.env` にコピーし、必要な値を設定してください：

```bash
cp config/config.template.env config/config.env
# エディタで config/config.env を編集
```

### 4. GitHubトークンの準備

GitHub Personal Access Tokenを取得してください：
1. GitHub.com にログイン
2. Settings > Developer settings > Personal access tokens > Tokens (classic)
3. "Generate new token" をクリック
4. 必要な権限を選択（repo, workflow等）
5. トークンを生成し、安全に保存

## デプロイメント

### 基本的なデプロイメント

環境変数を直接指定してデプロイ：

```bash
make deploy GITHUB_TOKEN=your_token_here
```

### Secret Managerを使用したデプロイメント（推奨）

1. シークレットを作成：

```bash
make create-secrets \
  GITHUB_TOKEN=your_token_here \
  GITHUB_APP_ID=your_app_id_here \
  GITHUB_APP_PRIVATE_KEY=your_private_key_here
```

2. シークレットを使用してデプロイ：

```bash
make deploy-with-secret
```

## 使用方法

### サービスの状態確認

```bash
make status
```

### サービスURLの取得

```bash
make get-url
```

### ログの確認

```bash
make logs
```

### ローカルテスト

```bash
make test-local GITHUB_TOKEN=your_token_here
```

## 設定オプション

### 環境変数

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | はい |
| `GITHUB_APP_ID` | GitHub App ID（オプション） | いいえ |
| `GITHUB_APP_PRIVATE_KEY` | GitHub App Private Key（オプション） | いいえ |

### GCP設定

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `PROJECT_ID` | gcloud configから取得 | GCPプロジェクトID |
| `REGION` | asia-northeast1 | Cloud Runのリージョン |
| `SERVICE_NAME` | github-mcp-server | Cloud Runサービス名 |

## 利用可能なコマンド

```bash
make help
```

### 主要なコマンド

- `make deploy` - 基本的なデプロイメント
- `make deploy-with-secret` - Secret Managerを使用したデプロイメント
- `make create-secrets` - Secret Managerにシークレットを作成
- `make status` - サービス状態の確認
- `make logs` - ログの表示
- `make delete` - サービスの削除
- `make clean` - Dockerイメージのクリーンアップ

## トラブルシューティング

### よくある問題

1. **認証エラー**
   ```bash
   make auth
   ```

2. **APIが有効になっていない**
   ```bash
   make enable-apis
   ```

3. **Dockerイメージの取得に失敗**
   ```bash
   make pull-image
   ```

4. **権限エラー**
   - GCPプロジェクトに適切な権限があることを確認
   - GitHubトークンに必要な権限があることを確認

### ログの確認

```bash
make logs
```

## セキュリティ

- GitHubトークンはSecret Managerを使用して安全に管理することを推奨
- 本番環境では `--allow-unauthenticated` フラグを削除し、適切な認証を設定
- 最小権限の原則に従ってGitHubトークンの権限を設定

## コスト最適化

- Cloud Runは使用量に応じて課金されるため、自動スケーリングが効率的
- `--max-instances` パラメータで最大インスタンス数を制限可能
- 使用していない時は `make delete` でサービスを削除してコストを削減

## 参考リンク

- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)