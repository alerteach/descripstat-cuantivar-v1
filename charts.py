import plotly.graph_objects as go
import numpy as np
from scipy import stats

def create_histogram_with_kde(numbers, k_sturges):
    fig = go.Figure()

    # Histograma con bordes blancos claros
    fig.add_trace(go.Histogram(
        x=numbers,
        nbinsx=k_sturges,
        name="Frecuencia",
        marker_color='#1E40AF',
        marker_line_color='white',
        marker_line_width=2,
        opacity=0.85,
        histnorm='probability density'
    ))

    # Curva KDE
    kde = stats.gaussian_kde(numbers)
    x_vals = np.linspace(min(numbers), max(numbers), 200)
    y_vals = kde(x_vals)

    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        name='Tendencia de Distribución (KDE)',
        line=dict(color='#DC2626', width=3)
    ))

    fig.update_layout(
        title="<b>Histograma de Frecuencias y Curva de Tendencia</b>",
        xaxis_title="Valores de la Variable",
        yaxis_title="Densidad",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"
    )
    return fig

def create_summary_five_numbers(stats_dict):
    """Crea una ilustración equilibrada con Boxplot y marcas de 5 números."""
    vals = [stats_dict['min'], stats_dict['q1'], stats_dict['median'], stats_dict['q3'], stats_dict['max']]
    labels = ["Mínimo", "Q1 (P25)", "Q2 (Mediana)", "Q3 (P75)", "Máximo"]
    
    fig = go.Figure()

    # Diagrama de Caja
    fig.add_trace(go.Box(
        x=stats_dict['min'] if False else None,
        q1=[stats_dict['q1']],
        median=[stats_dict['median']],
        q3=[stats_dict['q3']],
        lowerfence=[stats_dict['min']],
        upperfence=[stats_dict['max']],
        orientation='h',
        name="Distribución",
        fillcolor='rgba(37, 99, 235, 0.15)',
        line=dict(color='#2563EB', width=2),
        showlegend=False
    ))

    # Puntos numéricos limpios
    fig.add_trace(go.Scatter(
        x=vals,
        y=[0]*5,
        mode='markers+text',
        marker=dict(size=12, color='#1E3A8A'),
        text=[f"<b>{lbl}</b><br>{val:,.2f}" for lbl, val in zip(labels, vals)],
        textposition=["top center", "bottom center", "top center", "bottom center", "top center"],
        hoverinfo='text',
        showlegend=False
    ))

    fig.update_layout(
        title="<b>Posición y Dispersión (Diagrama de Caja y 5 Números Clave)</b>",
        xaxis=dict(showgrid=True, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        template="plotly_white",
        height=260,
        margin=dict(l=40, r=40, t=60, b=30)
    )
    return fig