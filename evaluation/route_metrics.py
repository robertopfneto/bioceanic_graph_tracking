"""Calculo uniforme das metricas de qualquer rota."""

import math

from cost import calcular_energia
from graph import Aresta, Grafo
from search_algorithms.martins import ganho_elevacao

from .models import MetricasRota


def localizar_aresta(grafo: Grafo, origem: str, destino: str) -> Aresta:
    for aresta in grafo.vizinhos(origem):
        if aresta.destino == destino:
            return aresta
    raise ValueError(f"Aresta inexistente no caminho: {origem!r} -> {destino!r}")


def identificar_passos(arestas: list[Aresta]) -> str | None:
    passos = set()
    for aresta in arestas:
        if aresta.alt_passo_m is None:
            continue
        extremos = (aresta.origem, aresta.destino)
        nome = next(
            (cidade for cidade in extremos if cidade.startswith("Paso de ")),
            f"{aresta.origem} - {aresta.destino}",
        )
        passos.add(nome)
    return ", ".join(sorted(passos)) if passos else None


def calcular_metricas_rota(
    grafo: Grafo,
    caminho: list[str],
    velocidade_ms: float,
    identificador: str,
    algoritmo: str,
    ponderacao: str,
    tempo_us: float,
    expandidos: int,
) -> MetricasRota:
    if not caminho:
        return MetricasRota(
            identificador=identificador,
            algoritmo=algoritmo,
            ponderacao=ponderacao,
            caminho=[],
            energia_j_kg=math.inf,
            distancia_km=math.inf,
            subida_m=math.inf,
            passo_andino=None,
            tempo_us=tempo_us,
            expandidos=expandidos,
        )

    arestas = [
        localizar_aresta(grafo, origem, destino)
        for origem, destino in zip(caminho, caminho[1:])
    ]
    energia = 0.0
    distancia = 0.0
    subida = 0.0
    for aresta in arestas:
        origem = grafo.cidades[aresta.origem]
        destino = grafo.cidades[aresta.destino]
        energia += calcular_energia(origem, destino, aresta, velocidade_ms)
        distancia += aresta.dist_km
        subida += ganho_elevacao(
            origem.altitude_m, destino.altitude_m, aresta.alt_passo_m
        )

    return MetricasRota(
        identificador=identificador,
        algoritmo=algoritmo,
        ponderacao=ponderacao,
        caminho=caminho,
        energia_j_kg=energia,
        distancia_km=distancia,
        subida_m=subida,
        passo_andino=identificar_passos(arestas),
        tempo_us=tempo_us,
        expandidos=expandidos,
    )
