"""Graficos dos experimentos complementares."""

from pathlib import Path

from .models import ResultadosExperimentos
from .plotting import plt


def _formatar_p(valor: float) -> str:
    return "<1e-300" if valor == 0 else f"{valor:.3g}"


def _plotar_desempenho(experimentos: ResultadosExperimentos, caminho: Path) -> Path:
    resultado = experimentos.desempenho
    figura, ax = plt.subplots(figsize=(8, 6))
    partes = ax.violinplot(
        [resultado.tempos_dijkstra_us, resultado.tempos_martins_us],
        showmeans=True,
        showmedians=True,
    )
    for corpo, cor in zip(partes["bodies"], ["#d62728", "#1f77b4"]):
        corpo.set_facecolor(cor)
        corpo.set_alpha(0.65)
    ax.set_xticks([1, 2], ["Dijkstra", "Martins"])
    ax.set_ylabel("Tempo [us]")
    ax.set_title(
        "Distribuicao dos tempos de execucao\n"
        f"Mann-Whitney unilateral: p={_formatar_p(resultado.mann_whitney_p)}"
    )
    ax.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(caminho, dpi=180, bbox_inches="tight")
    plt.close(figura)
    return caminho


def _plotar_sensibilidade(experimentos: ResultadosExperimentos, caminho: Path) -> Path:
    resultado = experimentos.sensibilidade
    figura, ax = plt.subplots(figsize=(8, 6))
    velocidades = [ponto.velocidade_kmh for ponto in resultado.pontos]
    energias = [ponto.energia_j_kg for ponto in resultado.pontos]
    ax.plot(velocidades, energias, marker="o", color="#d62728")
    for ponto in resultado.pontos:
        ax.annotate(
            ponto.passo_andino or "sem passo",
            (ponto.velocidade_kmh, ponto.energia_j_kg),
            xytext=(4, 6),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set_xlabel("Velocidade [km/h]")
    ax.set_ylabel("Energia [J/kg]")
    ax.set_title(
        "Sensibilidade da ponderacao VSP\n"
        f"Pearson(v,E)={resultado.pearson_v_r:.4f}; "
        f"Pearson(v2,E)={resultado.pearson_v2_r:.4f}"
    )
    ax.grid(alpha=0.25)
    figura.tight_layout()
    figura.savefig(caminho, dpi=180, bbox_inches="tight")
    plt.close(figura)
    return caminho


def _plotar_robustez(experimentos: ResultadosExperimentos, caminho: Path) -> Path:
    resultado = experimentos.robustez
    figura, ax = plt.subplots(figsize=(8, 6))
    tamanhos = list(resultado.frequencias_tamanho)
    frequencias = [resultado.frequencias_tamanho[tamanho] for tamanho in tamanhos]
    ax.bar(tamanhos, frequencias, color="#1f77b4")
    ax.set_xticks(tamanhos)
    ax.set_xlabel("Quantidade de solucoes na fronteira")
    ax.set_ylabel("Numero de simulacoes")
    ax.set_title(
        f"Robustez de Martins ({resultado.simulacoes} simulacoes)\n"
        "distancia: CV=5%; altitude: sigma=30 m"
    )
    ax.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(caminho, dpi=180, bbox_inches="tight")
    plt.close(figura)
    return caminho


def gerar_graficos_experimentos(
    experimentos: ResultadosExperimentos, diretorio: Path
) -> tuple[Path, ...]:
    return (
        _plotar_desempenho(experimentos, diretorio / "desempenho.png"),
        _plotar_sensibilidade(experimentos, diretorio / "sensibilidade.png"),
        _plotar_robustez(experimentos, diretorio / "robustez.png"),
    )
