import numpy as np
import pandas as pd
from scipy import stats
import math

def process_raw_data(raw_text):
    if not raw_text or not raw_text.strip():
        return []
    # Reemplaza comas por espacios y divide los tokens
    clean_text = raw_text.replace(',', ' ')
    tokens = clean_text.split()
    numbers = []
    for t in tokens:
        try:
            numbers.append(float(t))
        except ValueError:
            pass
    return numbers

def get_max_decimals(data):
    """Detecta el número máximo de decimales presentes en el conjunto de datos."""
    max_d = 0
    for val in data:
        str_val = str(val).rstrip('0').rstrip('.')
        if '.' in str_val:
            d = len(str_val.split('.')[1])
            if d > max_d:
                max_d = d
    return max_d

def calculate_sturges_k(n):
    """Calcula k por Sturges y devuelve el número IMPAR más cercano."""
    k_raw = 1 + 3.322 * np.log10(n)
    
    # Evalúa impares candidatos alrededor del valor real
    k_lower = math.floor(k_raw)
    if k_lower % 2 == 0:
        k_lower -= 1  # Forzar a impar inferior
        
    candidato1 = k_lower
    candidato2 = k_lower + 2
    
    # Elige el impar con menor distancia absoluta al valor real
    if abs(k_raw - candidato1) <= abs(k_raw - candidato2):
        return max(1, candidato1)
    else:
        return candidato2

def generate_frequency_table_intervals(data, custom_k=None):
    n = len(data)
    min_val = min(data)
    max_val = max(data)
    range_val = max_val - min_val

    # 1. Determinar K
    if custom_k is not None and custom_k > 0:
        k = int(custom_k)
    else:
        k = calculate_sturges_k(n)

    # 2. Determinar Amplitud (A) respetando la naturaleza de los datos
    max_d = get_max_decimals(data)
    raw_width = range_val / k if k > 0 else 1.0

    if max_d == 0:
        # Datos Enteros
        if raw_width.is_integer():
            width = int(raw_width)
        else:
            width = math.ceil(raw_width)
    else:
        # Datos con Decimales: Ajustar a max_d decimales redondeando al alza el último dígito
        factor = 10 ** max_d
        width = math.ceil(raw_width * factor) / factor
        # Si por precisión queda exacto al raw, incrementamos el paso mínimo
        if width * k <= range_val:
            width += 1 / factor

    # 3. Construir Intervalos y Métricas
    bins = [min_val + i * width for i in range(k + 1)]
    counts, _ = np.histogram(data, bins=bins)

    rows = []
    f_acum = 0
    f_desacum = n

    for i in range(k):
        f = counts[i]
        fr = f / n
        fp = fr * 100
        f_acum += f
        
        lower = bins[i]
        upper = bins[i+1]
        xi = (lower + upper) / 2
        
        # Formato numérico adaptado
        if max_d == 0:
            interval_str = f"[{int(lower)} - {int(upper)})" if i < k-1 else f"[{int(lower)} - {int(upper)}]"
            xi_str = f"{xi:,.1f}" if xi % 1 != 0 else f"{int(xi)}"
        else:
            interval_str = f"[{lower:,.{max_d}f} - {upper:,.{max_d}f})" if i < k-1 else f"[{lower:,.{max_d}f} - {upper:,.{max_d}f}]"
            xi_str = f"{xi:,.{max_d+1}f}"

        rows.append({
            "Intervalo de Clase": interval_str,
            "Marca (Xi)": xi_str,
            "Frec. Abs (f)": int(f),
            "Frec. Rel (fr)": round(fr, 4),
            "Frec. Porc (f%)": f"{fp:.2f}%",
            "Frec. Acum (F)": int(f_acum),
            "Frec. Desacum (F_des)": int(f_desacum)
        })
        f_desacum -= f

    df = pd.DataFrame(rows)

    # 4. Fila de Totales
    total_row = pd.DataFrame([{
        "Intervalo de Clase": "TOTAL",
        "Marca (Xi)": "—",
        "Frec. Abs (f)": int(df["Frec. Abs (f)"].sum()),
        "Frec. Rel (fr)": round(df["Frec. Rel (fr)"].sum(), 2),
        "Frec. Porc (f%)": "100.00%",
        "Frec. Acum (F)": "—",
        "Frec. Desacum (F_des)": "—"
    }])

    df_with_total = pd.concat([df, total_row], ignore_index=True)

    return df_with_total, k, width

def generate_frequency_table_discrete(data):
    n = len(data)
    unique_vals, counts = np.unique(data, return_counts=True)
    
    rows = []
    f_acum = 0
    f_desacum = n
    
    for val, f in zip(unique_vals, counts):
        fr = f / n
        fp = fr * 100
        f_acum += f
        
        val_str = f"{int(val)}" if val % 1 == 0 else f"{val:,.2f}"
        
        rows.append({
            "Valor (X)": val_str,
            "Frec. Abs (f)": int(f),
            "Frec. Rel (fr)": round(fr, 4),
            "Frec. Porc (f%)": f"{fp:.2f}%",
            "Frec. Acum (F)": int(f_acum),
            "Frec. Desacum (F_des)": int(f_desacum)
        })
        f_desacum -= f

    df = pd.DataFrame(rows)

    # Fila de Totales para discreta
    total_row = pd.DataFrame([{
        "Valor (X)": "TOTAL",
        "Frec. Abs (f)": int(df["Frec. Abs (f)"].sum()),
        "Frec. Rel (fr)": round(df["Frec. Rel (fr)"].sum(), 2),
        "Frec. Porc (f%)": "100.00%",
        "Frec. Acum (F)": "—",
        "Frec. Desacum (F_des)": "—"
    }])

    return pd.concat([df, total_row], ignore_index=True)

def calculate_descriptive_stats(data):
    np_data = np.array(data)
    n = len(np_data)
    
    mean_val = float(np.mean(np_data))
    median_val = float(np.median(np_data))
    
    # Moda
    mode_res = stats.mode(np_data, keepdims=True)
    mode_val = float(mode_res.mode[0]) if len(mode_res.mode) > 0 else None

    # Varianza y Desviación
    var_sample = float(np.var(np_data, ddof=1)) if n > 1 else 0.0
    std_sample = float(np.std(np_data, ddof=1)) if n > 1 else 0.0
    cv_sample = (std_sample / mean_val * 100) if mean_val != 0 else 0.0

    var_pop = float(np.var(np_data, ddof=0))
    std_pop = float(np.std(np_data, ddof=0))
    cv_pop = (std_pop / mean_val * 100) if mean_val != 0 else 0.0

    # Cuartiles y Percentiles
    q1 = float(np.percentile(np_data, 25))
    q3 = float(np.percentile(np_data, 75))
    iqr = q3 - q1

    percentile_keys = [10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95]
    percentiles = {f"P{p}": float(np.percentile(np_data, p)) for p in percentile_keys}

    skewness = float(stats.skew(np_data)) if n > 2 else 0.0
    kurtosis = float(stats.kurtosis(np_data)) if n > 3 else 0.0

    return {
        "n": n,
        "min": float(np.min(np_data)),
        "max": float(np.max(np_data)),
        "mean": mean_val,
        "median": median_val,
        "mode": mode_val,
        "var_sample": var_sample,
        "std_sample": std_sample,
        "cv_sample": cv_sample,
        "var_pop": var_pop,
        "std_pop": std_pop,
        "cv_pop": cv_pop,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "percentiles": percentiles,
        "skewness": skewness,
        "kurtosis": kurtosis
    }