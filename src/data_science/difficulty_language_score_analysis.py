import streamlit as st
import polars as pl
import plotly.graph_objects as go


def show_difficulty_language_score_analysis(scores: pl.DataFrame):
    """難易度と言語の組み合わせによる平均スコアの分析を表示"""
    if len(scores) == 0:
        st.info("スコアデータがありません")
        return

    fig = create_difficulty_language_heatmap(scores)
    st.plotly_chart(fig, use_container_width=True)


def create_difficulty_language_heatmap(scores: pl.DataFrame) -> go.Figure:
    """難易度と言語の組み合わせによる平均スコアのヒートマップを作成"""
    # 難易度と言語の組み合わせでグループ化して平均スコアを計算
    grouped = (
        scores.group_by(["difficulty", "language"])
        .agg(pl.col("score").mean().alias("average_score"))
        .sort(["difficulty", "language"])
    )

    # ヒートマップ用のデータを整形
    # 難易度の順序を指定（イージーからハードへ）
    difficulties = ["イージー", "ノーマル", "ハード"]
    # 言語の順序を指定（日本語から英語へ）
    languages = ["日本語", "英語"]
    z_data = []

    for diff in difficulties:
        row = []
        for lang in languages:
            filtered_data = grouped.filter(
                (pl.col("difficulty") == diff) & (pl.col("language") == lang)
            )
            # データが存在する場合はその値を、存在しない場合は0を使用
            score = (
                filtered_data["average_score"].item() if len(filtered_data) > 0 else 0
            )
            row.append(score)
        z_data.append(row)

    # ヒートマップの作成
    fig = go.Figure(
        data=go.Heatmap(
            z=z_data,
            x=languages,
            y=difficulties,
            colorscale="Viridis",
            text=[
                [f"{score:.0f}" if score > 0 else "-" for score in row]
                for row in z_data
            ],
            texttemplate="%{text}",
            textfont={"size": 14},
        )
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
    )

    return fig
