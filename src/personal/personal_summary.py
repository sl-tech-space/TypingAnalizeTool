import streamlit as st
import polars as pl


def show_personal_summary(user_scores, user_misses):
    """ユーザーサマリーを表示"""
    user_metrics = calculate_user_metrics(user_scores, user_misses)

    # すべてのサマリーアイテムを1つのHTMLブロックとして構築
    summary_items = [
        f"""
        <div class="summary-item">
            <div class="summary-label">総プレイ回数</div>
            <div class="summary-value">{user_metrics["total_plays"]:,}<span class="summary-unit">回</span></div>
        </div>
        """,
        f"""
        <div class="summary-item">
            <div class="summary-label">平均スコア</div>
            <div class="summary-value">{user_metrics["average_score"]:.1f}</div>
        </div>
        """,
        f"""
        <div class="summary-item">
            <div class="summary-label">平均正確度</div>
            <div class="summary-value">{user_metrics["average_accuracy"] * 100:.1f}<span class="summary-unit">%</span></div>
        </div>
        """,
        f"""
        <div class="summary-item">
            <div class="summary-label">平均タイピング数</div>
            <div class="summary-value">{user_metrics["average_typing_count"]:.1f}<span class="summary-unit">回</span></div>
        </div>
        """,
        f"""
        <div class="summary-item">
            <div class="summary-label">総ミスタイプ数</div>
            <div class="summary-value">{user_metrics["total_misses"]:,}<span class="summary-unit">回</span></div>
        </div>
        """,
    ]

    # すべてのアイテムを1つのHTMLブロックとして表示
    st.markdown(
        f"""
        <div class="summary-container">
            {"".join(summary_items)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def calculate_user_metrics(
    user_scores: pl.DataFrame, user_misses: pl.DataFrame
) -> dict:
    """ユーザーメトリクスを計算

    Args:
        user_scores (pl.DataFrame): ユーザーのスコアデータ
        user_misses (pl.DataFrame): ユーザーのミスタイプデータ

    Returns:
        dict: ユーザーメトリクス
    """
    return {
        "total_plays": user_scores.height,
        "average_score": user_scores["score"].mean(),
        "average_accuracy": user_scores["accuracy"].mean(),
        "total_misses": user_misses["miss_count"].sum(),
        "average_typing_count": user_scores["typing_count"].mean(),
    }
