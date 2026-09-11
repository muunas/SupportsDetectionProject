import argparse
import subprocess
import os
import json
import time
import sys
import mplfinance as mpf
import matplotlib.pyplot as plt

from fetcher import descargar_velas_semanales
from supports import detectar_soportes
from yahooquery import Ticker
from distance import calcular_distancia
from filter import filterfunc
from distance import precio_actual


years = 3
max_pct = 5
ventana = 2
visualizer = True  
CONFIG_PATH = "config.json"




def cargar_ruta_ticker():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            return data.get("ruta_ticker")
    return None

def guardar_ruta_ticker(ruta):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"ruta_ticker": ruta}, f)

def obtener_ruta_ticker():
    ruta = cargar_ruta_ticker()
    if ruta and os.path.exists(ruta):
        return ruta
    
    print("No se ha encontrado la ruta del ticker.json.")
    ruta = input("Introduce la ruta completa del ticker.json: ").strip()
    guardar_ruta_ticker(ruta)
    return ruta



def imprimir_porcentajes_coloreados(resultados):
    VERDE = "\033[92m"
    ROJO = "\033[91m"
    RESET = "\033[0m"

    for simbolo, pct in resultados:
        color = VERDE if pct >= 0 else ROJO
        print(f"{simbolo}: {color}{pct:.2f}%{RESET}")

def plot_ticker_with_supports(df, supports, ticker):
    df = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    })

    soporte_vals = [s["valor"] for s in supports]
    precio_act = df["Close"].iloc[-1]

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    mpf.plot(
        df,
        type='candle',
        ax=ax,
        style='nightclouds',
        show_nontrading=True
    )

    for s in soporte_vals:
        ax.axhline(s, color='#4da6ff', linestyle='--', alpha=0.9)

    ax.scatter(
        df.index[-1],
        precio_act,
        color='#ff4d4d',
        s=80,
        label='Current Price'
    )

    ax.legend(facecolor="black", edgecolor="white", labelcolor="white")
    ax.tick_params(colors="white")
    plt.title(f"{ticker} - Supports & Current Price", color="white")

    plt.tight_layout()
    plt.show()


# ==========================
# PIPELINE PRINCIPAL
# ==========================

def analizar_cambios_porcentuales(rticker):
    with open(rticker, "r") as f:
        tickers = json.load(f)["tickers"]

    t = Ticker(tickers)
    hist = t.history(period="2d", interval="1d")

    resultados = []

    for simbolo in tickers:
        try:
            df = hist.loc[simbolo]
            precios = df["close"].tolist()

            if len(precios) < 2:
                continue

            pct = ((precios[-1] - precios[-2]) / precios[-2]) * 100
            resultados.append((simbolo, pct))

        except Exception:
            continue

    resultados.sort(key=lambda x: x[1])
    return resultados


def ejecutar_pipeline(rticker, data):
    print("\n==============================================")
    print(" INICIANDO SCREENER DE SOPORTES")
    print("==============================================\n")

    tickers = data["tickers"]
    total = len(tickers)

    print(f"Tickers cargados: {total}")
    print(f"Años analizados: {years}")
    print(f"Máx % distancia: {max_pct}")
    print(f"Visualizer: {'ON' if visualizer else 'OFF'}\n")

    for i, simbolo in enumerate(tickers, start=1):
        print(f"\n[{i}/{total}] Analizando {simbolo}...")
        print("----------------------------------------------")

        df_weekly = descargar_velas_semanales(simbolo, years)
        if df_weekly is None:
            print(f"[SKIP] No hay datos para {simbolo}")
            continue

        soportes = detectar_soportes(df_weekly, ventana)
        precio = precio_actual(simbolo)

        print(f"Precio actual: {precio}")

        distancias = calcular_distancia(df_weekly, soportes, simbolo)
        cercanos = filterfunc(distancias, max_pct)

        print("Soportes cercanos:")
        if cercanos == ["NONE"]:
            print("→ Ninguno dentro del rango")
        else:
            if visualizer:
                plot_ticker_with_supports(df_weekly, soportes, simbolo)

            for c in cercanos:
                print("→", c)

    print("\n==============================================")
    print(" SCREENER COMPLETADO")
    print("==============================================\n")


# ==========================
# COMANDOS
# ==========================

def abrir_editor(rticker):
    print("\nAbriendo ticker.json...")
    subprocess.Popen(["notepad.exe", rticker])
    print("Puedes editar los tickers y guardar.\n")

def mostrar_menu():
    print("\n==============================================")
    print(" COMANDOS DISPONIBLES")
    print("==============================================")
    print(" supports      → Analisis de soportes")
    print(" edit_tickers → Editar ticker.json")
    print(" pctchanges   → Analisis de cambios porcentuales")
    print(" set_years    → Cambiar años analizados")
    print(" viz_on       → Activar visualizador")
    print(" viz_off      → Desactivar visualizador")
    print(" exit         → Salir del programa")
    print("==============================================\n")


# ==========================
# MAIN
# ==========================

def main():
    global years, visualizer

    ruta_ticker = obtener_ruta_ticker()

    with open(ruta_ticker, "r") as f:
        data = json.load(f)

    print("\n==============================================")
    print(" CONFIGURACIÓN ACTUAL")
    print("==============================================")
    print(f"Years: {years}")
    print(f"Visualizer: {'ON' if visualizer else 'OFF'}")
    print("==============================================\n")

    mostrar_menu()

    while True:
        comando = input(">>> ").strip().lower()

        if comando == "supports":
            ejecutar_pipeline(ruta_ticker, data)

        elif comando == "edit_tickers":
            abrir_editor(ruta_ticker)

        elif comando == "pctchanges":
            resultados = analizar_cambios_porcentuales(ruta_ticker)
            imprimir_porcentajes_coloreados(resultados)

        elif comando == "set_years":
            try:
                nuevo = int(input("Nuevo valor para years: "))
                years = nuevo
                print(f"Years actualizado a {years}\n")
            except:
                print("Valor inválido.\n")

        elif comando == "viz_on":
            visualizer = True
            print("Visualizer activado.\n")

        elif comando == "viz_off":
            visualizer = False
            print("Visualizer desactivado.\n")

        elif comando == "exit":
            print("\nCerrando programa...")
            time.sleep(1)
            break

        else:
            print("Comando no reconocido.\n")


if __name__ == "__main__":
    main()
