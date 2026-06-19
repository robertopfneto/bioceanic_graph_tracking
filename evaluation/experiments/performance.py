"""Benchmark comparativo de Dijkstra e Martins."""

import random
import time

from scipy.stats import mannwhitneyu

from graph import Grafo
from search_algorithms.dijkstra import dijkstra
from search_algorithms.martins import martins

from ..models import ConfiguracaoAvaliacao, ResultadoDesempenho
from .statistics import resumir_amostra


def _medir(funcao, *args) -> float:
    inicio = time.perf_counter_ns()
    funcao(*args)
    return (time.perf_counter_ns() - inicio) / 1_000.0


def avaliar_desempenho(
    grafo: Grafo, configuracao: ConfiguracaoAvaliacao
) -> ResultadoDesempenho:
    argumentos_dijkstra = (
        grafo,
        configuracao.origem,
        configuracao.destino,
        configuracao.velocidade_ms,
    )
    argumentos_martins = (grafo, configuracao.origem, configuracao.destino)

    for _ in range(configuracao.repeticoes_aquecimento):
        dijkstra(*argumentos_dijkstra)
        martins(*argumentos_martins)

    rng = random.Random(configuracao.seed)
    tempos_dijkstra = []
    tempos_martins = []
    for _ in range(configuracao.repeticoes_desempenho):
        if rng.random() < 0.5:
            tempos_dijkstra.append(_medir(dijkstra, *argumentos_dijkstra))
            tempos_martins.append(_medir(martins, *argumentos_martins))
        else:
            tempos_martins.append(_medir(martins, *argumentos_martins))
            tempos_dijkstra.append(_medir(dijkstra, *argumentos_dijkstra))

    teste = mannwhitneyu(
        tempos_dijkstra,
        tempos_martins,
        alternative="less",
        method="auto",
    )
    return ResultadoDesempenho(
        tempos_dijkstra_us=tempos_dijkstra,
        tempos_martins_us=tempos_martins,
        resumo_dijkstra=resumir_amostra(tempos_dijkstra),
        resumo_martins=resumir_amostra(tempos_martins),
        mann_whitney_u=float(teste.statistic),
        mann_whitney_p=float(teste.pvalue),
        hipotese_alternativa="tempo(Dijkstra) < tempo(Martins)",
    )
