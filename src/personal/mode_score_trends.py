import streamlit as st
import polars as pl
import plotly.graph_objects as go


def show_personal_mode_score_trends(user_scores: pl.DataFrame):
    """モード別スコア推移を表示"""
    with st.container():
        # 言語と難易度の組み合わせを生成
        mode_combinations = [
            (lang_id, diff_id)
            for lang_id in user_scores["lang_id"].unique()
            for diff_id in user_scores["diff_id"].unique()
        ]

        # モード名のマッピング
        lang_names = {1: "日本語", 2: "英語"}
        diff_names = {1: "イージー", 2: "ノーマル", 3: "ハード"}

        # 3×2のグリッドを作成
        cols = st.columns(3)
        for i, (lang_id, diff_id) in enumerate(mode_combinations):
            mode_scores = user_scores.filter(
                (pl.col("lang_id") == lang_id) & (pl.col("diff_id") == diff_id)
            )
            if len(mode_scores) > 0:
                # モード名を生成
                mode_name = f"{lang_names[lang_id]} - {diff_names[diff_id]}"

                # モード別メトリクスを計算
                mode_metrics = calculate_mode_metrics(mode_scores)

                # スコア推移チャートを表示（2行3列のグリッド）
                with cols[i % 3]:
                    st.subheader(mode_name)
                    fig = create_score_trend_chart(mode_metrics["scores"], mode_name)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # データがない場合は空のメッセージを表示
                with cols[i % 3]:
                    st.subheader(f"{lang_names[lang_id]} - {diff_names[diff_id]}")
                    st.info("データがありません")


def create_score_trend_chart(scores, future_dates=None, future_scores=None):
    """スコア推移グラフを作成"""
    fig = go.Figure()

    # プレイ回数のインデックスを作成
    play_counts = list(range(1, len(scores) + 1))

    # 実際のスコアの折れ線グラフ
    fig.add_trace(
        go.Scatter(
            x=play_counts,
            y=scores["score"],
            mode="lines",
            line=dict(color="#4CAF50", width=2),
        )
    )

    # 予測スコアの折れ線グラフ（存在する場合）
    if future_dates is not None and future_scores is not None:
        future_play_counts = list(
            range(len(scores) + 1, len(scores) + len(future_scores) + 1)
        )
        fig.add_trace(
            go.Scatter(
                x=future_play_counts,
                y=future_scores,
                mode="lines",
                name="予測スコア",
                line=dict(color="#FF5252", width=2, dash="dot"),
            )
        )

    # レイアウトの設定
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(size=11, color="white"),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.2)",
            gridwidth=1,
            tickfont=dict(color="white"),
            tickmode="linear",  # 線形の目盛り
            tick0=1,  # 最初の目盛り
            dtick=1,  # 目盛りの間隔
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.2)",
            gridwidth=1,
            tickfont=dict(color="white"),
        ),
        paper_bgcolor="black",
        plot_bgcolor="black",
        showlegend=False,
    )

    return fig


def calculate_mode_metrics(mode_scores: pl.DataFrame) -> dict:
    """モード別メトリクスを計算

    Args:
        mode_scores (pl.DataFrame): モード別スコアデータ

    Returns:
        dict: モード別メトリクス
    """
    return {
        "average_score": mode_scores["score"].mean(),
        "max_score": mode_scores["score"].max(),
        "play_count": mode_scores.height,
        "scores": mode_scores.sort("created_at"),
    }
