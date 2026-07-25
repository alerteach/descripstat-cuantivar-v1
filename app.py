import streamlit as st
import numpy as np
import pandas as pd
from metrics import process_raw_data, calculate_descriptive_stats, generate_frequency_table_intervals, generate_frequency_table_discrete
from charts import create_histogram_with_kde, create_summary_five_numbers, PLOTLY_CONFIG

st.set_page_config(page_title="Analizador Estadístico Cuantitativo", layout="wide")

# Estilos CSS de Alta Legibilidad y Resalte de Resultados
st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: 800; color: #1E3A8A; margin-bottom: 5px; }
    .var-title { font-size: 18px; font-weight: 700; color: #2563EB; margin-bottom: 20px; border-bottom: 2px solid #E5E7EB; padding-bottom: 6px; }
    
    /* Tarjetas de Estadística con Tipografía Destacada */
    .stat-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .stat-card-title {
        font-size: 14px;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        border-bottom: 2px solid #F1F5F9;
        padding-bottom: 6px;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px dashed #F1F5F9;
    }
    .metric-row:last-child { border-bottom: none; }
    .metric-label { font-size: 13px; color: #64748B; font-weight: 500; }
    .metric-value { font-size: 18px; color: #0F172A; font-weight: 800; font-family: monospace; }
    .highlight-value { color: #2563EB; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Sistema de Análisis Estadístico Descriptivo</div>', unsafe_allow_html=True)

# Panel Lateral
st.sidebar.header("Configuración de Datos")
var_name = st.sidebar.text_input("Nombre de la Variable Cuantitativa:", value="Variable Cuantitativa 1")
data_type = st.sidebar.radio("Tipo de Tabla de Frecuencias:", ["Agrupada por Intervalos (Continua)", "Valores Únicos (Discreta)"])

custom_k_value = None
if "Intervalos" in data_type:
    interval_method = st.sidebar.radio(
        "Cálculo de Intervalos (k):",
        ["Regla de Sturges (Impar cercano)", "Personalizado"]
    )
    if interval_method == "Personalizado":
        custom_k_value = st.sidebar.number_input(
            "Número de Intervalos deseados (k):",
            min_value=1,
            max_value=50,
            value=7,
            step=1
        )

st.sidebar.markdown("---")
example_type = st.sidebar.radio("Cargar datos de ejemplo:", ["No, ingresar mis datos", "Ejemplo 100 datos", "Ejemplo 1,000 datos"])

data_input = ""
is_discrete = "Discreta" in data_type

if example_type == "Ejemplo 100 datos":
    np.random.seed(42)
    if is_discrete:
        data_input = " ".join(map(str, np.random.randint(1, 11, size=100)))
    else:
        data_input = " ".join(map(str, np.round(np.random.normal(500, 150, 100), 2)))

elif example_type == "Ejemplo 1,000 datos":
    np.random.seed(42)
    if is_discrete:
        data_input = " ".join(map(str, np.random.poisson(lam=5, size=1000)))
    else:
        data_input = " ".join(map(str, np.round(np.random.exponential(scale=300000, size=1000), 2)))

raw_text = st.sidebar.text_area("Ingrese los datos (separados por espacio, coma o salto de línea):", value=data_input, height=220)

numbers = process_raw_data(raw_text)

if len(numbers) < 2:
    st.info("Ingrese al menos 2 valores numéricos en el panel lateral para iniciar el análisis.")
else:
    st.markdown(f'<div class="var-title">Variable en Análisis: {var_name}</div>', unsafe_allow_html=True)

    s = calculate_descriptive_stats(numbers)

    if "Intervalos" in data_type:
        df_freq, k, width = generate_frequency_table_intervals(numbers, custom_k=custom_k_value)
    else:
        df_freq = generate_frequency_table_discrete(numbers)
        k, width = len(df_freq) - 1, 0  # Resta la fila TOTAL

    # 1. Resumen General
    st.subheader("Resumen Muestral")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tamaño Muestral (N)", f"{s['n']:,}")
    c2.metric("Mínimo", f"{s['min']:,.2f}")
    c3.metric("Máximo", f"{s['max']:,.2f}")
    if "Intervalos" in data_type:
        c4.metric("Número de Clases (k)", f"{k}", help=f"Amplitud de clase (A) = {width}")
    else:
        c4.metric("Valores Únicos", f"{k}")

    st.markdown("---")

    # 2. Diagrama de 5 Números
    st.plotly_chart(create_summary_five_numbers(s), use_container_width=True, config=PLOTLY_CONFIG)

    with st.expander("Ver Tabla de Percentiles (P10 - P95)"):
        p_cols = st.columns(6)
        i = 0
        for name, val in s['percentiles'].items():
            p_cols[i % 6].metric(name, f"{val:,.2f}")
            i += 1

    st.markdown("---")

    # 3. Histograma y Tabla de Frecuencias
    st.subheader("Distribución y Tabla de Frecuencias")
    st.plotly_chart(create_histogram_with_kde(numbers, k), use_container_width=True, config=PLOTLY_CONFIG)

    # Tabla con Fila de Totales
    st.dataframe(
        df_freq, 
        use_container_width=True, 
        hide_index=True
    )

    st.markdown("---")

    # 4. Medidas Estadísticas con Resalte de Resultados (KPIs)
    st.subheader("Medidas Estadísticas Descriptivas")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-title">Tendencia Central</div>
            <div class="metric-row">
                <span class="metric-label">Media (x̄):</span>
                <span class="metric-value highlight-value">{s['mean']:,.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Mediana:</span>
                <span class="metric-value">{s['median']:,.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Moda:</span>
                <span class="metric-value">{f"{s['mode']:,.2f}" if s['mode'] is not None else 'N/A'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-title">Dispersión Muestral (n - 1)</div>
            <div class="metric-row">
                <span class="metric-label">Varianza (S²):</span>
                <span class="metric-value">{s['var_sample']:,.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Desviación Est. (S):</span>
                <span class="metric-value highlight-value">{s['std_sample']:,.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Coef. Variación (CV):</span>
                <span class="metric-value">{s['cv_sample']:.2f}%</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Rango Intercuartil (IQR):</span>
                <span class="metric-value">{s['iqr']:,.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-title">Dispersión Poblacional (N)</div>
            <div class="metric-row">
                <span class="metric-label">Varianza (σ²):</span>
                <span class="metric-value">{s['var_pop']:,.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Desviación Est. (σ):</span>
                <span class="metric-value highlight-value">{s['std_pop']:,.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Coef. Variación (CV):</span>
                <span class="metric-value">{s['cv_pop']:.2f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 5. Forma de la Distribución
    col_s1, col_s2 = st.columns(2)
    skew_desc = "Simétrica" if abs(s['skewness']) < 0.5 else ("Asimétrica Positiva (Sesgo a la Derecha)" if s['skewness'] > 0 else "Asimétrica Negativa (Sesgo a la Izquierda)")
    kurt_desc = "Mesocúrtica (Distribución Normal)" if abs(s['kurtosis']) < 0.5 else ("Leptocúrtica (Elevada concentración)" if s['kurtosis'] > 0 else "Platocúrtica (Gran dispersión)")

    col_s1.info(f"**Asimetría / Sesgo (Skewness):** {s['skewness']:.4f}\n\n*Interpretación:* {skew_desc}")
    col_s2.info(f"**Curtosis (Kurtosis):** {s['kurtosis']:.4f}\n\n*Interpretación:* {kurt_desc}")