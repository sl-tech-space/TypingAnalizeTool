import streamlit as st
import polars as pl
from utils.charts.bar_chart import create_bar_chart


def show_personal_miss_chart(user_misses: pl.DataFrame, username: str):
    """個人ミスタイプ分析のグラフを表示"""
    # ミスタイプを分析
    miss_chars = analyze_misses(user_misses)

    if len(miss_chars) > 0:
        # チャートを表示
        fig = create_bar_chart(
            miss_chars.rename({"char": "miss_type", "miss_count": "count"}),
            "miss_type",
            "count",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(
            """
            <div class="ranking-text">
                <span class="rank-number">-</span>
                ミスタイプデータがありません
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_personal_miss_details(user_misses: pl.DataFrame, username: str):
    """個人ミスタイプ分析の詳細情報を表示"""
    # ミスタイプを分析
    miss_chars = analyze_misses(user_misses)

    if len(miss_chars) > 0:
        # 上位5件のミスタイプを表示
        for i, row in enumerate(miss_chars.head(5).iter_rows(named=True), 1):
            rank_class = f"rank-{i}" if i <= 3 else "rank-other"
            rank_text = f"{i}位"
            st.markdown(
                f'<div class="ranking-text {rank_class}"><span class="rank-number">{rank_text}</span> {row["char"]} <span class="rank-score">{row["miss_count"]:,}回</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="ranking-text">
                <span class="rank-number">-</span>
                ミスタイプデータがありません
            </div>
            """,
            unsafe_allow_html=True,
        )


def analyze_misses(misses: pl.DataFrame) -> pl.DataFrame:
    """ミスタイプを分析"""
    # 文字ごとのミスタイプ回数を集計
    miss_chars = (
        misses.group_by("miss_char")
        .agg(pl.col("miss_count").sum())
        .sort("miss_count", descending=True)
    )

    # インデックスを文字に設定
    miss_chars = miss_chars.with_columns(pl.col("miss_char").alias("char")).drop(
        "miss_char"
    )

    return miss_chars
