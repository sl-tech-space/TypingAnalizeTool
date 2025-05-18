import polars as pl
from pathlib import Path
from utils.config import (
    DIFFICULTY_NAMES,
    LANGUAGE_NAMES,
)


def load_data():
    """
    タイピングデータを読み込む

    Returns:
        tuple: (scores, misses) スコアデータとミスタイプデータのタプル
    """
    # プロジェクトのルートディレクトリを取得
    root_dir = Path(__file__).parent.parent

    # スコアデータの読み込み
    scores = pl.read_csv(root_dir / "t_score.csv", try_parse_dates=True)

    # ミスタイプデータの読み込み
    misses = pl.read_csv(root_dir / "t_miss.csv", try_parse_dates=True)

    # ユーザーデータの読み込み
    users = pl.read_csv(root_dir / "m_user.csv", try_parse_dates=True)

    # 必要なカラムのみを選択
    scores = scores.select(
        [
            "user_id",
            "diff_id",
            "lang_id",
            "score",
            "accuracy",
            "typing_count",
            "created_at",
        ]
    )

    misses = misses.select(["user_id", "miss_char", "miss_count", "created_at"])

    users = users.select(["user_id", "username", "created_at"])

    # ユーザー情報を結合
    scores = scores.join(
        users.select(["user_id", "username"]), on="user_id", how="left"
    )
    misses = misses.join(
        users.select(["user_id", "username"]), on="user_id", how="left"
    )

    # 難易度と言語の名称を追加
    scores = scores.with_columns(
        [
            pl.col("diff_id").map_dict(DIFFICULTY_NAMES).alias("difficulty"),
            pl.col("lang_id").map_dict(LANGUAGE_NAMES).alias("language"),
        ]
    )

    return scores, misses
