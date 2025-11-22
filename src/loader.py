import polars as pl
import os
import psycopg2
from pathlib import Path
from utils.config import (
    DIFFICULTY_NAMES,
    LANGUAGE_NAMES,
)


def get_db_connection():
    """
    データベース接続を取得する

    Returns:
        psycopg2.connection: データベース接続オブジェクト
    """
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
    )


def load_data():
    """
    タイピングデータをデータベースから読み込む

    Returns:
        tuple: (scores, misses, users) スコアデータ、ミスタイプデータ、ユーザーデータのタプル
    """
    try:
        # データベース接続
        conn = get_db_connection()

        # スコアデータの読み込み
        scores_query = """
        SELECT 
            s.user_id,
            s.score,
            s.accuracy,
            s.typing_count,
            s.created_at,
            s.updated_at,
            s.diff_id,
            s.lang_id,
            d.diff as difficulty,
            l.lang as language
        FROM t_score s
        LEFT JOIN m_diff d ON s.diff_id = d.diff_id
        LEFT JOIN m_lang l ON s.lang_id = l.lang_id
        """
        scores = pl.read_database(scores_query, conn)

        # ミスタイプデータの読み込み
        misses_query = """
        SELECT 
            user_id,
            miss_char,
            miss_count,
            created_at,
            updated_at
        FROM t_miss
        """
        misses = pl.read_database(misses_query, conn)

        # ユーザーデータの読み込み
        users_query = """
        SELECT 
            user_id,
            username,
            email,
            date_joined,
            created_at,
            updated_at,
            is_newgraduate
        FROM m_user
        """
        users = pl.read_database(users_query, conn)

        # 接続を閉じる
        conn.close()

        # 新卒ユーザーのみをフィルタリング
        new_graduate_users = users.filter(pl.col("is_newgraduate") == 1)
        new_graduate_user_ids = (
            new_graduate_users.select("user_id").to_series().to_list()
        )

        # スコアとミスデータを新卒ユーザーのみにフィルタリングし、スコアが500以下のデータを除外
        scores = scores.filter(
            (pl.col("user_id").is_in(new_graduate_user_ids)) & (pl.col("score") > 500)
        )
        misses = misses.filter(pl.col("user_id").is_in(new_graduate_user_ids))

        # ユーザー情報を結合
        scores = scores.join(
            users.select(["user_id", "username"]), on="user_id", how="left"
        )
        misses = misses.join(
            users.select(["user_id", "username"]), on="user_id", how="left"
        )

        return scores, misses, users

    except Exception as e:
        print(f"データベース接続エラー: {str(e)}")
        # エラーが発生した場合は空のデータフレームを返す
        return pl.DataFrame(), pl.DataFrame(), pl.DataFrame()
