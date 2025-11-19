# メールフォーム営業システム - Railway版

## 🚀 Railwayで5分デプロイ

このバージョンはRailway.appに最適化されています。

## ✨ 特徴

- ✅ 完全無料で使える
- ✅ 自動でURL発行
- ✅ データベース永続化
- ✅ SSL対応（HTTPS）
- ✅ デモモード搭載

## 📦 デプロイ手順

### ステップ1: GitHubにアップロード

1. **GitHubアカウントを作成**（まだの方）
   - https://github.com/ にアクセス
   - Sign upをクリック
   - メールアドレスで登録（無料）

2. **新しいリポジトリを作成**
   - GitHubにログイン
   - 右上の「+」→「New repository」
   - Repository name: `form-sales-system`
   - Public を選択
   - 「Create repository」をクリック

3. **ファイルをアップロード**
   - 「uploading an existing file」をクリック
   - このフォルダ内の全ファイルをドラッグ&ドロップ
   - 「Commit changes」をクリック

### ステップ2: Railwayでデプロイ

1. **Railwayにアクセス**
   - https://railway.app/ を開く
   - 「Start a New Project」をクリック
   - 「Login with GitHub」でログイン

2. **プロジェクトを作成**
   - 「Deploy from GitHub repo」を選択
   - 先ほど作成した `form-sales-system` を選択
   - 「Deploy Now」をクリック

3. **デプロイ完了を待つ**
   - 自動でデプロイが開始されます
   - 1〜3分待ちます
   - 「Success」と表示されたら完了！

4. **URLを取得**
   - 「Settings」タブをクリック
   - 「Generate Domain」をクリック
   - 表示されたURLをコピー

### ステップ3: アクセス

発行されたURLにアクセスすれば、すぐに使えます！

例: `https://form-sales-system-production.up.railway.app`

---

## 🎯 使い方

### 1. 基本設定
- 「基本設定」タブで営業文面を登録

### 2. クロール（デモ）
- 「クロール」タブでキーワードを入力
- 「デモデータを生成」をクリック

### 3. 自動送信（デモ）
- 「自動送信」タブで設定を選択
- 「デモ送信開始」をクリック

### 4. 結果確認
- 「結果管理」タブで確認
- CSVエクスポート可能

---

## ⚠️ 注意事項

### デモモードについて
このRailway版は**デモモード**で動作します：
- ✅ UI/UXの確認
- ✅ データベース機能
- ✅ 統計表示
- ❌ 実際のWebクロール
- ❌ 実際のフォーム送信

### 理由
Railwayの無料枠では以下の制限があります：
- Playwrightブラウザの実行が困難
- リソース制限
- 長時間実行の制限

### 本番運用したい場合
実際のクロール・送信機能が必要な場合は、VPS版をご検討ください。

---

## 🔧 トラブルシューティング

### デプロイが失敗する
- GitHubにすべてのファイルがアップロードされているか確認
- Railwayのログを確認

### URLにアクセスできない
- 「Generate Domain」をクリックしたか確認
- 数分待ってから再度アクセス

### アプリが動かない
- Railwayのログを確認
- 「Redeploy」をクリックして再デプロイ

---

## 📊 含まれるファイル

```
form_sales_railway/
├── app.py              # メインアプリケーション
├── requirements.txt    # Python依存パッケージ
├── Procfile           # Railway起動設定
├── runtime.txt        # Pythonバージョン指定
├── railway.json       # Railway設定
├── templates/
│   └── index.html     # WebUI
└── README.md          # このファイル
```

---

## 🎉 完了！

これでインターネット上で動くメールフォーム営業システムが完成です！

発行されたURLを共有すれば、誰でもアクセスできます。

---

## 📞 サポート

問題があれば、Railwayのドキュメントを参照：
https://docs.railway.app/

---

**Happy Automation! 🚀**
