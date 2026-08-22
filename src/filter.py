"""
Funcion que filtra los resultados de distancias según un porcentaje máximo dado. 
Si no hay resultados que cumplan con el criterio, devuelve ["NONE"].
"""

def filterfunc(distancias, max_pct=5):
    filtrados = []

    for d in distancias:
        if d["distancia_pct"] <= max_pct:
            filtrados.append(d)
            

    if not filtrados:
        return ["NONE"]

    return filtrados
