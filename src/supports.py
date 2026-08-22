import pandas as pd

"""
Función que detecta soportes en un dataframe de velas semanales. 
Un soporte se define como un mínimo pivot que no ha sido roto por los cierres posteriores y debe de cumplir con un criterio de ventana (window) para ser considerado válido.
"""

def detectar_soportes(df_weekly, window):
    lows = df_weekly["low"]
    closes = df_weekly["close"]

    soportes_validos = []

    for i in range(window, len(df_weekly) - window):

        # 1. Detectar pivot mínimo
        ventana = lows.iloc[i-window : i+window+1]
        if lows.iloc[i] != ventana.min():
            continue

        soporte = lows.iloc[i]

        # 2. Validar que el soporte no fue roto
        posteriores = closes.iloc[i+1:]
        if (posteriores < soporte).any():
            continue

        # 3. Guardar soporte válido
        soportes_validos.append({
            "fecha": df_weekly.index[i],
            "valor": soporte
        })

    return soportes_validos
