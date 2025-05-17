import sys
from pathlib import Path
import streamlit as st
import polars as pl
from loader import load_data
from overall import (
    show_growth_ranking,
    show_growth_ranking_details,
    show_average_score,
    show_average_score_details,
    show_overall_miss_chart,
    show_overall_miss_details,
    show_overall_summary,
)
from personal import (
    show_growth_analysis,
    show_personal_miss_chart,
    show_personal_miss_details,
    show_personal_summary,
)

# srcディレクトリをPythonパスに追加
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)


def load_css():
    """CSSファイルを読み込む"""
    css_dir = Path(__file__).parent / "static"

    # CSSファイルの読み込み順序
    css_files = [
        "base.css",  # 基本レイアウト
        "ranking.css",  # ランキング表示用
        "summary.css",  # サマリー表示用
        "growth.css",  # 成長率分析用
    ]

    # 各CSSファイルを読み込む
    for css_file in css_files:
        with open(css_dir / css_file) as f:
            # CSSを直接スタイルタグとして挿入
            st.markdown(
                f"""
                <style>
                {f.read()}
                </style>
                """,
                unsafe_allow_html=True,
            )


def show_overall_analysis(scores, misses, users):
    """全体分析を表示"""
    # 全体サマリーを表示
    st.subheader("👑 全体サマリー")
    show_overall_summary(scores, misses)

    st.markdown("---")

    # 成長率ランキングとモード別プレイ回数を横並びに表示
    st.subheader("👑 成長率ランキング")
    col1, col2 = st.columns([2, 1])
    with col1:
        show_growth_ranking(scores, users)
    with col2:
        show_growth_ranking_details(scores, users)

    st.markdown("---")

    # 平均スコアとプレイ回数を横並びに表示
    st.subheader("👑 平均スコアランキング")
    col3, col4 = st.columns([2, 1])
    with col3:
        show_average_score(scores, users)
    with col4:
        show_average_score_details(scores, users)

    st.markdown("---")

    # 全体ミスタイプ分析
    st.subheader("💬 全体ミスタイプ分析")
    col5, col6 = st.columns([2, 1])
    with col5:
        show_overall_miss_chart(misses)
    with col6:
        show_overall_miss_details(misses)


def show_personal_analysis(scores, misses, users):
    """個人分析を表示"""
    # ユーザー選択
    selected_user = st.selectbox(
        "分析するユーザーを選択",
        users,
        key="user_selector",
    )

    # ユーザーデータの取得
    user_scores = scores.filter(pl.col("username") == selected_user)
    user_misses = misses.filter(pl.col("username") == selected_user)

    # 個人サマリーを表示
    st.subheader("👤 個人サマリー")
    show_personal_summary(user_scores, user_misses)

    # 成長率分析
    st.subheader("👑 成長率分析")
    show_growth_analysis(user_scores)

    # 個人ミスタイプ分析
    st.subheader("💬 個人ミスタイプ分析")
    col7, col8 = st.columns([2, 1])
    with col7:
        show_personal_miss_chart(user_misses, selected_user)
    with col8:
        show_personal_miss_details(user_misses, selected_user)


def main():
    # ページ設定
    st.set_page_config(
        page_title="タイピング分析ダッシュボード",
        page_icon="⌨️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # CSSの読み込み（ページ設定の後に行う）
    load_css()

    # カスタムスタイルの追加
    st.markdown(
        """
        <style>
        /* タブのスタイルを直接指定 */
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 2rem !important;
            padding: 1rem !important;
        }
        div[data-testid="stTabs"] [data-baseweb="tab"] {
            padding: 1rem 2rem !important;
            margin: 0 1rem !important;
            font-size: 1.25rem !important;
        }
        /* 見出しのスタイルを直接指定 */
        div[data-testid="stMarkdown"] h1 {
            font-size: 2.8rem !important;
            color: white !important;
            margin: 2rem 0 !important;
        }
        div[data-testid="stMarkdown"] h2 {
            font-size: 2.4rem !important;
            margin: 1.5rem 0 !important;
        }
        div[data-testid="stMarkdown"] h3 {
            font-size: 2rem !important;
            margin: 1rem 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("⌨️ タイピング分析ダッシュボード")

    # データの読み込み
    try:
        scores, misses = load_data()
    except Exception as e:
        st.error("データの読み込みに失敗しました。")
        st.error(str(e))
        st.stop()

    # ユーザーリストの取得
    users = scores["username"].unique().to_list()
    users.sort()

    # タブの作成
    tab1, tab2 = st.tabs(["📊 全体分析", "👤 個人分析"])

    # 全体分析タブ
    with tab1:
        show_overall_analysis(scores, misses, users)

    # 個人分析タブ
    with tab2:
        show_personal_analysis(scores, misses, users)


if __name__ == "__main__":
    main()
