"""Orquestracao top-down da avaliacao."""

from graph import Grafo

from .article_artifacts import gerar_artefatos_artigo
from .comparison import comparar_ponderacoes
from .experiment_exporters import exportar_experimentos
from .experiment_plotting import gerar_graficos_experimentos
from .experiments import avaliar_desempenho, avaliar_robustez, avaliar_sensibilidade
from .exporters import exportar_resultados, preparar_diretorio_saida
from .models import (
    ArtefatosAvaliacao,
    ConfiguracaoAvaliacao,
    ResultadosExperimentos,
)
from .plotting import gerar_graficos
from .validation import validar_grafo


def executar_avaliacao(
    grafo: Grafo, configuracao: ConfiguracaoAvaliacao
) -> ArtefatosAvaliacao:
    """Executa a receita completa da avaliacao em ordem de leitura."""
    configuracao.validar()

    validacao = validar_grafo(grafo, configuracao)
    validacao.exigir_valido()

    resultado = comparar_ponderacoes(grafo, configuracao, validacao)
    experimentos = ResultadosExperimentos(
        desempenho=avaliar_desempenho(grafo, configuracao),
        sensibilidade=avaliar_sensibilidade(grafo, configuracao),
        robustez=avaliar_robustez(grafo, configuracao),
    )

    diretorio = preparar_diretorio_saida(
        configuracao.diretorio_saida, configuracao.destino
    )

    dados = exportar_resultados(resultado, diretorio)
    figuras = gerar_graficos(grafo, resultado, diretorio)
    dados_experimentos = exportar_experimentos(experimentos, diretorio)
    figuras_experimentos = gerar_graficos_experimentos(experimentos, diretorio)
    artigo = gerar_artefatos_artigo(grafo, resultado, diretorio)

    return ArtefatosAvaliacao(
        resultado=resultado,
        experimentos=experimentos,
        diretorio=diretorio,
        arquivos=dados + figuras + dados_experimentos + figuras_experimentos + artigo,
    )
