"""Comparacao das ponderacoes VSP e distancia-subida."""

import math
import time

from graph import Grafo
from search_algorithms.dijkstra import dijkstra
from search_algorithms.martins import martins

from .models import ConfiguracaoAvaliacao, ResultadoComparacao, ValidacaoGrafo
from .route_metrics import calcular_metricas_rota


def _executar_medido(funcao, *args):
    inicio = time.perf_counter_ns()
    resultado = funcao(*args)
    return resultado, (time.perf_counter_ns() - inicio) / 1_000.0


def comparar_ponderacoes(
    grafo: Grafo,
    configuracao: ConfiguracaoAvaliacao,
    validacao: ValidacaoGrafo,
) -> ResultadoComparacao:
    resultado_dijkstra, tempo_dijkstra = _executar_medido(
        dijkstra,
        grafo,
        configuracao.origem,
        configuracao.destino,
        configuracao.velocidade_ms,
    )
    resultado_martins, tempo_martins = _executar_medido(
        martins, grafo, configuracao.origem, configuracao.destino
    )

    rotas = [
        calcular_metricas_rota(
            grafo,
            resultado_dijkstra.caminho,
            configuracao.velocidade_ms,
            "Dijkstra-VSP",
            "Dijkstra",
            "energia VSP [J/kg]",
            tempo_dijkstra,
            resultado_dijkstra.nos_expandidos,
        )
    ]
    for indice, (_, _, caminho) in enumerate(
        resultado_martins.fronteira_pareto, start=1
    ):
        rotas.append(
            calcular_metricas_rota(
                grafo,
                caminho,
                configuracao.velocidade_ms,
                f"Martins-M{indice}",
                "Martins",
                "(distancia [km], subida [m])",
                tempo_martins,
                resultado_martins.rotulos_expandidos,
            )
        )

    dijkstra_rota = rotas[0]
    fronteira = rotas[1:]
    na_fronteira = any(
        math.isclose(dijkstra_rota.distancia_km, rota.distancia_km, abs_tol=1e-9)
        and math.isclose(dijkstra_rota.subida_m, rota.subida_m, abs_tol=1e-9)
        for rota in fronteira
    )
    dominado = any(
        rota.distancia_km <= dijkstra_rota.distancia_km
        and rota.subida_m <= dijkstra_rota.subida_m
        and (
            rota.distancia_km < dijkstra_rota.distancia_km
            or rota.subida_m < dijkstra_rota.subida_m
        )
        for rota in fronteira
    )

    return ResultadoComparacao(
        origem=configuracao.origem,
        destino=configuracao.destino,
        velocidade_kmh=configuracao.velocidade_kmh,
        validacao=validacao,
        rotas=rotas,
        dijkstra_na_fronteira=na_fronteira,
        dijkstra_dominado=dominado,
    )
