# Company Analysis Agent

このエージェントは、A2Aプロトコルを使用して、指定された企業の分析を行うエージェントです。
Web検索結果を利用して、企業の概要、業界情報、競合他社、最新ニュースなどの情報を収集・分析します。

## 機能

- JWT認証によるセキュアなアクセス制御
- 企業分析タスクの作成と管理
- Web検索結果を利用した企業情報の収集と分析
- A2Aプロトコルに準拠したエージェントカードとスキル定義

## インストール

```bash
# 仮想環境の作成と有効化
python -m venv .venv
source .venv/bin/activate  # Linuxの場合
# または
.venv\Scripts\activate  # Windowsの場合

# 依存パッケージのインストール
pip install -e .
```

## 使用方法

1. エージェントの起動:
```bash
python -m company_analysis_agent
```

2. 新規ユーザー登録:
```bash
curl -X POST http://localhost:8000/register -d "username=your_username&password=your_password"
```

3. ログインしてトークンを取得:
```bash
curl -X POST http://localhost:8000/token -d "username=your_username&password=your_password"
```

4. エージェントカードの取得:
```bash
curl http://localhost:8000/agent-card
```

5. 企業分析タスクの作成:
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer your_token" \
  -d "company_name=Google"
```

6. タスクの状態確認:
```bash
curl http://localhost:8000/tasks/task_id \
  -H "Authorization: Bearer your_token"
```

## API エンドポイント

- POST `/register` - 新規ユーザー登録
- POST `/token` - ユーザー認証とトークン発行
- GET `/agent-card` - エージェントカードの取得
- POST `/tasks` - 新規タスクの作成
- GET `/tasks/{task_id}` - タスクの状態取得
- GET `/tasks` - 全タスクのリスト取得
- DELETE `/tasks/{task_id}` - タスクの削除

## セキュリティに関する注意

- 本番環境では、`SECRET_KEY`を安全な方法で管理してください
- 実際の実装では、ユーザー情報をデータベースで管理することを推奨します
- Web検索の実装では、適切なAPIを使用することを推奨します