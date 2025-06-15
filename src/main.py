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


def save_uploaded_file(file, filename):
    """アップロードされたファイルを保存"""
    with open(DATA_DIR / filename, "wb") as f:
        f.write(file.getbuffer())


def load_saved_data():
    """保存されたデータを読み込む"""
    scores, misses, users = None, None, None
    if (DATA_DIR / "score.csv").exists():
        scores = pl.read_csv(DATA_DIR / "score.csv")
    if (DATA_DIR / "miss.csv").exists():
        misses = pl.read_csv(DATA_DIR / "miss.csv")
    if (DATA_DIR / "user.csv").exists():
        users = pl.read_csv(DATA_DIR / "user.csv")
    return scores, misses, users


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
    st.subheader("👑 全体サマリー")
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
        st.subheader("💯 難易度と言語の組み合わせによる平均スコア")
        show_difficulty_language_score_analysis(scores)
    with col4:
        st.subheader("💯 難易度と言語の組み合わせによる正確性")
        show_difficulty_language_accuracy_analysis(scores)


def check_password():
    """パスワードチェック"""
    # .envファイルからパスワードを読み込む
    load_dotenv()
    correct_password = os.getenv("UPLOAD_PASSWORD")
    if not correct_password:
        st.error("環境変数UPLOAD_PASSWORDが設定されていません。")
        return False

    # セッション状態の初期化
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if "password_attempted" not in st.session_state:
        st.session_state.password_attempted = False

    def password_entered():
        if "password" in st.session_state:
            st.session_state.password_attempted = True
            if st.session_state.password == correct_password:
                st.session_state.password_correct = True
                del st.session_state.password
            else:
                st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.text_input(
            "パスワードを入力してください",
            type="password",
            on_change=password_entered,
            key="password",
        )
        if (
            st.session_state.password_attempted
            and not st.session_state.password_correct
        ):
            st.error("😕 パスワードが正しくありません")
        return False
    else:
        return True


def show_data_upload():
    """データアップロード画面を表示"""
    if not check_password():
        return

    st.subheader("📤 CSVファイルのアップロード")

    # データの読み込み状態を表示
    data_loaded = (
        st.session_state.scores_data is not None
        and st.session_state.misses_data is not None
        and st.session_state.users_data is not None
        and st.session_state.scores_data.shape[0] > 0
        and st.session_state.misses_data.shape[0] > 0
        and st.session_state.users_data.shape[0] > 0
    )

    if data_loaded:
        st.success("✅ データの読み込みが完了しました")
        st.write("読み込まれたデータの件数:")
        st.write(f"- スコアデータ: {st.session_state.scores_data.shape[0]}件")
        st.write(f"- ミスタイプデータ: {st.session_state.misses_data.shape[0]}件")
        st.write(f"- ユーザーデータ: {st.session_state.users_data.shape[0]}件")

    # スコアデータのアップロード
    st.write("### スコアデータ")
    score_file = st.file_uploader(
        "スコアデータをアップロード",
        type="csv",
        key="score_upload",
        help="スコアデータのCSVファイルをドラッグ＆ドロップまたはクリックして選択",
    )
    if score_file is not None:
        try:
            # 直接Polarsで読み込む
            df = pl.read_csv(score_file)
            st.write("プレビュー:", df.head())
            if st.button("スコアデータを読み込み", key="load_score"):
                # 必要なカラムを選択
                required_columns = [
                    "user_id",
                    "diff_id",
                    "lang_id",
                    "score",
                    "accuracy",
                    "typing_count",
                    "created_at",
                ]
                if all(col in df.columns for col in required_columns):
                    # ファイルを保存
                    save_uploaded_file(score_file, "score.csv")
                    st.session_state.scores_data = df.select(required_columns)
                    st.success("スコアデータを読み込みました！")
                    st.rerun()
                else:
                    st.error(
                        "必要なカラムが不足しています。以下のカラムが必要です："
                        + ", ".join(required_columns)
                    )
        except Exception as e:
            st.error(f"スコアデータの読み込みに失敗しました: {str(e)}")

    # ミスタイプデータのアップロード
    st.write("### ミスタイプデータ")
    miss_file = st.file_uploader(
        "ミスタイプデータをアップロード",
        type="csv",
        key="miss_upload",
        help="ミスタイプデータのCSVファイルをドラッグ＆ドロップまたはクリックして選択",
    )
    if miss_file is not None:
        try:
            # 直接Polarsで読み込む
            df = pl.read_csv(miss_file)
            st.write("プレビュー:", df.head())
            if st.button("ミスタイプデータを読み込み", key="load_miss"):
                required_columns = ["user_id", "miss_char", "miss_count", "created_at"]
                if all(col in df.columns for col in required_columns):
                    # ファイルを保存
                    save_uploaded_file(miss_file, "miss.csv")
                    st.session_state.misses_data = df.select(required_columns)
                    st.success("ミスタイプデータを読み込みました！")
                    st.rerun()
                else:
                    st.error(
                        "必要なカラムが不足しています。以下のカラムが必要です："
                        + ", ".join(required_columns)
                    )
        except Exception as e:
            st.error(f"ミスタイプデータの読み込みに失敗しました: {str(e)}")

    # ユーザーデータのアップロード
    st.write("### ユーザーデータ")
    user_file = st.file_uploader(
        "ユーザーデータをアップロード",
        type="csv",
        key="user_upload",
        help="ユーザーデータのCSVファイルをドラッグ＆ドロップまたはクリックして選択",
    )
    if user_file is not None:
        try:
            # 直接Polarsで読み込む
            df = pl.read_csv(user_file)
            st.write("プレビュー:", df.head())
            if st.button("ユーザーデータを読み込み", key="load_user"):
                required_columns = ["user_id", "username", "created_at"]
                if all(col in df.columns for col in required_columns):
                    # ファイルを保存
                    save_uploaded_file(user_file, "user.csv")
                    st.session_state.users_data = df.select(required_columns)
                    st.success("ユーザーデータを読み込みました！")
                    st.rerun()
                else:
                    st.error(
                        "必要なカラムが不足しています。以下のカラムが必要です："
                        + ", ".join(required_columns)
                    )
        except Exception as e:
            st.error(f"ユーザーデータの読み込みに失敗しました: {str(e)}")

    # データのクリアボタン
    if st.button("データをクリア", key="clear_data"):
        # ファイルも削除
        for filename in ["score.csv", "miss.csv", "user.csv"]:
            file_path = DATA_DIR / filename
            if file_path.exists():
                file_path.unlink()
        st.session_state.scores_data = None
        st.session_state.misses_data = None
        st.session_state.users_data = None
        st.rerun()


def main():
    # ページ設定
    st.set_page_config(
        page_title="新卒Saltypeスコア分析",
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

    st.title("⌨️ 新卒Saltypeスコア分析")

    # データの読み込みを試みる
    try:
        scores, misses, users = load_data()
        scores, misses, users = load_and_process_data(scores, misses, users)
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {str(e)}")
        scores, misses, users = None, None, None

    # タブの作成
    tab1, tab2, tab3 = st.tabs(["📊 全体分析", "👤 個人分析", "📈 データサイエンス"])

    # データが読み込めている場合のみ分析タブを表示
    data_loaded = (
        scores is not None
        and misses is not None
        and users is not None
        and scores.shape[0] > 0
        and misses.shape[0] > 0
        and users.shape[0] > 0
    )

    if data_loaded:
        with tab1:
            try:
                show_overall_analysis(scores, misses, users)
            except Exception as e:
                st.error(f"全体分析の表示に失敗: {e}")
        with tab2:
            try:
                show_personal_analysis(scores, misses, users)
            except Exception as e:
                st.error(f"個人分析の表示に失敗: {e}")
        with tab3:
            try:
                show_data_science_analysis(scores, misses, users)
            except Exception as e:
                st.error(f"データサイエンス分析の表示に失敗: {e}")
    else:
        with tab1:
            st.info("data/ディレクトリに必要なデータファイルが存在しません。")
        with tab2:
            st.info("data/ディレクトリに必要なデータファイルが存在しません。")
        with tab3:
            st.info("data/ディレクトリに必要なデータファイルが存在しません。")


if __name__ == "__main__":
    main()
