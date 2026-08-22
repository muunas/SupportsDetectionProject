from yahooquery import Ticker

"""
Esta funcion nos permite obtener el precio actual de un ticker y gestionar posibles errores, 
devolviendo None si no se puede obtener el precio.
"""

def precio_actual(ticker):
    try:
        t = Ticker(ticker)
        data = t.price.get(ticker)

        if not data:
            print(f"[WARN] No hay precio para {ticker}")
            return None

        precio = data.get("regularMarketPrice")

        if precio is None:
            print(f"[WARN] Precio None para {ticker}")
            return None

        return precio

    except Exception as e:
        print(f"[ERROR] Fallo obteniendo precio de {ticker}: {e}")
        return None


"""
Calcula la distancia porcentual entre el precio actual y cada soporte detectado. 
Devuelve un listado para que sea mas limpio printear los resultados.
"""

def calcular_distancia(df_weekly, soportes, ticker):


    precio = precio_actual(ticker)
    if precio is None:
        return []  

    resultados = []

    for s in soportes:
        soporte_valor = round(s["valor"], 2)

        distancia_abs = round(abs(precio - soporte_valor), 2)
        distancia_pct = round((distancia_abs / soporte_valor) * 100, 2)

        resultados.append({
            "fecha": s["fecha"],
            "valor": soporte_valor,
            "distancia_pct": distancia_pct
        })


    return resultados
