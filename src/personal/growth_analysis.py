import streamlit as st
import polars as pl
import plotly.graph_objects as go


def show_growth_analysis(user_scores: pl.DataFrame):
    """成長率分析を表示"""
    with st.container():
        # 言語と難易度の組み合わせを生成
        mode_combinations = [
            (lang_id, diff_id)
            for lang_id in [1, 2]  # 日本語、英語
            for diff_id in [1, 2, 3]  # 初級、中級、上級
        ]

        # モード名のマッピング
        lang_names = {1: "日本語", 2: "英語"}
        diff_names = {1: "イージー", 2: "ノーマル", 3: "ハード"}

        # 3×2のグリッドレイアウトを作成
        for i in range(0, len(mode_combinations), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(mode_combinations):
                    lang_id, diff_id = mode_combinations[i + j]
                    mode_scores = user_scores.filter(
                        (pl.col("lang_id") == lang_id) & (pl.col("diff_id") == diff_id)
                    )
                    mode_name = f"{lang_names[lang_id]} - {diff_names[diff_id]}"

                    with cols[j]:
                        if len(mode_scores) > 0:
                            # 日付でソート
                            sorted_scores = mode_scores.sort("created_at")

                            # 初回スコアと最高スコアを取得
                            first_score = sorted_scores["score"].head(1).item()
                            max_score = sorted_scores["score"].max()
                            play_count = len(mode_scores)

                            # 成長率を計算
                            growth_rate = (
                                (max_score - first_score) / first_score * 100
                                if first_score != 0
                                else 0
                            )

                            st.markdown(
                                f"""
                                <div class="growth-container">
                                    <div class="mode-title">{mode_name}</div>
                                    <div class="mode-stats">
                                        <div class="stat-item">
                                            <div class="stat-label">初回スコア</div>
                                            <div class="stat-value">{first_score:,}点</div>
                                        </div>
                                        <div class="stat-item">
                                            <div class="stat-label">最高スコア</div>
                                            <div class="stat-value">{max_score:,}点</div>
                                        </div>
                                        <div class="stat-item">
                                            <div class="stat-label">プレイ回数</div>
                                            <div class="stat-value">{play_count}回</div>
                                        </div>
                                        <div class="stat-item">
                                            <div class="stat-label">成長率</div>
                                            <div class="stat-value {("growth-positive" if growth_rate >= 0 else "growth-negative")}">
                                                {growth_rate:+.1f}%
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            # スコア推移チャートを表示
                            fig = create_score_trend_chart(sorted_scores, mode_name)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.markdown(
                                f"""
                                <div class="growth-container">
                                    <div class="mode-title">{mode_name}</div>
                                    <div style="text-align: center; padding: 20px; color: rgba(255, 255, 255, 0.5);">
                                        データがありません
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )


def create_score_trend_chart(scores, mode_name):
    """スコア推移グラフを作成"""
    fig = go.Figure()

    # プレイ回数のインデックスを作成
    play_counts = list(range(1, len(scores) + 1))

    # 実際のスコアの折れ線グラフ
    fig.add_trace(
        go.Scatter(
            x=play_counts,
            y=scores["score"],
            mode="lines+markers",
            line=dict(color="#4CAF50", width=2),
            marker=dict(size=6, color="#4CAF50", line=dict(width=1, color="#FFFFFF")),
            name="スコア",
        )
    )

    # レイアウトの設定
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=11, color="white"),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.2)",
            gridwidth=1,
            tickfont=dict(color="white"),
            tickmode="linear",
            tick0=1,
            dtick=1,
            title=dict(text="プレイ回数", font=dict(color="white")),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.2)",
            gridwidth=1,
            tickfont=dict(color="white"),
            title=dict(text="スコア", font=dict(color="white")),
        ),
        paper_bgcolor="black",
        plot_bgcolor="black",
        showlegend=False,
    )

    return fig
