import plotly.graph_objects as go
import polars as pl


def create_bar_chart(
    data: pl.DataFrame, x_col: str, y_col: str, title: str = None
) -> go.Figure:
    """縦棒グラフを作成"""
    # グラフの基本設定
    fig = go.Figure()

    # 棒グラフの追加
    fig.add_trace(
        go.Bar(
            x=data[x_col].to_numpy(),
            y=data[y_col].to_numpy(),
            marker_color="#00ACFF",  # Streamlitのプライマリカラーに近い青
            text=data[y_col].to_numpy(),  # 値のラベル
            textposition="outside",  # ラベルの位置
            texttemplate="%{text:,.0f}",  # 数値のフォーマット
            textfont=dict(size=12, color="#FFFFFF"),  # テキストを白に
            hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",  # ホバー時の表示
            width=0.6,  # 棒の幅を調整
        )
    )

    # レイアウトの設定
    layout = {
        "showlegend": False,
        "height": 500,
        "margin": dict(l=20, r=20, t=40, b=20),  # タイトルがない場合のマージン調整
        "plot_bgcolor": "#0E1117",  # Streamlitのダークテーマの背景色
        "paper_bgcolor": "#0E1117",  # Streamlitのダークテーマの背景色
        "xaxis": dict(
            title=None,
            showgrid=True,
            gridcolor="#262730",  # グリッド線の色を暗めに
            tickfont=dict(size=12, color="#FFFFFF", family="Arial"),  # テキストを白に
            tickangle=-45,  # ラベルを45度回転
            tickmode="array",
            ticktext=data[x_col].to_numpy(),
            tickvals=data[x_col].to_numpy(),
            zeroline=False,  # ゼロラインを非表示
        ),
        "yaxis": dict(
            title=None,
            showgrid=True,
            gridcolor="#262730",  # グリッド線の色を暗めに
            tickfont=dict(size=12, color="#FFFFFF", family="Arial"),  # テキストを白に
            tickformat=",.0f",  # 数値のフォーマット
            zeroline=False,  # ゼロラインを非表示
            rangemode="tozero",  # Y軸の範囲を0から開始
        ),
        "hovermode": "x unified",  # ホバー時の表示モード
        "hoverlabel": dict(
            bgcolor="#262730",  # ホバーラベルの背景色
            font_size=12,
            font_family="Arial",
            font_color="#FFFFFF",  # ホバーラベルのテキスト色
        ),
        "bargap": 0.2,  # 棒グラフ間の間隔
        "bargroupgap": 0.1,  # 棒グラフグループ間の間隔
    }

    # タイトルが指定されている場合のみ追加
    if title:
        layout["title"] = dict(
            text=title,
            font=dict(size=18, color="#FFFFFF", family="Arial"),
        )
        layout["margin"]["t"] = 60  # タイトルがある場合のマージン調整

    fig.update_layout(**layout)

    return fig
