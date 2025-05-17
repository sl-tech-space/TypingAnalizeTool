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

        # 成長率データを収集
        growth_data = []
        for lang_id, diff_id in mode_combinations:
            # 該当するモードのスコアを抽出
            mode_scores = user_scores.filter(
                (pl.col("lang_id") == lang_id) & (pl.col("diff_id") == diff_id)
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

                # モード名を生成
                mode_name = f"{lang_names[lang_id]} - {diff_names[diff_id]}"

                growth_data.append(
                    {
                        "mode_name": mode_name,
                        "first_score": first_score,
                        "max_score": max_score,
                        "growth_rate": growth_rate,
                        "play_count": len(mode_scores),
                    }
                )

        if growth_data:
            # カスタムCSSを適用
            st.markdown(
                """
                <style>
                .mode-title { 
                    font-size: 24px;
                    margin: 10px 0;
                    line-height: 1.3;
                    font-weight: 500;
                    color: #FFFFFF;
                }
                .mode-stats { 
                    font-size: 20px;
                    margin: 5px 0;
                    line-height: 1.3;
                }
                .growth-positive { color: #4CAF50; }
                .growth-negative { color: #FF6B6B; }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # 3×2のグリッドレイアウトを作成
            cols = st.columns(3)
            for i, data in enumerate(growth_data):
                col_idx = i % 3
                with cols[col_idx]:
                    # モード名を表示
                    st.markdown(
                        f'<div class="mode-title">{data["mode_name"]}</div>',
                        unsafe_allow_html=True,
                    )

                    # スコアと成長率を表示
                    growth_color = (
                        "growth-positive"
                        if data["growth_rate"] >= 0
                        else "growth-negative"
                    )
                    st.markdown(
                        f"""
                        <div class="mode-stats">
                        初回スコア: {data["first_score"]:,}点<br>
                        最高スコア: {data["max_score"]:,}点<br>
                        成長率: <span class="{growth_color}">{data["growth_rate"]:+.1f}%</span><br>
                        プレイ回数: {data["play_count"]}回
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # 成長率チャートを表示
                    fig = create_growth_comparison_chart(
                        pl.DataFrame([data]),
                        "mode_name",
                        "first_score",
                        "max_score",
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("スコアデータがありません")


def create_growth_comparison_chart(
    df: pl.DataFrame, mode_col: str, first_score_col: str, max_score_col: str
):
    """成長率比較グラフを作成"""
    fig = go.Figure()

    # 各モードごとに2本の棒を表示
    for i, row in enumerate(df.iter_rows(named=True)):
        # 初回スコアの棒
        fig.add_trace(
            go.Bar(
                x=[row[mode_col]],
                y=[row[first_score_col]],
                name="初回スコア",
                marker_color="#4CAF50",
                width=0.4,
                showlegend=False,
            )
        )

        # 最高スコアの棒
        fig.add_trace(
            go.Bar(
                x=[row[mode_col]],
                y=[row[max_score_col]],
                name="最高スコア",
                marker_color="#2196F3",
                width=0.4,
                showlegend=False,
            )
        )

        # 成長率をテキストで表示
        growth_rate = (
            (row[max_score_col] - row[first_score_col]) / row[first_score_col] * 100
            if row[first_score_col] != 0
            else 0
        )
        color = "green" if growth_rate >= 0 else "red"
        fig.add_annotation(
            x=row[mode_col],
            y=max(row[max_score_col], row[first_score_col]),
            text=f"{growth_rate:+.1f}%",
            showarrow=False,
            font=dict(color=color, size=12),
            yshift=10,
        )

    # レイアウトの設定
    fig.update_layout(
        height=200,  # 高さを調整
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=11, color="white"),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color="white"),
            tickangle=0,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.2)",
            gridwidth=1,
            tickfont=dict(color="white"),
            title="スコア",
            titlefont=dict(color="white"),
        ),
        paper_bgcolor="black",
        plot_bgcolor="black",
        showlegend=False,
        bargap=0.3,
        bargroupgap=0.3,
        barmode="group",
    )

    return fig
