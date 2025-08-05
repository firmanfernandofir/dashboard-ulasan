import dash
from dash import html, dcc
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv('data.csv')

# Contoh asumsi data.csv memiliki kolom bernama 'tanggal' dan 'sentimen'
if 'tanggal' in df.columns:
    df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
    df = df.dropna(subset=['tanggal'])

# Inisialisasi Dash app
app = dash.Dash(__name__)
app.title = "Dashboard Ulasan"
server = app.server  # <<== Penting untuk Railway (Gunicorn)

# Layout
app.layout = html.Div([
    html.H1("Dashboard Ulasan", style={"textAlign": "center"}),
    
    dcc.Graph(
        id='grafik-sentimen',
        figure=px.histogram(df, x='tanggal', title="Jumlah Ulasan per Tanggal")
    ),
    
    html.Div("Sumber data: data.csv", style={"textAlign": "center", "marginTop": "20px"})
])
