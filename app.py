import pandas as pd
import re
from datetime import datetime, timedelta
from dash import Dash, html, dcc, dash_table
import plotly.graph_objs as go

# === STEP 1: Load & Parse Dataset ===
df = pd.read_csv("data.csv")

def parse_relative_date(text):
    text = str(text).lower()
    today = datetime.today()
    try:
        if "sebulan" in text:
            return today - timedelta(days=30)
        elif "bulan" in text:
            match = re.search(r"(\d+)\s+bulan", text)
            if match:
                return today - timedelta(days=30 * int(match.group(1)))
        elif "setahun" in text:
            return today - timedelta(days=365)
        elif "tahun" in text:
            match = re.search(r"(\d+)\s+tahun", text)
            if match:
                return today - timedelta(days=365 * int(match.group(1)))
        elif "minggu" in text:
            match = re.search(r"(\d+)\s+minggu", text)
            if match:
                return today - timedelta(weeks=int(match.group(1)))
        elif "hari" in text:
            match = re.search(r"(\d+)\s+hari", text)
            if match:
                return today - timedelta(days=int(match.group(1)))
    except:
        return None
    return None

df["parsed_date"] = df["date"].apply(parse_relative_date)
df = df.dropna(subset=["parsed_date"])
df["week"] = df["parsed_date"].dt.to_period("W").apply(lambda r: r.start_time)

# Tambahkan kolom dummy link jika tidak ada
if "link" not in df.columns:
    df["link"] = "https://google.com"

# === STEP 2: Group by Minggu ===
weekly_summary = df.groupby("week").agg(
    jumlah_ulasan=("snippet", "count")
).reset_index()

# === STEP 3: Build Dash App ===
app = Dash(__name__)
app.title = "Dashboard Ulasan PDAM Sidoarjo"

app.layout = html.Div([
    html.H2("📊 Jumlah Ulasan per Minggu"),
    
    dcc.Graph(
        id='ulasan-mingguan',
        figure={
            'data': [
                go.Bar(
                    x=weekly_summary['week'],
                    y=weekly_summary['jumlah_ulasan'],
                    marker_color='lightskyblue',
                    text=weekly_summary['jumlah_ulasan'],
                    textposition='outside',
                    hovertemplate='Tanggal: %{x|%Y-%m-%d}<br>Jumlah Ulasan: %{y}<extra></extra>'
                )
            ],
            'layout': go.Layout(
                xaxis_title='Minggu',
                yaxis_title='Jumlah Ulasan',
                margin=dict(l=40, r=40, t=40, b=40),
                template='plotly_white'
            )
        }
    ),

    html.H3("📄 Daftar Ulasan + Link Sumber"),
    dash_table.DataTable(
        columns=[
            {"name": "Tanggal", "id": "parsed_date"},
            {"name": "Ulasan", "id": "snippet"},
            {"name": "Link", "id": "link", "presentation": "markdown"},
        ],
        data=[
            {
                "parsed_date": row["parsed_date"].strftime("%Y-%m-%d"),
                "snippet": row["snippet"],
                "link": f"[Klik Link]({row['link']})"
            }
            for _, row in df.sort_values("parsed_date", ascending=False).head(50).iterrows()
        ],
        style_cell={'textAlign': 'left', 'whiteSpace': 'normal', 'height': 'auto'},
        style_table={'overflowX': 'auto', 'maxHeight': '600px', 'overflowY': 'scroll'},
        markdown_options={"html": True},
        page_size=10,
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
