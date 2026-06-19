"""Validacoes de pre-voo do grafo."""

from cost import verificar_pesos_positivos
from graph import Grafo

from .models import ConfiguracaoAvaliacao, ValidacaoGrafo


def validar_grafo(
    grafo: Grafo, configuracao: ConfiguracaoAvaliacao
) -> ValidacaoGrafo:
    erros, _ = grafo.validate_graph_integrity()
    return ValidacaoGrafo(
        cidades=len(grafo.cidades),
        arestas_direcionadas=sum(len(arestas) for arestas in grafo.adj.values()),
        cidades_esperadas=configuracao.cidades_esperadas,
        arestas_esperadas=configuracao.arestas_esperadas,
        erros_integridade=erros,
        pesos_negativos=verificar_pesos_positivos(
            grafo, configuracao.velocidade_ms
        ),
    )
