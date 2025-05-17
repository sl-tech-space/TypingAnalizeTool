import streamlit as st
import polars as pl


def show_personal_summary(user_scores, user_misses):
    """ユーザーサマリーを表示"""
    user_metrics = calculate_user_metrics(user_scores, user_misses)
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("総プレイ回数", f"{user_metrics['total_plays']:,}回")
    with metric_cols[1]:
        st.metric("平均スコア", f"{user_metrics['average_score']:.1f}")
    with metric_cols[2]:
        st.metric("平均正確度", f"{user_metrics['average_accuracy'] * 100:.1f}%")
    with metric_cols[3]:
        st.metric("総ミスタイプ数", f"{user_metrics['total_misses']:,}回")


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
    }
