# タイピング分析ダッシュボード

タイピング練習のデータを分析し、可視化するダッシュボードアプリケーションです。

## 機能

### 全体分析
- 全体の統計情報の表示
- ユーザー別比較
- モード別比較
- ミスタイプ傾向
- 成長率ランキング

### 個人分析
- スコア推移
- 成長率分析
- ミスタイプ分析
- 個人サマリー

### 時間帯分析
- 時間帯別スコア分析
- 曜日×時間帯別スコア分析

### 難易度と言語の組み合わせ分析
- 平均スコア分析
- 正確性分析

## 技術スタック

- Python 3.11+
- Streamlit
- Polars
- Plotly
- Docker

## セットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/typing-analysis-dashboard.git
cd typing-analysis-dashboard
```

2. Dockerコンテナのビルドと起動
```bash
docker-compose up --build
```

3. アプリケーションにアクセス
ブラウザで http://localhost:8501 にアクセスしてください。

## 開発

### コードフォーマット

```bash
ruff format .
```


## プロジェクト構造

```
typing-analysis-dashboard/
├── src/
│   ├── __init__.py
│   ├── main.py          # メインアプリケーション
│   ├── loader.py        # データローダー
│   ├── data_science/    # データ分析モジュール
│   │   ├── __init__.py
│   │   ├── time_score_analysis.py      # 時間帯別スコア分析
│   │   ├── time_accuracy_analysis.py   # 曜日×時間帯別スコア分析
│   │   ├── difficulty_language_score_analysis.py    # 難易度と言語の組み合わせによる平均スコア分析
│   │   └── difficulty_language_accuracy_analysis.py # 難易度と言語の組み合わせによる正確性分析
│   ├── personal/        # 個人分析モジュール
│   │   ├── __init__.py
│   │   ├── personal_summary.py    # 個人サマリー
│   │   ├── personal_miss.py       # 個人ミスタイプ分析
│   │   └── growth_analysis.py     # 成長率分析
│   ├── overall/         # 全体分析モジュール
│   │   ├── __init__.py
│   │   ├── overall_summary.py     # 全体サマリー
│   │   ├── overall_miss.py        # 全体ミスタイプ分析
│   │   ├── average_score.py       # 平均スコア分析
│   │   └── growth_ranking.py      # 成長率ランキング
│   ├── utils/           # ユーティリティモジュール
│   │   ├── __init__.py
│   │   ├── config.py    # 設定ファイル
│   │   └── charts/      # チャート関連のユーティリティ
│   └── static/          # 静的ファイル
├── data/               # データファイル
├── tests/              # テストコード
├── requirements.txt    # 依存関係
├── Dockerfile         # Docker設定
├── docker-compose.yml # Docker Compose設定
├── .gitignore        # Git除外設定
└── README.md         # プロジェクト説明
```

## ライセンス

MIT License 