from yahooquery import Ticker
import pandas as pd

"""
Este es el primer modulo que tocamos, su función es descargar los datos de las velas diarias del ticker
que queramos, gestionas posibles errores como que no haya datos, que yahoo no devuelva la columna 'symbol', etc.,
en cuyo caso devuelve None. Finalmente convierte las velas diarias en velas semanales y devuelve un dataframe.
"""

def descargar_velas_semanales(ticker, años):
    try:
        t = Ticker(ticker)

        df = t.history(period=f"{años}y", interval="1d")


        if df is None or df.empty:
            print(f"[WARN] No hay datos históricos para {ticker}")
            return None

        # Aplanar MultiIndex
        df = df.reset_index()


        if "symbol" not in df.columns:
            print(f"[WARN] Yahoo no devolvió columna 'symbol' para {ticker}")
            return None

        # Filtrar por símbolo
        df = df[df["symbol"] == ticker]

        if df.empty:
            print(f"[WARN] Yahoo no devolvió datos válidos para {ticker}")
            return None

        # Convertir fecha
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        # Convertir a velas semanales
        df_weekly = df.resample("W").agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        })

        df_weekly = df_weekly.dropna()

        if df_weekly.empty:
            print(f"[WARN] No se pudieron generar velas semanales para {ticker}")
            return None

        return df_weekly

    except Exception as e:
        print(f"[ERROR] Fallo descargando {ticker}: {e}")
        return None
