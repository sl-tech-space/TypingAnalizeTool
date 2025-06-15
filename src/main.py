import sys
from pathlib import Path
import streamlit as st
import polars as pl
import pandas as pd
import os
from dotenv import load_dotenv
from overall import (
    show_growth_ranking,
    show_growth_ranking_details,
    show_average_score,
    show_average_score_details,
    show_overall_miss_chart,
    show_overall_miss_details,
    show_overall_summary,
    calculate_growth_ranking,
    calculate_average_score,
)
from personal import (
    show_growth_analysis,
    show_personal_miss_chart,
    show_personal_miss_details,
    show_personal_summary,
)
from data_science import (
    show_difficulty_language_score_analysis,
    show_difficulty_language_accuracy_analysis,
    show_time_score_analysis,
    show_time_accuracy_analysis,
)
from loader import load_data

# srcディレクトリをPythonパスに追加
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def load_and_process_data(scores, misses, users):
    """データの読み込みと前処理を行う"""
    try:
        if all(
            [
                scores is not None,
                misses is not None,
                users is not None,
            ]
        ):
            # データの型変換を明示的に行う
            scores = scores.with_columns(
                [
                    pl.col("created_at")
                    .str.replace("\\+00$", "")
                    .str.to_datetime(format="%Y-%m-%d %H:%M:%S.%f", strict=False),
                    pl.col("score").cast(pl.Float64),
                    pl.col("user_id").cast(pl.Utf8),
                    pl.col("diff_id").cast(pl.Int64),
                    pl.col("lang_id").cast(pl.Int64),
                    pl.col("accuracy").cast(pl.Float64),
                    pl.col("typing_count").cast(pl.Int64),
                ]
            )

            misses = misses.with_columns(
                [
                    pl.col("created_at")
                    .str.replace("\\+00$", "")
                    .str.to_datetime(format="%Y-%m-%d %H:%M:%S.%f", strict=False),
                    pl.col("user_id").cast(pl.Utf8),
                    pl.col("miss_count").cast(pl.Int64),
                ]
            )

            users = users.with_columns(
                [
                    pl.col("created_at")
                    .str.replace("\\+00$", "")
                    .str.to_datetime(format="%Y-%m-%d %H:%M:%S.%f", strict=False),
                    pl.col("user_id").cast(pl.Utf8),
                ]
            )

            # データの存在確認
            if scores.shape[0] > 0 and misses.shape[0] > 0 and users.shape[0] > 0:
                return scores, misses, users
    except Exception as e:
        st.error(f"データの処理中にエラーが発生しました: {str(e)}")
    return None, None, None


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
    # データの前処理
    scores = scores.with_columns(
        [
            pl.col("username").fill_null("不明"),  # usernameがnullの場合は"不明"を設定
        ]
    )
    misses = misses.with_columns(
        [
            pl.col("username").fill_null("不明"),  # usernameがnullの場合は"不明"を設定
        ]
    )

    # 全体サマリーを表示
    st.subheader("👑 全体成績")
    show_overall_summary(scores, misses)

    st.markdown("---")

    # 成長率ランキングを表示
    st.subheader("👑 成長率ランキング")

    # 月ごとの成長率ランキングを計算
    overall_growth_df = calculate_growth_ranking(scores)
    april_growth_df = calculate_growth_ranking(
        scores.filter(pl.col("created_at").dt.month() == 4)
    )
    may_growth_df = calculate_growth_ranking(
        scores.filter(pl.col("created_at").dt.month() == 5)
    )
    june_growth_df = calculate_growth_ranking(
        scores.filter(pl.col("created_at").dt.month() == 6)
    )

    # 月選択用のプルダウンメニュー
    month_options = {
        "全体": overall_growth_df,
        "4月": april_growth_df,
        "5月": may_growth_df,
        "6月": june_growth_df,
    }

    # プルダウンメニューを全体幅で表示
    selected_month = st.selectbox("期間を選択", list(month_options.keys()), index=0)
    selected_df = month_options[selected_month]

    # 成長率ランキングと詳細を横並びに表示
    col1, col2 = st.columns([2, 1])
    with col1:
        show_growth_ranking(selected_df)
    with col2:
        show_growth_ranking_details(scores, users)

    st.markdown("---")

    # 平均スコアランキングを表示
    st.subheader("👑 平均スコアランキング")

    # 月ごとの平均スコアランキングを計算
    overall_avg_df = calculate_average_score(scores)
    april_avg_df = calculate_average_score(
        scores.filter(pl.col("created_at").dt.month() == 4)
    )
    may_avg_df = calculate_average_score(
        scores.filter(pl.col("created_at").dt.month() == 5)
    )
    june_avg_df = calculate_average_score(
        scores.filter(pl.col("created_at").dt.month() == 6)
    )

    # 月選択用のプルダウンメニュー
    avg_month_options = {
        "全体": overall_avg_df,
        "4月": april_avg_df,
        "5月": may_avg_df,
        "6月": june_avg_df,
    }

    # プルダウンメニューを全体幅で表示
    selected_avg_month = st.selectbox(
        "期間を選択", list(avg_month_options.keys()), index=0, key="avg_month"
    )
    selected_avg_df = avg_month_options[selected_avg_month]

    # 平均スコアランキングと詳細を横並びに表示
    col3, col4 = st.columns([2, 1])
    with col3:
        show_average_score(selected_avg_df)
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
    # 新卒ユーザーのみをフィルタリング
    new_graduate_users = users.filter(pl.col("is_newgraduate") == 1)

    # 個人成績を表示
    st.subheader("👤 個人成績")

    # ユーザー選択（ユーザー名のリストを取得してソート）
    usernames = (
        new_graduate_users.select("username")
        .unique()
        .sort("username")
        .to_series()
        .to_list()
    )
    if not usernames:
        st.error("新卒ユーザーのデータが見つかりません")
        return

    # セッション状態の初期化
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = usernames[0]
    elif st.session_state.selected_user not in usernames:
        # 現在選択されているユーザーが新卒ユーザーリストに存在しない場合
        st.session_state.selected_user = usernames[0]

    # ユーザー選択ボックスの表示
    selected_user = st.selectbox(
        "分析するユーザーを選択",
        usernames,
        key="user_selector",
        index=usernames.index(st.session_state.selected_user),
    )

    # 選択されたユーザーをセッション状態に保存
    if selected_user != st.session_state.selected_user:
        st.session_state.selected_user = selected_user
        st.rerun()  # 選択が変更された場合にページを再読み込み

    # 選択されたユーザーのデータを取得
    user_data = new_graduate_users.filter(pl.col("username") == selected_user)
    if user_data.shape[0] == 0:
        st.error(f"ユーザー {selected_user} のデータが見つかりません")
        return

    user_id = user_data.select("user_id").item()

    # ユーザーのスコアとミスデータを取得
    user_scores = scores.filter(pl.col("user_id") == user_id)
    user_misses = misses.filter(pl.col("user_id") == user_id)

    if user_scores.shape[0] == 0:
        st.warning(f"ユーザー {selected_user} のスコアデータが見つかりません")
        return

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


def show_data_science_analysis(scores, misses, users):
    """データサイエンス分析を表示"""
    # データの前処理
    scores = scores.with_columns(
        [
            pl.col("diff_id")
            .map_dict({1: "イージー", 2: "ノーマル", 3: "ハード"})
            .alias("difficulty"),
            pl.col("lang_id").map_dict({1: "日本語", 2: "英語"}).alias("language"),
        ]
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⏰ 最高スコアが出やすい時間帯")
        show_time_score_analysis(scores)
    with col2:
        st.subheader("🗓️ 最高スコアが出やすい曜日")
        show_time_accuracy_analysis(scores)

    st.markdown("---")

    # 難易度と言語の組み合わせ分析
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("💯 難易度×言語別平均スコア")
        show_difficulty_language_score_analysis(scores)
    with col4:
        st.subheader("💯 難易度×言語別正確率")
        show_difficulty_language_accuracy_analysis(scores)


def main():
    # ページ設定
    st.set_page_config(
        page_title="新卒Saltypeスコア分析",
        page_icon="⌨️",
        layout="wide",
    )

    # CSSの読み込み
    load_css()

    st.title("⌨️ 新卒Saltypeスコア分析")

    # データの読み込み
    scores, misses, users = load_data()
    if scores is None or misses is None or users is None:
        st.error("データの読み込みに失敗しました")
        return

    # データの前処理
    scores, misses, users = load_and_process_data(scores, misses, users)
    if scores is None or misses is None or users is None:
        st.error("データの処理に失敗しました")
        return

    # タブの作成
    tab1, tab2, tab3 = st.tabs(["📊 全体サマリー", "👤 個人サマリー", "📈 データ分析"])

    with tab1:
        show_overall_analysis(scores, misses, users)

    with tab2:
        show_personal_analysis(scores, misses, users)

    with tab3:
        show_data_science_analysis(scores, misses, users)


if __name__ == "__main__":
    main()
