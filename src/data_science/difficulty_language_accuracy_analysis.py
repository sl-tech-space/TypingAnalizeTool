import streamlit as st
import polars as pl
import plotly.graph_objects as go


def show_difficulty_language_accuracy_analysis(scores: pl.DataFrame):
    """難易度と言語の組み合わせによる正確性分析を表示"""
    if len(scores) == 0:
        st.info("スコアデータがありません")
        return

    fig = create_difficulty_language_accuracy_heatmap(scores)
    st.plotly_chart(fig, use_container_width=True)


def create_difficulty_language_accuracy_heatmap(scores: pl.DataFrame) -> go.Figure:
    """難易度と言語の組み合わせによる正確性のヒートマップを作成"""
    # 難易度と言語の組み合わせでグループ化して平均正確性を計算
    grouped = (
        scores.group_by(["difficulty", "language"])
        .agg(pl.col("accuracy").mean().alias("average_accuracy"))
        .sort(["difficulty", "language"])
    )

    # ヒートマップ用のデータを整形
    # 難易度の順序を指定
    difficulties = ["イージー", "ノーマル", "ハード"]
    languages = grouped["language"].unique().to_list()
    z_data = []

    for diff in difficulties:
        row = []
        for lang in languages:
            filtered_data = grouped.filter(
                (pl.col("difficulty") == diff) & (pl.col("language") == lang)
            )
            # データが存在する場合はその値を、存在しない場合は0を使用
            accuracy = (
                filtered_data["average_accuracy"].item()
                if len(filtered_data) > 0
                else 0
            )
            row.append(accuracy)
        z_data.append(row)

    # ヒートマップの作成
    fig = go.Figure(
        data=go.Heatmap(
            z=z_data,
            x=languages,
            y=difficulties,
            colorscale="Viridis",
            text=[[f"{acc:.2%}" if acc > 0 else "-" for acc in row] for row in z_data],
            texttemplate="%{text}",
            textfont={"size": 14},
        )
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
    )

    return fig
