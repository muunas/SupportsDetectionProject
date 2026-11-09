import math

from distance import precio_actual

"""
Calculadora DCA (Opción 1).

La idea: se compra SIEMPRE el mismo numero de acciones X en cada nivel.
La perdida total si salta el stoploss (que es comun a todos los niveles) debe
ser lo mas cercana posible a la apuesta total, pero SIEMPRE por debajo.

    X * (E1 - SL) + X * (E2 - SL) + ... + X * (En - SL) = Total
    X = Total / suma(Ei - SL)

Como X casi nunca es un numero finito "bonito", se trunca (no se redondea)
a 3 decimales para garantizar que el riesgo total nunca supere la apuesta.
"""


def truncar(valor, decimales=3):
    factor = 10 ** decimales
    return math.floor(valor * factor) / factor


def calcular_dca(niveles, stoploss, apuesta_total):
    """
    Devuelve un dict con el desglose del calculo DCA.

    Parametros:
        niveles         -> lista de precios de entrada (floats)
        stoploss        -> precio de stoploss (float), menor que el nivel mas bajo
        apuesta_total   -> riesgo total que se quiere asumir (float)

    Lanza ValueError si los datos no son validos.
    """
    if not niveles:
        raise ValueError("Debes indicar al menos un nivel.")

    if apuesta_total <= 0:
        raise ValueError("La apuesta total debe ser mayor que 0.")

    nivel_minimo = min(niveles)
    if stoploss >= nivel_minimo:
        raise ValueError(
            f"El stoploss ({stoploss}) debe ser menor que el nivel mas bajo ({nivel_minimo})."
        )

    # Suma de distancias (entrada - stoploss) de todos los niveles.
    suma_distancias = sum(nivel - stoploss for nivel in niveles)
    if suma_distancias <= 0:
        raise ValueError("La suma de distancias hasta el stoploss no es valida.")

    acciones_por_nivel = truncar(apuesta_total / suma_distancias, 3)

    desglose = []
    for i, nivel in enumerate(niveles, start=1):
        coste = acciones_por_nivel * nivel
        riesgo = acciones_por_nivel * (nivel - stoploss)
        desglose.append({
            "nivel": i,
            "precio": nivel,
            "acciones": acciones_por_nivel,
            "coste": coste,
            "riesgo": riesgo,
        })

    riesgo_total = sum(d["riesgo"] for d in desglose)
    coste_total = sum(d["coste"] for d in desglose)
    acciones_totales = acciones_por_nivel * len(niveles)

    return {
        "acciones_por_nivel": acciones_por_nivel,
        "desglose": desglose,
        "riesgo_total": riesgo_total,
        "coste_total": coste_total,
        "acciones_totales": acciones_totales,
        "apuesta_total": apuesta_total,
        "stoploss": stoploss,
    }


# ==========================
# INTERFAZ INTERACTIVA (CLI)
# ==========================

def _pedir_numero(mensaje):
    while True:
        try:
            return float(input(mensaje).strip().replace(",", "."))
        except ValueError:
            print("Valor invalido, introduce un numero.")


def _pedir_entero(mensaje):
    while True:
        try:
            return int(input(mensaje).strip())
        except ValueError:
            print("Valor invalido, introduce un numero entero.")


def _estado_nivel(precio, precio_actual_valor):
    """Marca si el nivel aun no se ha alcanzado o si el precio ya esta por debajo."""
    if precio_actual_valor is None:
        return "-"
    return "esperando" if precio_actual_valor > precio else "activo (<= actual)"


def ejecutar_calculadora():
    print("\n==============================================")
    print(" CALCULADORA DCA")
    print("==============================================")

    # 1. Numero de niveles
    n = _pedir_entero("Cuantos niveles quieres? ")
    if n < 1:
        print("Debe haber al menos 1 nivel.\n")
        return

    # 2. Precios de los niveles
    niveles = []
    for i in range(1, n + 1):
        niveles.append(_pedir_numero(f"Precio del nivel {i}: "))

    # 3. Stoploss
    stoploss = _pedir_numero("Precio del stoploss: ")

    # 4. Apuesta total
    apuesta_total = _pedir_numero("Apuesta total (riesgo maximo, ej 140): ")

    # 5. Ticker -> precio actual (solo informativo, no interviene en el calculo)
    ticker = input("Ticker (ej. GOOGL): ").strip().upper()
    precio_actual_valor = precio_actual(ticker) if ticker else None

    # Calculo
    try:
        resultado = calcular_dca(niveles, stoploss, apuesta_total)
    except ValueError as e:
        print(f"[ERROR] {e}\n")
        return

    _imprimir_resultado(ticker, precio_actual_valor, resultado)


def _imprimir_resultado(ticker, precio_actual_valor, resultado):
    precio_actual_str = f"{precio_actual_valor:.2f}" if precio_actual_valor is not None else "N/A"

    print("\n" + "-" * 70)
    print(f"Ticker: {ticker or 'N/A'} | Precio actual: {precio_actual_str}")
    print(f"Apuesta total: {resultado['apuesta_total']:.2f} | Stoploss: {resultado['stoploss']:.2f}")
    print(f"Acciones por nivel: {resultado['acciones_por_nivel']}")
    print("-" * 70)

    print(f"{'Nivel':<6}{'Precio':>10}{'Acciones':>10}{'Coste($)':>12}{'Riesgo($)':>12}   Estado")
    for d in resultado["desglose"]:
        estado = _estado_nivel(d["precio"], precio_actual_valor)
        print(
            f"{d['nivel']:<6}"
            f"{d['precio']:>10.2f}"
            f"{d['acciones']:>10.3f}"
            f"{d['coste']:>12.2f}"
            f"{d['riesgo']:>12.2f}"
            f"   {estado}"
        )

    print("-" * 70)
    print(
        f"{'TOTAL':<6}"
        f"{'':>10}"
        f"{resultado['acciones_totales']:>10.3f}"
        f"{resultado['coste_total']:>12.2f}"
        f"{resultado['riesgo_total']:>12.2f}"
    )

    # Verificacion de que el riesgo esta por debajo de la apuesta
    if resultado["riesgo_total"] <= resultado["apuesta_total"]:
        margen = resultado["apuesta_total"] - resultado["riesgo_total"]
        print(f"\nRiesgo total {resultado['riesgo_total']:.2f} <= apuesta {resultado['apuesta_total']:.2f} (margen {margen:.2f})")
    else:
        # No deberia ocurrir gracias al truncado, pero se avisa por seguridad.
        print(f"\n[WARN] El riesgo total {resultado['riesgo_total']:.2f} supera la apuesta {resultado['apuesta_total']:.2f}")

    print()
