"""Sensibilidade da rota VSP a velocidade de cruzeiro."""

from scipy.stats import pearsonr

from graph import Grafo
from search_algorithms.dijkstra import dijkstra

from ..models import (
    ConfiguracaoAvaliacao,
    PontoSensibilidade,
    ResultadoSensibilidade,
)
from ..route_metrics import calcular_metricas_rota


def avaliar_sensibilidade(
    grafo: Grafo, configuracao: ConfiguracaoAvaliacao
) -> ResultadoSensibilidade:
    pontos = []
    for velocidade_kmh in configuracao.velocidades_sensibilidade:
        velocidade_ms = velocidade_kmh / 3.6
        resultado = dijkstra(
            grafo,
            configuracao.origem,
            configuracao.destino,
            velocidade_ms,
        )
        metricas = calcular_metricas_rota(
            grafo,
            resultado.caminho,
            velocidade_ms,
            identificador=f"Dijkstra-{velocidade_kmh:g}kmh",
            algoritmo="Dijkstra",
            ponderacao="energia VSP [J/kg]",
            tempo_us=0,
            expandidos=resultado.nos_expandidos,
        )
        pontos.append(
            PontoSensibilidade(
                velocidade_kmh=velocidade_kmh,
                energia_j_kg=metricas.energia_j_kg,
                distancia_km=metricas.distancia_km,
                subida_m=metricas.subida_m,
                passo_andino=metricas.passo_andino,
                caminho=metricas.caminho,
            )
        )

    velocidades = [ponto.velocidade_kmh for ponto in pontos]
    energias = [ponto.energia_j_kg for ponto in pontos]
    pearson_v = pearsonr(velocidades, energias)
    pearson_v2 = pearsonr([velocidade**2 for velocidade in velocidades], energias)
    return ResultadoSensibilidade(
        pontos=pontos,
        pearson_v_r=float(pearson_v.statistic),
        pearson_v_p=float(pearson_v.pvalue),
        pearson_v2_r=float(pearson_v2.statistic),
        pearson_v2_p=float(pearson_v2.pvalue),
    )
