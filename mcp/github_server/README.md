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

### 1. .envファイルの作成

まず、`.env`ファイルを作成し、必要な値を設定します。

```bash
make setup-env
cp .env.template .env
# エディタで .env を編集
```

- `GITHUB_TOKEN` にはGitHubのPersonal Access Tokenを設定してください。
- 必要に応じて `GITHUB_APP_ID` や `GITHUB_APP_PRIVATE_KEY` も設定できます。
- GCPの設定値（`PROJECT_ID` など）は省略可能で、gcloudのデフォルト値が使われます。

### 2. GitHubトークンの準備

GitHub Personal Access Tokenを取得してください：
1. GitHub.com にログイン
2. Settings > Developer settings > Personal access tokens > Tokens (classic)
3. "Generate new token" をクリック
4. 必要な権限を選択（repo, workflow等）
5. トークンを生成し、安全に保存

### 3. 前提条件の確認

```bash
make check-prerequisites
```

### 4. Google Cloud認証

```bash
make auth
```

## デプロイメント

### 基本的なデプロイメント

`.env`ファイルに必要な値を記載した上で、以下のコマンドでデプロイします：

```bash
make deploy
```

### Secret Managerを使用したデプロイメント（推奨）

1. `.env`ファイルにシークレット情報を記載した上で、シークレットを作成：

```bash
make create-secrets
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
make test-local
```

## 設定オプション

### .envファイルの例

`.env.template` を参考にしてください。

```
# GitHub MCP Server Environment Configuration
# Copy this file to .env and fill in your values

# GitHub Personal Access Token (required)
GITHUB_TOKEN=your_github_token_here

# GitHub App Configuration (optional)
GITHUB_APP_ID=your_github_app_id_here
GITHUB_APP_PRIVATE_KEY=your_github_app_private_key_here

# GCP Configuration (optional)
PROJECT_ID=your_gcp_project_id_here
REGION=asia-northeast1
SERVICE_NAME=github-mcp-server
```

### 必須・任意の変数

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | はい |
| `GITHUB_APP_ID` | GitHub App ID（オプション） | いいえ |
| `GITHUB_APP_PRIVATE_KEY` | GitHub App Private Key（オプション） | いいえ |
| `PROJECT_ID` | GCPプロジェクトID（省略可） | いいえ |
| `REGION` | Cloud Runのリージョン（省略可） | いいえ |
| `SERVICE_NAME` | Cloud Runサービス名（省略可） | いいえ |

## 利用可能なコマンド

```bash
make help
```

### 主要なコマンド

- `make setup-env` - .envテンプレートの作成
- `make check-prerequisites` - 前提条件の確認
- `make auth` - GCP認証
- `make deploy` - デプロイ
- `make deploy-with-secret` - Secret Managerを使用したデプロイ
- `make create-secrets` - Secret Managerにシークレットを作成
- `make status` - サービス状態の確認
- `make logs` - ログの表示
- `make delete` - サービスの削除
- `make clean` - Dockerイメージのクリーンアップ
- `make test-local` - ローカルテスト

## トラブルシューティング

### よくある問題

1. **.envファイルがない/値が未設定**
   ```bash
   make setup-env
   cp .env.template .env
   # .envを編集
   ```
2. **認証エラー**
   ```bash
   make auth
   ```
3. **APIが有効になっていない**
   ```bash
   make enable-apis
   ```
4. **Dockerイメージの取得に失敗**
   ```bash
   make pull-image
   ```
5. **権限エラー**
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