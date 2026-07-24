import numpy as np
import pandas as pd
from scipy import stats

def process_raw_data(data_text):
    if not data_text:
        return []
    cleaned_text = data_text.replace(',', ' ').replace('\n', ' ')
    tokens = cleaned_text.split()
    numbers = []
    for token in tokens:
        try:
            numbers.append(float(token))
        except ValueError:
            continue
    return numbers

def calculate_descriptive_stats(numbers):
    arr = np.array(numbers)
    n = len(arr)
    if n == 0:
        return {}

    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))
    
    mode_res = stats.mode(arr, keepdims=True)
    mode_val = mode_res.mode[0] if len(mode_res.mode) > 0 else None
    
    var_sample = float(np.var(arr, ddof=1)) if n > 1 else 0.0
    std_sample = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    cv_sample = (std_sample / mean_val * 100) if mean_val != 0 else 0.0

    var_pop = float(np.var(arr, ddof=0))
    std_pop = float(np.std(arr, ddof=0))
    cv_pop = (std_pop / mean_val * 100) if mean_val != 0 else 0.0

    min_val = float(np.min(arr))
    max_val = float(np.max(arr))
    q1 = float(np.percentile(arr, 25))
    q3 = float(np.percentile(arr, 75))
    iqr = q3 - q1

    skewness = float(stats.skew(arr)) if n > 2 else 0.0
    kurtosis = float(stats.kurtosis(arr)) if n > 3 else 0.0

    percentiles = {f"P{p}": float(np.percentile(arr, p)) for p in [10, 20, 25, 30, 40, 50, 60, 70, 80, 90, 95]}

    return {
        "n": n, "mean": mean_val, "median": median_val, "mode": mode_val,
        "min": min_val, "max": max_val, "q1": q1, "q3": q3, "iqr": iqr,
        "var_sample": var_sample, "std_sample": std_sample, "cv_sample": cv_sample,
        "var_pop": var_pop, "std_pop": std_pop, "cv_pop": cv_pop,
        "skewness": skewness, "kurtosis": kurtosis, "percentiles": percentiles
    }

def generate_frequency_table_intervals(numbers, custom_k=None):
    n = len(numbers)
    if n < 2:
        return pd.DataFrame(), 0, 0

    if custom_k is not None and custom_k > 0:
        k = int(custom_k)
    else:
        k_raw = int(np.ceil(1 + 3.322 * np.log10(n)))
        k = k_raw if k_raw % 2 != 0 else k_raw + 1

    min_val = np.min(numbers)
    max_val = np.max(numbers)
    rango = max_val - min_val
    width = rango / k if k > 0 else 1

    bins = [min_val + i * width for i in range(k + 1)]
    bins[-1] = max_val + 1e-9

    counts, _ = np.histogram(numbers, bins=bins)
    
    rows = []
    f_acum = 0
    f_desacum = n

    for i in range(k):
        l_inf = bins[i]
        l_sup = bins[i+1]
        marca = (l_inf + l_sup) / 2
        f = counts[i]
        fr = f / n
        fp = fr * 100
        f_acum += f

        rows.append({
            "Intervalo de Clase": f"[{l_inf:,.2f} - {l_sup:,.2f})",
            "Marca de Clase (Xi)": round(marca, 2),
            "Frec. Absoluta (f)": f,
            "Frec. Relativa (fr)": round(fr, 4),
            "Frec. Porcentual (f%)": f"{fp:.2f}%",
            "Frec. Acumulada (F)": f_acum,
            "Frec. Desacumulada (F_des)": f_desacum
        })
        f_desacum -= f

    return pd.DataFrame(rows), k, width

def generate_frequency_table_discrete(numbers):
    n = len(numbers)
    if n < 1:
        return pd.DataFrame()

    unique_vals, counts = np.unique(numbers, return_counts=True)
    rows = []
    f_acum = 0
    f_desacum = n

    for val, f in zip(unique_vals, counts):
        fr = f / n
        fp = fr * 100
        f_acum += f
        rows.append({
            "Valor (X)": round(val, 2),
            "Frec. Absoluta (f)": f,
            "Frec. Relativa (fr)": round(fr, 4),
            "Frec. Porcentual (f%)": f"{fp:.2f}%",
            "Frec. Acumulada (F)": f_acum,
            "Frec. Desacumulada (F_des)": f_desacum
        })
        f_desacum -= f

    return pd.DataFrame(rows)