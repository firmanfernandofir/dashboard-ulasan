import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# Load data
df = pd.read_csv('data.csv', parse_dates=['Tanggal'])

# Pastikan kolom yang dibutuhkan tersedia
if 'Tanggal' not in df.columns or 'Ulasan' not in df.columns:
    raise ValueError("Dataset harus memiliki kolom 'Tanggal' dan 'Ulasan'")

# Tambahkan kolom tahun dan bulan
df['Tahun'] = df['Tanggal'].dt.year
df['Bulan'] = df['Tanggal'].dt.month
df['Tanggal Format'] = df['Tanggal'].dt.strftime('%Y-%m-%d')

# Inisialisasi Dash App
app = dash.Dash(__name__)
server = app.server  # <--- penting untuk Railway

# Layout aplikasi
app.layout = html.Div([
    html.H1('Dashboard Ulasan', style={'textAlign': 'center'}),
    
    dcc.Dropdown(
        id='dropdown-tahun',
        options=[{'label': str(t), 'value': t} for t in sorted(df['Tahun'].unique())],
        value=sorted(df['Tahun'].unique())[0],
        clearable=False,
        style={'width': '50%', 'margin': 'auto'}
    ),

    dcc.Graph(id='grafik-ulas')

    ,

    html.H2('Daftar Ulasan Lengkap'),
    html.Div(id='tabel-ulas')
])

# Callback grafik
@app.callback(
    dash.dependencies.Output('grafik-ulas', 'figure'),
    dash.dependencies.Input('dropdown-tahun', 'value')
)
def update_grafik(tahun):
    dff = df[df['Tahun'] == tahun]
    data_per_bulan = dff.groupby('Bulan').size().reset_index(name='Jumlah Ulasan')
    fig = px.bar(data_per_bulan, x='Bulan', y='Jumlah Ulasan', title=f'Ulasan per Bulan - {tahun}')
    return fig

# Callback tabel
@app.callback(
    dash.dependencies.Output('tabel-ulas', 'children'),
    dash.dependencies.Input('dropdown-tahun', 'value')
)
def tampilkan_ulasan(tahun):
    dff = df[df['Tahun'] == tahun]
    tabel = html.Ul([
        html.Li(f"{row['Tanggal Format']}: {row['Ulasan']}")
        for i, row in dff.iterrows()
    ])
    return tabel

if __name__ == '__main__':
    app.run_server(debug=True)
