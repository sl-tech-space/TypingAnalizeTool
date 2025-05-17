import streamlit as st
import polars as pl


def show_overall_summary(scores, misses=None):
    """全体サマリーを表示"""
    overall_metrics = calculate_overall_metrics(scores, misses)

    # すべてのサマリーアイテムを1つのHTMLブロックとして構築
    summary_items = [
        f"""
        <div class="summary-item">
            <div class="summary-label">総プレイ回数</div>
            <div class="summary-value">{overall_metrics["total_plays"]:,}<span class="summary-unit">回</span></div>
        </div>
        """,
        f"""
        <div class="summary-item">
            <div class="summary-label">全体平均スコア</div>
            <div class="summary-value">{overall_metrics["average_score"]:.1f}</div>
        </div>
        """,
        f"""
        <div class="summary-item">
            <div class="summary-label">全体平均正確度</div>
            <div class="summary-value">{overall_metrics["average_accuracy"] * 100:.1f}<span class="summary-unit">%</span></div>
        </div>
        """,
        f"""
        <div class="summary-item">
            <div class="summary-label">全体平均タイピング数</div>
            <div class="summary-value">{overall_metrics["average_typing_count"]:.1f}<span class="summary-unit">回</span></div>
        </div>
        """,
    ]

    # 総ミスタイプ数（存在する場合）
    if misses is not None:
        summary_items.append(
            f"""
        <div class="summary-item">
            <div class="summary-label">総ミスタイプ数</div>
            <div class="summary-value">{overall_metrics["total_misses"]:,}<span class="summary-unit">回</span></div>
        </div>
        """
        )

    # すべてのアイテムを1つのHTMLブロックとして表示
    st.markdown(
        f"""
        <div class="summary-container">
            {"".join(summary_items)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def calculate_overall_metrics(
    scores: pl.DataFrame, misses: pl.DataFrame = None
) -> dict:
    """全体メトリクスを計算"""
    metrics = {
        "total_plays": scores.height,
        "average_score": scores["score"].mean(),
        "average_accuracy": scores["accuracy"].mean(),
        "average_typing_count": scores["typing_count"].mean(),
    }

    if misses is not None:
        metrics["total_misses"] = misses["miss_count"].sum()

    return metrics
