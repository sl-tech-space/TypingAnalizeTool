import streamlit as st
import polars as pl
from utils.charts.bar_chart import create_bar_chart


def show_average_score(scores: pl.DataFrame, users: list[str]):
    """平均スコアを表示"""
    # ユーザーごとの平均スコアを計算
    avg_scores = (
        scores.group_by("username")
        .agg(pl.col("score").mean().alias("average_score"))
        .sort("average_score", descending=True)
    )

    # チャートを表示
    fig = create_bar_chart(
        avg_scores.rename({"average_score": "score"}), "username", "score"
    )
    st.plotly_chart(fig, use_container_width=True)


def show_average_score_details(scores: pl.DataFrame, users: list[str]):
    """平均スコアの詳細情報を表示"""
    if len(users) > 0:
        # ユーザーごとの平均スコアを計算
        user_avg_scores = []
        for username in users:
            user_scores = scores.filter(pl.col("username") == username)
            if len(user_scores) > 0:
                avg_score = user_scores["score"].mean()
                user_avg_scores.append({"username": username, "avg_score": avg_score})

        if user_avg_scores:
            # 平均スコアでソート
            user_avg_df = pl.DataFrame(user_avg_scores).sort(
                "avg_score", descending=True
            )

            # ランキングを表示
            for i, row in enumerate(user_avg_df.head(5).iter_rows(named=True), 1):
                rank_class = f"rank-{i}" if i <= 3 else "rank-other"
                rank_text = f"{i}位"
                st.markdown(
                    f'<div class="ranking-text {rank_class}"><span class="rank-number">{rank_text}</span> {row["username"]} <span class="rank-score">{row["avg_score"]:,.0f}点</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("スコアデータがありません")
    else:
        st.info("ユーザーデータがありません")
