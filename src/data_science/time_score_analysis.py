import streamlit as st
import polars as pl
import plotly.graph_objects as go


def show_time_score_analysis(scores: pl.DataFrame):
    """時間帯分析のグラフを表示"""
    if len(scores) == 0:
        st.info("スコアデータがありません")
        return

    # 時間帯別スコアのグラフを作成
    fig = create_time_heatmap(scores)
    st.plotly_chart(fig, use_container_width=True)
    # 最高スコアが出やすい時間帯を表示
    show_time_analysis_text(scores, is_weekday=False)


def show_time_analysis_text(scores: pl.DataFrame, is_weekday: bool):
    """時間帯分析のテキスト情報を表示"""
    # 各ユーザーの各難易度・モードの最高スコアを取得
    best_scores = scores.group_by(["user_id", "diff_id", "lang_id"]).agg(
        pl.col("score").max().alias("max_score"),
        pl.col("created_at")
        .filter(pl.col("score") == pl.col("score").max())
        .first()
        .alias("best_time"),
    )

    # 日時型に変換してから時間と曜日を抽出
    best_scores = best_scores.with_columns(
        [
            pl.col("best_time")
            .str.extract(r"(\d{2}):\d{2}:\d{2}")  # 時間部分を抽出
            .cast(pl.Int64)  # 整数に変換
            .map_elements(lambda x: (x + 9) % 24)  # UTC+9に変換（日本時間）
            .alias("hour"),
            pl.col("best_time")
            .str.extract(r"(\d{4}-\d{2}-\d{2})")  # 日付部分を抽出
            .str.strptime(pl.Date, "%Y-%m-%d")  # 日付型に変換
            .dt.weekday()  # 曜日を取得（0=月曜日）
            .map_elements(lambda x: (x - 1) % 7)  # 曜日を1日ずらす
            .alias("weekday"),
        ]
    )

    if is_weekday:
        # 曜日×時間帯で集計
        time_scores = (
            best_scores.filter(
                (pl.col("hour") >= 8)
                & (pl.col("hour") < 21)
                & (pl.col("weekday") < 5)  # 土日を除外
            )
            .group_by(["weekday", "hour"])
            .agg(pl.col("max_score").count().alias("count"))
            .sort(["weekday", "hour"])
        )

        if len(time_scores) == 0:
            return

        # 最高スコアが出やすい曜日と時間帯を特定
        best_time = time_scores.filter(pl.col("count") == time_scores["count"].max())
        best_time_row = best_time.row(0, named=True)
        weekday_names = ["月", "火", "水", "木", "金"]

        st.markdown(
            f"""
            <div class="ranking-text">
                <span class="rank-number">🏆</span>
                最高スコアが出やすい時間帯
                <span class="rank-score">{weekday_names[int(best_time_row["weekday"])]}曜日 {int(best_time_row["hour"])}時台</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # 時間帯ごとに集計
        time_scores = (
            best_scores.filter((pl.col("hour") >= 8) & (pl.col("hour") < 21))
            .group_by("hour")
            .agg(pl.col("max_score").count().alias("count"))
            .sort("hour")
        )

        if len(time_scores) == 0:
            return

        # 最高スコアが出やすい時間帯を特定
        best_hour = time_scores.filter(pl.col("count") == time_scores["count"].max())
        best_hour_row = best_hour.row(0, named=True)

        st.markdown(
            f"""
            <div class="ranking-text">
                <span class="rank-number">🏆</span>
                最高スコアが出やすい時間帯
                <span class="rank-score">{int(best_hour_row["hour"])}時台</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def create_time_heatmap(scores: pl.DataFrame) -> go.Figure:
    """時間帯ヒートマップを作成"""
    # 各ユーザーの各難易度・モードの最高スコアを取得
    best_scores = scores.group_by(["user_id", "diff_id", "lang_id"]).agg(
        pl.col("score").max().alias("max_score"),
        pl.col("created_at")
        .filter(pl.col("score") == pl.col("score").max())
        .first()
        .alias("best_time"),
    )

    # 日時型に変換してから時間を抽出
    best_scores = best_scores.with_columns(
        pl.col("best_time")
        .str.extract(r"(\d{2}):\d{2}:\d{2}")  # 時間部分を抽出
        .cast(pl.Int64)  # 整数に変換
        .map_elements(lambda x: (x + 9) % 24)  # UTC+9に変換（日本時間）
        .alias("hour")
    )

    # 表示する時間範囲を設定（8:00-20:00）
    start_hour = 8
    end_hour = 21  # 20:00を含めるため
    hours = list(range(start_hour, end_hour))
    scores = [0] * len(hours)
    counts = [0] * len(hours)

    # 時間帯ごとに集計
    time_scores = (
        best_scores.filter((pl.col("hour") >= start_hour) & (pl.col("hour") < end_hour))
        .group_by("hour")
        .agg(
            pl.col("max_score").count().alias("count")  # 最高スコアの数をカウント
        )
        .sort("hour")
    )

    # データを埋める
    for row in time_scores.iter_rows(named=True):
        hour = int(row["hour"])
        if start_hour <= hour < end_hour:
            counts[hour - start_hour] = row["count"]

    # ヒートマップを作成
    fig = go.Figure()

    # スコアのヒートマップ
    fig.add_trace(
        go.Bar(
            x=hours,
            y=counts,
            marker_color=counts,
            marker_colorscale="Viridis",
            name="最高スコア数",
            hovertemplate="%{x}時台<br>最高スコア数: %{y}回<extra></extra>",
        )
    )

    # レイアウトの設定
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=11, color="white"),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.2)",
            gridwidth=1,
            tickfont=dict(color="white"),
            tickmode="linear",
            tick0=start_hour,
            dtick=1,
            title="時間帯",
            titlefont=dict(color="white"),
            range=[start_hour - 0.5, end_hour - 0.5],  # バーの表示を調整
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.2)",
            gridwidth=1,
            tickfont=dict(color="white"),
            title="最高スコア数",
            titlefont=dict(color="white"),
        ),
        paper_bgcolor="black",
        plot_bgcolor="black",
        showlegend=False,
    )

    return fig


def calculate_time_scores(scores: pl.DataFrame) -> pl.DataFrame:
    """時間帯別のスコアを計算"""
    # 文字列の日時を日時型に変換
    scores = scores.with_columns(
        pl.col("created_at").str.to_datetime(strict=False).alias("created_at")
    )

    # 日時から曜日と時間を抽出
    scores = scores.with_columns(
        pl.col("created_at").dt.weekday().alias("weekday"),
        pl.col("created_at").dt.hour().alias("hour"),
    )

    # 曜日の名前を設定
    weekday_names = ["月", "火", "水", "木", "金", "土", "日"]
    scores = scores.with_columns(
        pl.col("weekday").map_dict(dict(enumerate(weekday_names, 1))).alias("weekday")
    )

    # 時間帯と曜日でグループ化して平均スコアを計算
    time_scores = (
        scores.group_by(["weekday", "hour"])
        .agg(pl.col("score").mean().alias("score"))
        .sort(["weekday", "hour"])
    )

    # データを2次元配列に変換
    weekdays = time_scores["weekday"].unique().to_list()
    hours = time_scores["hour"].unique().to_list()
    score_matrix = []

    for weekday in weekdays:
        row = []
        for hour in hours:
            filtered_data = time_scores.filter(
                (pl.col("weekday") == weekday) & (pl.col("hour") == hour)
            )
            # データが存在する場合はその値を、存在しない場合は0を使用
            score = filtered_data["score"].item() if len(filtered_data) > 0 else 0
            row.append(score)
        score_matrix.append(row)

    return pl.DataFrame(
        {
            "weekday": weekdays,
            "hour": hours,
            "score": score_matrix,
        }
    )
