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
        st.info("ミスタイプデータがありません")


def show_personal_miss_details(user_misses: pl.DataFrame, username: str):
    """個人ミスタイプ分析の詳細情報を表示"""
    # ミスタイプを分析
    miss_chars = analyze_misses(user_misses)

    if len(miss_chars) > 0:
        # 詳細情報を表示
        total_misses = miss_chars["miss_count"].sum()
        top_miss = miss_chars.row(0, named=True)
        top10_percentage = miss_chars.head(10)["miss_count"].sum() / total_misses * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総ミスタイプ数", f"{total_misses:,}回")
        with col2:
            st.metric(
                "最多ミスタイプ", f"{top_miss['char']}", f"{top_miss['miss_count']:,}回"
            )
        with col3:
            st.metric("上位10件の割合", f"{top10_percentage:.1f}%")
    else:
        st.info("ミスタイプデータがありません")


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
