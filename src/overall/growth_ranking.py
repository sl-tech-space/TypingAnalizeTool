import streamlit as st
import polars as pl
from utils.charts.bar_chart import create_bar_chart


def show_growth_ranking(growth_df: pl.DataFrame):
    """成長率ランキングを表示"""
    # グラフ表示
    st.plotly_chart(
        create_bar_chart(
            growth_df,
            x_col="username",
            y_col="total_growth_rate",
            title="成長率ランキング",
        ),
        use_container_width=True,
    )


def show_growth_ranking_details(scores: pl.DataFrame, users: pl.DataFrame):
    """成長率ランキングの詳細情報を表示"""
    # ユーザー一覧を取得
    user_list = users.select("username").unique().to_series().to_list()

    if len(user_list) > 0:
        # ユーザーごとの成長率を計算
        user_growth = []
        for username in user_list:
            user_scores = scores.filter(pl.col("username") == username)
            if len(user_scores) > 0:
                # 各難易度・言語の成長率を計算
                mode_growth_rates = []
                for lang_id in [1, 2]:  # 日本語、英語
                    for diff_id in [1, 2, 3]:  # 初級、中級、上級
                        mode_scores = user_scores.filter(
                            (pl.col("lang_id") == lang_id)
                            & (pl.col("diff_id") == diff_id)
                        )
                        if len(mode_scores) > 0:
                            # 日付でソート
                            sorted_scores = mode_scores.sort("created_at")
                            # 初回スコアと最高スコアを取得
                            first_score = sorted_scores["score"].head(1).item()
                            max_score = sorted_scores["score"].max()
                            # 成長率を計算
                            growth_rate = (
                                (max_score - first_score) / first_score * 100
                                if first_score != 0
                                else 0
                            )
                            mode_growth_rates.append(growth_rate)

                # 全モードの成長率の合計を計算
                total_growth_rate = sum(mode_growth_rates)
                user_growth.append(
                    {"username": username, "growth_rate": total_growth_rate}
                )

        if user_growth:
            # 成長率でソート
            user_growth_df = pl.DataFrame(user_growth).sort(
                "growth_rate", descending=True
            )

            # ランキングを表示
            for i, row in enumerate(user_growth_df.head(5).iter_rows(named=True), 1):
                rank_class = f"rank-{i}" if i <= 3 else "rank-other"
                rank_text = f"{i}位"
                st.markdown(
                    f'<div class="ranking-text {rank_class}"><span class="rank-number">{rank_text}</span> {row["username"]} <span class="rank-score">{row["growth_rate"]:+.1f}%</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("成長率データがありません")
    else:
        st.info("ユーザーデータがありません")


def calculate_growth_ranking(scores: pl.DataFrame) -> pl.DataFrame:
    """成長率ランキングを計算"""
    # 言語と難易度の組み合わせごとに成長率を計算
    growth_rates = []
    for lang_id in [1, 2]:  # 日本語、英語
        for diff_id in [1, 2, 3]:  # 初級、中級、上級
            # 該当するモードのスコアを抽出
            mode_scores = scores.filter(
                (pl.col("lang_id") == lang_id) & (pl.col("diff_id") == diff_id)
            )

            if len(mode_scores) > 0:
                # ユーザーごとの最初と最後のスコアを取得
                first_scores = (
                    mode_scores.sort("created_at")
                    .group_by("username")
                    .agg(pl.col("score").first())
                    .rename({"score": "first_score"})
                )
                last_scores = (
                    mode_scores.sort("created_at")
                    .group_by("username")
                    .agg(pl.col("score").last())
                    .rename({"score": "last_score"})
                )

                # 成長率を計算
                mode_growth = first_scores.join(
                    last_scores, on="username"
                ).with_columns(
                    [
                        pl.lit(lang_id).alias("lang_id"),
                        pl.lit(diff_id).alias("diff_id"),
                        (
                            (pl.col("last_score") - pl.col("first_score"))
                            / pl.col("first_score")
                            * 100
                        ).alias("growth_rate"),
                    ]
                )
                growth_rates.append(mode_growth)

    if not growth_rates:
        return pl.DataFrame({"username": [], "total_growth_rate": []})

    # 全モードの成長率を結合
    all_growth_rates = pl.concat(growth_rates)

    # ユーザーごとに成長率の合計を計算
    total_growth = (
        all_growth_rates.group_by("username")
        .agg(
            [
                pl.col("first_score").first(),
                pl.col("last_score").last(),
                pl.col("growth_rate").sum().alias("total_growth_rate"),
            ]
        )
        .sort("total_growth_rate", descending=True)
    )

    return total_growth
