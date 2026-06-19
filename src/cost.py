import math
from graph import Cidade, Aresta, Grafo


# Coeficientes da formulação VSP adotada como referência. O projeto não
# reivindica que estes valores estejam calibrados para uma classe veicular
# específica.
G = 9.81             # aceleração gravitacional [m/s²]
FR_G = 0.132         # f_r * g [m/s²] — resistência de rolamento (Jiménez-Palacios, 1999)
C_AERO = 0.000302    # coeficiente aerodinâmico específico [m^-1] (Jiménez-Palacios, 1999)


def calcular_energia(origem: Cidade,destino: Cidade,aresta: Aresta, velocidade_ms: float) -> float:
    d_m = aresta.dist_km * 1000.0

    if aresta.alt_passo_m is not None:
        delta_h = aresta.alt_passo_m - origem.altitude_m
        if delta_h < 0:
            delta_h = destino.altitude_m - origem.altitude_m
    else:
        delta_h = destino.altitude_m - origem.altitude_m

    ganho_altimetrico = max(0.0, delta_h) # evita ganho negativo

    E_gravidade = G * ganho_altimetrico
    E_rolamento = FR_G * d_m
    E_aerodinamica = C_AERO * (velocidade_ms ** 2) * d_m

    return E_gravidade + E_rolamento + E_aerodinamica


def verificar_pesos_positivos(grafo: Grafo, velocidade_ms: float)-> list:
    negativas = []

    for cidade_nome, arestas in grafo.adj.items():
        for aresta in arestas:
            origem = grafo.cidades[cidade_nome]
            destino = grafo.cidades[aresta.destino]

            e = calcular_energia(origem, destino, aresta, velocidade_ms)

            if e < 0:
                negativas.append((cidade_nome, aresta.destino, e))

    return negativas
