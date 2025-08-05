# app.py

import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
from datetime import datetime, timedelta
import re

# === 1. Load Data ===
df = pd.read_csv("data.csv")

# === 2. Parsing Tanggal ===
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

df = df.dropna(subset=["date", "snippet"])
df["parsed_date"] = df["date"].apply(parse_relative_date)
df = df.dropna(subset=["parsed_date"])
df["parsed_date"] = pd.to_datetime(df["parsed_date"])
df["week"] = df["parsed_date"].dt.to_period("W").apply(lambda r: r.start_time)
df["month"] = df["parsed_date"].dt.to_period("M").astype(str)
df["year"] = df["parsed_date"].dt.year

# === 3. Inisialisasi Dash ===
app = dash.Dash(__name__)
server = app.server  # Untuk deployment Railway

# === 4. Layout Aplikasi ===
app.layout = html.Div([
    html.H2("📊 Dashboard Ulasan: Mingguan & Bulanan"),

    html.Div([
        dcc.Dropdown(
            id='filter_tahun',
            options=[{"label": str(y), "value": y} for y in sorted(df['year'].unique())],
            value=2025,
            placeholder="Pilih Tahun"
        ),
        dcc.Dropdown(
            id='filter_bulan',
            placeholder="Pilih Bulan (opsional)"
        )
    ], style={'width': '60%', 'margin': '20px auto'}),

    dcc.Graph(id='grafik_ulasan'),

    html.H4("🗂️ Daftar Ulasan + Link Sumber"),
    dash_table.DataTable(
        id='tabel_ulasan',
        columns=[
            {"name": "Tanggal", "id": "parsed_date"},
            {"name": "Ulasan", "id": "snippet"},
            {"name": "Link", "id": "link", "presentation": "markdown"}
        ],
        style_cell={"textAlign": "left", 'whiteSpace': 'normal', 'height': 'auto'},
        style_table={"overflowX": "auto"},
        page_size=10
    )
])

# === 5. Callback ===
@app.callback(
    Output('filter_bulan', 'options'),
    Output('filter_bulan', 'value'),
    Input('filter_tahun', 'value')
)
def update_bulan_options(tahun):
    bulan_data = df[df['year'] == tahun]['month'].unique()
    return ([{"label": b, "value": b} for b in sorted(bulan_data)], None)

@app.callback(
    Output('grafik_ulasan', 'figure'),
    Output('tabel_ulasan', 'data'),
    Input('filter_tahun', 'value'),
    Input('filter_bulan', 'value')
)
def update_visualisasi(tahun, bulan):
    dff = df[df['year'] == tahun]
    if bulan:
        dff = dff[dff['month'] == bulan]

    # Grafik mingguan
    weekly_counts = dff.groupby('week').size().reset_index(name='Jumlah')
    fig = px.bar(weekly_counts, x='week', y='Jumlah', title='Jumlah Ulasan per Minggu', opacity=0.6)
    fig.update_layout(xaxis_title='Minggu', yaxis_title='Jumlah Ulasan')

    # Data tabel dengan link Markdown
    tabel_data = dff[['parsed_date', 'snippet', 'link']].copy()
    tabel_data['parsed_date'] = tabel_data['parsed_date'].dt.strftime('%Y-%m-%d')
    tabel_data['link'] = tabel_data['link'].apply(lambda l: f"[Klik Link]({l})")

    return fig, tabel_data.to_dict('records')

# === 6. Jalankan Lokal ===
if __name__ == '__main__':
    app.run_server(debug=True)
