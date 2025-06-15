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
        tuple: (scores, misses, users) スコアデータ、ミスタイプデータ、ユーザーデータのタプル
    """
    # データディレクトリのパスを取得
    data_dir = Path(__file__).parent / "data"

    # スコアデータの読み込み
    scores = pl.read_csv(data_dir / "t_score.csv", try_parse_dates=True)

    # ミスタイプデータの読み込み
    misses = pl.read_csv(data_dir / "t_miss.csv", try_parse_dates=True)

    # ユーザーデータの読み込み
    users = pl.read_csv(data_dir / "m_user.csv", try_parse_dates=True)

    # 新卒ユーザーのみをフィルタリング
    new_graduate_users = users.filter(pl.col("is_newgraduate") == 1)
    new_graduate_user_ids = new_graduate_users.select("user_id").to_series().to_list()

    # スコアとミスデータを新卒ユーザーのみにフィルタリングし、スコアが500以下のデータを除外
    scores = scores.filter(
        (pl.col("user_id").is_in(new_graduate_user_ids)) & (pl.col("score") > 500)
    )
    misses = misses.filter(pl.col("user_id").is_in(new_graduate_user_ids))

    # 必要なカラムのみを選択
    scores = scores.select(
        [
            "user_id",
            "score",
            "accuracy",
            "typing_count",
            "created_at",
            "updated_at",
            "diff_id",
            "lang_id",
        ]
    )

    misses = misses.select(
        [
            "user_id",
            "miss_char",
            "miss_count",
            "created_at",
            "updated_at",
        ]
    )

    users = users.select(
        [
            "user_id",
            "username",
            "email",
            "date_joined",
            "created_at",
            "updated_at",
            "is_newgraduate",
        ]
    )

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

    return scores, misses, users
