"""Artefatos prontos para inclusao no artigo."""

from pathlib import Path

from dados import FONTES_VERTICES, METADADOS_VERTICES
from graph import Grafo

from .models import ResultadoComparacao
from .plotting import _arestas_sem_duplicata, plt


POSICOES = {
    "Santos": (0.0, 0.0),
    "Presidente Epitacio": (1.0, -0.55),
    "Tres Lagoas": (1.0, 0.75),
    "Bataguassu": (2.0, -0.55),
    "Nova Alvorada do Sul": (3.0, -0.55),
    "Campo Grande": (4.0, 0.0),
    "Porto Murtinho": (5.0, 0.0),
    "Carmelo Peralta": (6.0, 0.0),
    "Loma Plata": (7.0, -0.75),
    "MJF Estigarribia": (7.0, 0.0),
    "Pozo Hondo": (8.0, 0.0),
    "Mision La Paz": (9.0, 0.0),
    "Pozo de Maza": (10.0, 0.0),
    "Tartagal": (11.0, 0.0),
    "San Salvador de Jujuy": (12.0, 0.72),
    "Salta": (12.0, -0.58),
    "Susques": (13.0, 0.72),
    "San Antonio de los Cobres": (13.0, -0.58),
    "Paso de Jama": (14.0, 0.72),
    "Paso de Sico": (14.0, -0.58),
    "San Pedro de Atacama": (15.0, 0.72),
    "Calama": (15.4, -0.05),
    "Baquedano": (16.35, -0.05),
    "Mejillones": (17.35, 0.62),
    "Antofagasta": (17.35, -0.05),
    "Iquique": (16.35, 1.2),
}


def _escapar_latex(texto: str) -> str:
    substituicoes = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(substituicoes.get(caractere, caractere) for caractere in texto)


def _formatar_altitude(valor: float) -> str:
    return f"{valor:,.0f}".replace(",", ".")


def exportar_tabela_vertices_latex(grafo: Grafo, caminho: Path) -> Path:
    registros = []
    for indice, cidade in enumerate(grafo.cidades.values(), start=1):
        nome, pais, fonte = METADADOS_VERTICES[cidade.nome]
        registros.append(
            (
                str(indice),
                _escapar_latex(nome),
                _escapar_latex(pais),
                _formatar_altitude(cidade.altitude_m),
                fonte,
            )
        )

    metade = (len(registros) + 1) // 2
    esquerda = registros[:metade]
    direita = registros[metade:]
    linhas = []
    for primeiro, segundo in zip(esquerda, direita):
        linhas.append(" & ".join(primeiro + segundo) + r" \\")

    fontes = "; ".join(
        f"{sigla}: {descricao}" for sigla, descricao in FONTES_VERTICES.items()
    )
    conteudo = "\n".join(
        [
            r"\begin{table*}[t]",
            r"\centering",
            (
                r"\caption{Vértices usados na representação em grafo da "
                r"Rota Bioceânica de Capricórnio.}"
            ),
            r"\label{tab:vertices}",
            r"\scriptsize",
            r"\begin{tabularx}{\textwidth}{r Y l r l r Y l r l}",
            r"\toprule",
            (
                r"\textbf{\#} & \textbf{Vértice} & \textbf{País/região} & "
                r"\textbf{Alt.} & \textbf{Fonte} & \textbf{\#} & "
                r"\textbf{Vértice} & \textbf{País/região} & "
                r"\textbf{Alt.} & \textbf{Fonte} \\"
            ),
            r"\midrule",
            *linhas,
            r"\bottomrule",
            r"\end{tabularx}",
            rf"\tabnote{{Alt. = altitude em metros. Fontes: {_escapar_latex(fontes)}.}}",
            r"\end{table*}",
            "",
        ]
    )
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def _chave_aresta(origem: str, destino: str) -> frozenset[str]:
    return frozenset((origem, destino))


def plotar_grafo_rota_otima(
    grafo: Grafo, resultado: ResultadoComparacao, caminho: Path
) -> Path:
    if resultado.destino != "Antofagasta":
        raise ValueError("O grafo editorial e exclusivo do destino Antofagasta.")

    rota = resultado.rotas[0]
    arestas_rota = {
        _chave_aresta(origem, destino)
        for origem, destino in zip(rota.caminho, rota.caminho[1:])
    }
    figura, ax = plt.subplots(figsize=(18, 5.8))
    faixas = [
        (-0.5, 5.5, "#eef7ee", "Brasil"),
        (5.5, 8.5, "#fff8e8", "Paraguai"),
        (8.5, 14.5, "#fff0f0", "Argentina"),
        (14.5, 17.85, "#edf4ff", "Chile"),
    ]
    for inicio, fim, cor, titulo in faixas:
        ax.axvspan(inicio, fim, color=cor, zorder=0)
        ax.text((inicio + fim) / 2, 1.55, titulo, ha="center", fontsize=10)

    for aresta in _arestas_sem_duplicata(grafo):
        x1, y1 = POSICOES[aresta.origem]
        x2, y2 = POSICOES[aresta.destino]
        destaque = _chave_aresta(aresta.origem, aresta.destino) in arestas_rota
        ax.plot(
            [x1, x2],
            [y1, y2],
            color="#075bd8" if destaque else "#9a9a9a",
            linewidth=2.5 if destaque else 0.8,
            zorder=2 if destaque else 1,
        )
        ax.text(
            (x1 + x2) / 2,
            (y1 + y2) / 2 + 0.07,
            f"{aresta.dist_km:g}",
            color="#075bd8" if destaque else "#555555",
            fontsize=5.5,
            ha="center",
            va="bottom",
            zorder=4,
        )

    nomes_rota = set(rota.caminho)
    for nome in grafo.cidades:
        x, y = POSICOES[nome]
        if nome == resultado.origem:
            cor, tamanho = "#19a538", 72
        elif nome == resultado.destino:
            cor, tamanho = "#e51b23", 72
        elif nome in nomes_rota:
            cor, tamanho = "#075bd8", 34
        else:
            cor, tamanho = "#777777", 24
        ax.scatter(x, y, s=tamanho, color=cor, edgecolor="white", linewidth=0.5, zorder=5)
        nome_publicacao = METADADOS_VERTICES[nome][0]
        deslocamento = 0.14 if y <= 0.1 else 0.12
        ax.text(
            x,
            y + deslocamento,
            nome_publicacao,
            fontsize=5.8,
            ha="center",
            va="bottom",
            zorder=6,
        )

    ax.plot(
        [], [], color="#075bd8", linewidth=2.5, label="Melhor rota (Dijkstra-VSP)"
    )
    ax.plot([], [], color="#9a9a9a", linewidth=0.8, label="Arestas alternativas")
    ax.scatter([], [], s=60, color="#19a538", label="Origem (Santos)")
    ax.scatter([], [], s=60, color="#e51b23", label="Destino (Antofagasta)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.13), ncol=4, frameon=False)
    ax.set_title(
        f"Grafo da Rota 4 — {len(grafo.cidades)} vértices, "
        f"{sum(1 for _ in _arestas_sem_duplicata(grafo))} arestas bidirecionais\n"
        f"Melhor rota energética Santos–Antofagasta: {rota.distancia_km:.0f} km"
    )
    ax.set_xlim(-0.65, 17.95)
    ax.set_ylim(-1.05, 1.72)
    ax.axis("off")
    figura.tight_layout()
    figura.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close(figura)
    return caminho


def gerar_artefatos_artigo(
    grafo: Grafo, resultado: ResultadoComparacao, diretorio: Path
) -> tuple[Path, ...]:
    if resultado.destino != "Antofagasta":
        return ()
    return (
        exportar_tabela_vertices_latex(grafo, diretorio / "tabela_vertices.tex"),
        plotar_grafo_rota_otima(
            grafo, resultado, diretorio / "grafo_rota_otima_antofagasta.png"
        ),
        plotar_grafo_rota_otima(
            grafo, resultado, diretorio / "grafo_rota_otima_antofagasta.pdf"
        ),
    )
