"""
cost.py — Função de custo energético baseada no modelo VSP

Referência principal:
    Gonçalves, G.A., Mendes, T. & Coelho, M. (2016). Impact of driving
    styles on greenhouse gas emissions from urban freight distribution.
    Transportation Research Part D, 46, 15-31.
    DOI: https://doi.org/10.1016/j.trd.2016.03.009

    Os coeficientes FR_G=0,132 e C_AERO=0,000302 são validados para HDV
    (veículo pesado de carga) a 80 km/h em cruzeiro constante, produzindo
    VSP ≈ 6,25 kW/t em pista plana e ≈ 10,60 kW/t em aclive de 2%,
    enquadrando-se nos Modos 5 e 7 da classificação VSP.

Referência original da fórmula VSP:
    Jiménez-Palacios, J.L. (1999). MIT Thesis, conforme citado em
    Jiang et al. (2025), Atmosphere 16(2):143,
    DOI: https://doi.org/10.3390/atmos16020143
"""

import math
from graph import Cidade, Aresta, Grafo


# Coeficientes VSP — Jiménez-Palacios (1999), conforme Jiang et al. (2025)
# Aplicabilidade a veículos pesados (HDV) validada por Gonçalves et al. (2016),
# que aplicaram o modelo VSP a frotas de distribuição urbana de carga na Europa,
# demonstrando que os coeficientes da formulação original se mantêm coerentes
# para HDV em regime de cruzeiro.
G = 9.81             # aceleração gravitacional [m/s²]
FR_G = 0.132         # f_r * g [m/s²] — resistência de rolamento (Jiménez-Palacios, 1999)
C_AERO = 0.000302    # coeficiente aerodinâmico específico [(m/s)^-2] (Jiménez-Palacios, 1999)


def calcular_energia(origem: Cidade,destino: Cidade,aresta: Aresta, velocidade_ms: float) -> float:
    """
    Calcula a energia específica de travessia da aresta u -> v [J/kg].

    Derivação (Jiménez-Palacios, 1999, adaptado):
        VSP = v * (9.8*s + 0.132) + 0.000302 * v³     [kW/t]
        E   = VSP * (d/v) = 9.8*Δh + 0.132*d + 0.000302*v²*d  [J/kg]

    Parâmetros:
        origem, destino : objetos Cidade com altitude_m
        aresta          : Aresta com dist_km e alt_passo_m (opcional)
        velocidade_ms   : velocidade de cruzeiro em m/s

    Retorna:
        Energia específica em J/kg (pode ser negativa em descidas íngremes,
        mas com os dados desta rota todas as arestas ficam positivas).

    Tratamento especial para passos andinos:
        Se aresta.alt_passo_m está definida, a subida é calculada até
        a cota do passo (a descida é dissipada na frenagem, sem recuperação).
        Isso evita subestimar o custo energético de cruzar os Andes.
    """
    d_m = aresta.dist_km * 1000.0

    if aresta.alt_passo_m is not None:
        # Subida até o pico do passo; descida dissipada (sem regeneração)
        delta_h = aresta.alt_passo_m - origem.altitude_m
        # Se a cota do passo for menor que a origem (ex.: trajeto inverso
        # descendo antes de subir), usa o Δh ponta-a-ponta como fallback.
        if delta_h < 0:
            delta_h = destino.altitude_m - origem.altitude_m
    else:
        # Δh ponta-a-ponta (funciona bem para trechos sem pico intermediário)
        delta_h = destino.altitude_m - origem.altitude_m

    # --- três termos da equação de energia ---
    E_gravidade    = G * delta_h                       # 9.81 * Δh
    E_rolamento    = FR_G * d_m                        # 0.132 * d
    E_aerodinamica = C_AERO * (velocidade_ms ** 2) * d_m  # 0.000302 * v² * d

    return E_gravidade + E_rolamento + E_aerodinamica


def verificar_pesos_positivos(grafo: Grafo, velocidade_ms: float) -> list:
    """
    Verifica se alguma aresta tem custo negativo.
    IMPORTANTE: Dijkstra só é correto para pesos >= 0.
    Se houver pesos negativos, usar Bellman-Ford.

    Retorna lista de arestas negativas (vazia = tudo ok para Dijkstra).
    """
    negativas = []
    for cidade_nome, arestas in grafo.adj.items():
        for aresta in arestas:
            origem = grafo.cidades[cidade_nome]
            destino = grafo.cidades[aresta.destino]
            e = calcular_energia(origem, destino, aresta, velocidade_ms)
            if e < 0:
                negativas.append((cidade_nome, aresta.destino, e))
    return negativas