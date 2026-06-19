"""
cost.py — Função de custo energético baseada no modelo VSP

Referência original da fórmula VSP:
    Jiménez-Palacios, J.L. (1999). Understanding and Quantifying Motor
    Vehicle Emissions with Vehicle Specific Power and TILDAS Remote Sensing.
    Ph.D. Thesis, Massachusetts Institute of Technology.
    http://hdl.handle.net/1721.1/44505

Referência de apoio sobre inclinação da via e velocidade:
    Jiang, B. et al. (2025). Impact of Road Gradient on Fuel Consumption of
    Light-Duty Diesel Vehicles. Atmosphere, 16(2):143.
    DOI: https://doi.org/10.3390/atmos16020143

Escopo:
    A integração da expressão VSP em energia específica, com velocidade
    constante e aceleração longitudinal nula, é uma derivação adotada neste
    projeto. Não há aqui calibração ou validação específica para veículos
    pesados (HDV). O valor calculado é um indicador comparativo de rota, não
    uma previsão calibrada de combustível ou emissões.
"""

import math
from graph import Cidade, Aresta, Grafo


# Coeficientes da formulação VSP adotada como referência. O projeto não
# reivindica que estes valores estejam calibrados para uma classe veicular
# específica.
G = 9.81             # aceleração gravitacional [m/s²]
FR_G = 0.132         # f_r * g [m/s²] — resistência de rolamento (Jiménez-Palacios, 1999)
C_AERO = 0.000302    # coeficiente aerodinâmico específico [m^-1] (Jiménez-Palacios, 1999)


def calcular_energia(origem: Cidade,destino: Cidade,aresta: Aresta, velocidade_ms: float) -> float:
    """
    Calcula a energia específica de travessia da aresta u -> v [J/kg].

    Derivação (Jiménez-Palacios, 1999, adaptado):
        VSP = v * (9.81*s + 0.132) + 0.000302 * v³
        E   = VSP * (d/v) = 9.81*Δh + 0.132*d + 0.000302*v²*d

        A expressão considera aceleração longitudinal nula e aproxima
        s*d por Δh. Como 1 kW/t equivale a 1 W/kg, a integração no tempo
        resulta em J/kg.

    Parâmetros:
        origem, destino : objetos Cidade com altitude_m
        aresta          : Aresta com dist_km e alt_passo_m (opcional)
        velocidade_ms   : velocidade de cruzeiro em m/s

    Retorna:
        Energia específica em J/kg (pode ser negativa em descidas íngremes,
        mas com os dados desta rota todas as arestas ficam positivas).

    Adaptação do projeto para passos andinos:
        Se aresta.alt_passo_m está definida, a subida é calculada até
        a cota do passo (a descida é dissipada na frenagem, sem recuperação).
        Isso evita subestimar o custo energético de cruzar os Andes. Essa
        hipótese não é atribuída às referências de VSP acima.
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
