import argparse
import subprocess
import os
import json
import time
import sys


from fetcher import descargar_velas_semanales
from supports import detectar_soportes
from yahooquery import Ticker
from distance import calcular_distancia
from filter import filterfunc
from distance import precio_actual

## CONFIGURACIÓN
ruta_ticker = r"..." ## Cambiar a la ruta de tu ticker.json
years = 1
max_pct = 5
ventana = 2

##FUNCIONES PRINCIPALES
def ejecutar_pipeline():
    print("\n==============================================")
    print(" INICIANDO SCREENER DE SOPORTES")
    print("==============================================\n")

    # Cargar tickers
    with open(ruta_ticker, "r") as f:
        data = json.load(f)

    tickers = data["tickers"]
    total = len(tickers)

    print(f"Tickers cargados: {total}")
    print(f"Años analizados: {years}")
    print(f"Máx % distancia: {max_pct}\n")

    # Loop principal
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
        if not cercanos:
            print("→ Ninguno dentro del rango")
        else:
            for c in cercanos:
                print("→", c)

    print("\n==============================================")
    print(" SCREENER COMPLETADO")
    print("==============================================\n")



## COMANDOS DE USUARIO

def abrir_editor():
    print("\nAbriendo ticker.json...")
    subprocess.Popen(["notepad.exe", ruta_ticker])
    print("Puedes editar los tickers y guardar.\n")


def mostrar_menu():
    print("\n==============================================")
    print(" COMANDOS DISPONIBLES")
    print("==============================================")
    print(" start  → Ejecutar screener")
    print(" edit   → Editar ticker.json")
    print(" exit   → Salir del programa")
    print("==============================================\n")


## MAIN
def main():
    mostrar_menu()

    while True:
        comando = input(">>> ").strip().lower()

        if comando == "start":
            ejecutar_pipeline()

        elif comando == "edit":
            abrir_editor()

        elif comando == "exit":
            print("\nCerrando programa...")
            time.sleep(1)
            break

        else:
            print("Comando no reconocido. Usa: start, edit, exit.\n")


## Punto de entrada

if __name__ == "__main__":
    main()

