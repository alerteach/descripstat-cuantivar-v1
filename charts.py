import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy.stats import gaussian_kde

PLOTLY_CONFIG = {
    'displayModeBar': False,
    'scrollZoom': False,
    'doubleClick': 'reset',
    'responsive': True
}

def create_summary_five_numbers(stats):
    min_val = stats['min']
    q1 = stats['q1']
    median = stats['median']
    q3 = stats['q3']
    max_val = stats['max']

    fig = go.Figure()

    fig.add_trace(go.Box(
        x=[min_val, q1, median, q3, max_val],
        name="",
        boxpoints=False,
        orientation='h',
        marker_color='#2563EB',
        line=dict(width=2),
        showlegend=False
    ))

    labels = ['Mín', 'Q1', 'Mediana', 'Q3', 'Máx']
    vals = [min_val, q1, median, q3, max_val]

    fig.add_trace(go.Scatter(
        x=vals,
        y=[0]*5,
        mode='markers+text',
        text=[f"<b>{l}</b><br>{v:,.2f}" for l, v in zip(labels, vals)],
        textposition="top center",
        marker=dict(color='#1E3A8A', size=10),
        hoverinfo='none',
        showlegend=False
    ))

    fig.update_layout(
        title=dict(text="Resumen de 5 Números (Caja y Bigotes)", font=dict(size=14, color="#1E293B")),
        xaxis=dict(showgrid=True, zeroline=False),
        yaxis=dict(showticklabels=False, range=[-0.8, 1.2]),
        height=220,
        margin=dict(l=15, r=15, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        dragmode=False
    )

    return fig

def create_histogram_with_kde(data, k_intervals):
    data_np = np.array(data)
    
    fig = go.Figure()

    # Histograma con bordes definidos entre columnas
    fig.add_trace(go.Histogram(
        x=data_np,
        nbinsx=k_intervals,
        name="Frecuencia",
        marker=dict(
            color="#2563EB",
            line=dict(color="#FFFFFF", width=1.5)  # Delimitación entre barras
        ),
        opacity=0.85,
        histnorm='probability density'
    ))

    if len(data_np) > 1 and np.std(data_np) > 0:
        kde = gaussian_kde(data_np)
        x_vals = np.linspace(min(data_np), max(data_np), 200)
        y_vals = kde(x_vals)

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='lines',
            name="Tendencia (KDE)",
            line=dict(color='#DC2626', width=2.5)
        ))

    fig.update_layout(
        title=dict(text="Histograma y Curva de Tendencia", font=dict(size=14, color="#1E293B")),
        xaxis_title="Valor (X)",
        yaxis_title="Densidad",
        height=320,
        margin=dict(l=15, r=15, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        dragmode=False
    )

    return fig