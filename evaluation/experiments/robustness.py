"""Robustez da fronteira de Martins sob incerteza dos dados."""

import random
from collections import Counter

from graph import Aresta, Cidade, Grafo
from search_algorithms.martins import martins

from ..models import ConfiguracaoAvaliacao, ResultadoRobustez
from .statistics import resumir_amostra


def _arestas_sem_duplicata(grafo: Grafo):
    vistas = set()
    for arestas in grafo.adj.values():
        for aresta in arestas:
            chave = frozenset((aresta.origem, aresta.destino))
            if chave not in vistas:
                vistas.add(chave)
                yield aresta


def perturbar_grafo(grafo: Grafo, rng: random.Random) -> Grafo:
    perturbado = Grafo()
    for cidade in grafo.cidades.values():
        perturbado.adicionar_cidade(
            Cidade(
                nome=cidade.nome,
                lat=cidade.lat,
                lon=cidade.lon,
                altitude_m=rng.gauss(cidade.altitude_m, 30.0),
            )
        )

    for aresta in _arestas_sem_duplicata(grafo):
        distancia = max(0.001, rng.gauss(aresta.dist_km, 0.05 * aresta.dist_km))
        altitude_passo = (
            rng.gauss(aresta.alt_passo_m, 30.0)
            if aresta.alt_passo_m is not None
            else None
        )
        perturbado.adicionar_aresta_bidirecional(
            Aresta(
                origem=aresta.origem,
                destino=aresta.destino,
                dist_km=distancia,
                alt_passo_m=altitude_passo,
            )
        )
    return perturbado


def avaliar_robustez(
    grafo: Grafo, configuracao: ConfiguracaoAvaliacao
) -> ResultadoRobustez:
    rng = random.Random(configuracao.seed)
    tamanhos = []
    for _ in range(configuracao.simulacoes_monte_carlo):
        cenario = perturbar_grafo(grafo, rng)
        resultado = martins(
            cenario, configuracao.origem, configuracao.destino
        )
        tamanhos.append(len(resultado.fronteira_pareto))

    frequencias = dict(sorted(Counter(tamanhos).items()))
    return ResultadoRobustez(
        seed=configuracao.seed,
        simulacoes=configuracao.simulacoes_monte_carlo,
        tamanhos_fronteira=tamanhos,
        resumo_tamanho_fronteira=resumir_amostra(tamanhos),
        frequencias_tamanho=frequencias,
    )
