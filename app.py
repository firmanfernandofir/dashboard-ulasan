import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import os

# ==== Load data safely ====
DATA_FILE = 'data.csv'

try:
    df = pd.read_csv(DATA_FILE, parse_dates=['Tanggal'])
except Exception as e:
    raise Exception(f"Gagal membaca '{DATA_FILE}': {e}")

# ==== Validasi kolom ====
required_columns = {'Tanggal', 'Ulasan'}
if not required_columns.issubset(df.columns):
    raise ValueError(f"Kolom yang dibutuhkan tidak ditemukan. Diperlukan: {required_columns}")

# ==== Prakondisi waktu ====
df['Tahun'] = df['Tanggal'].dt.year
df['Bulan'] = df['Tanggal'].dt.month
df['Tanggal Format'] = df['Tanggal'].dt.strftime('%Y-%m-%d')

# ==== Inisialisasi App Dash ====
app = dash.Dash(__name__)
server = app.server  # penting untuk deployment ke Railway

# ==== Layout ====
app.layout = html.Div([
    html.H1('Dashboard Ulasan Scraping', style={'textAlign': 'center'}),

    dcc.Dropdown(
        id='dropdown-tahun',
        options=[{'label': str(t), 'value': t} for t in sorted(df['Tahun'].unique())],
        value=sorted(df['Tahun'].unique())[0],
        clearable=False,
        style={'width': '50%', 'margin': 'auto'}
    ),

    dcc.Graph(id='grafik-ulas'),

    html.H2('Daftar Ulasan'),
    html.Div(id='tabel-ulas')
])

# ==== Callback grafik ====
@app.callback(
    dash.dependencies.Output('grafik-ulas', 'figure'),
    dash.dependencies.Input('dropdown-tahun', 'value')
)
def update_grafik(tahun):
    dff = df[df['Tahun'] == tahun]
    data_per_bulan = dff.groupby('Bulan').size().reset_index(name='Jumlah Ulasan')
    fig = px.bar(data_per_bulan, x='Bulan', y='Jumlah Ulasan', title=f'Ulasan per Bulan - {tahun}')
    return fig

# ==== Callback ulasan ====
@app.callback(
    dash.dependencies.Output('tabel-ulas', 'children'),
    dash.dependencies.Input('dropdown-tahun', 'value')
)
def tampilkan_ulasan(tahun):
    dff = df[df['Tahun'] == tahun]
    return html.Ul([
        html.Li(f"{row['Tanggal Format']}: {row['Ulasan']}")
        for i, row in dff.iterrows()
    ])

# ==== Jalankan lokal ====
if __name__ == '__main__':
    app.run_server(debug=True)
