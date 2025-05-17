# タイピング分析ダッシュボード

タイピング練習のデータを分析し、可視化するダッシュボードアプリケーションです。

## 機能

- 全体の統計情報の表示
- ユーザー別の分析
  - スコア推移
  - 成長率分析
  - ミスタイプ分析
- モード別の分析
  - スコア推移
  - プレイ回数
- 全体分析
  - ユーザー別比較
  - モード別比較
  - ミスタイプ傾向

## 技術スタック

- Python 3.11+
- Streamlit
- Polars
- Matplotlib
- Seaborn

## セットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/typing-analysis-dashboard.git
cd typing-analysis-dashboard
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
venv\Scripts\activate     # Windowsの場合
```

3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

4. アプリケーションの起動
```bash
streamlit run app/main.py
```

## 開発

### 開発環境のセットアップ

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

### テストの実行

```bash
pytest
```

### コードフォーマット

```bash
ruff format .
```

### 型チェック

```bash
mypy .
```

## プロジェクト構造

```
typing-analysis-dashboard/
├── app/
│   ├── __init__.py
│   ├── main.py          # メインアプリケーション
│   └── pages/           # マルチページアプリケーション用
├── src/
│   ├── __init__.py
│   ├── analysis/        # 分析ロジック
│   ├── data/           # データ処理
│   ├── visualization/  # 可視化
│   └── config/         # 設定
├── tests/              # テストコード
├── data/              # データファイル
├── docs/              # ドキュメント
├── scripts/           # ユーティリティスクリプト
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── README.md
└── Dockerfile
```

## ライセンス

MIT License 