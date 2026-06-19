"""Graficos da comparacao de rotas."""

import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from graph import Grafo

from .models import ResultadoComparacao


def _arestas_sem_duplicata(grafo: Grafo):
    vistas = set()
    for arestas in grafo.adj.values():
        for aresta in arestas:
            chave = frozenset((aresta.origem, aresta.destino))
            if chave not in vistas:
                vistas.add(chave)
                yield aresta


def _plotar_rede(ax, grafo: Grafo) -> None:
    for aresta in _arestas_sem_duplicata(grafo):
        origem = grafo.cidades[aresta.origem]
        destino = grafo.cidades[aresta.destino]
        ax.plot(
            [origem.lon, destino.lon],
            [origem.lat, destino.lat],
            color="#c7c7c7",
            linewidth=0.8,
            zorder=1,
        )
    ax.scatter(
        [cidade.lon for cidade in grafo.cidades.values()],
        [cidade.lat for cidade in grafo.cidades.values()],
        s=12,
        color="#666666",
        zorder=2,
    )


def plotar_rotas(
    grafo: Grafo, resultado: ResultadoComparacao, caminho: Path
) -> Path:
    quantidade = len(resultado.rotas)
    colunas = min(2, quantidade)
    linhas = math.ceil(quantidade / colunas)
    figura, eixos = plt.subplots(
        linhas, colunas, figsize=(8 * colunas, 5 * linhas), squeeze=False
    )
    cores = ["#d62728", "#1f77b4", "#2ca02c", "#9467bd", "#ff7f0e"]
    for indice, (ax, rota) in enumerate(zip(eixos.flat, resultado.rotas)):
        _plotar_rede(ax, grafo)
        cidades = [grafo.cidades[nome] for nome in rota.caminho]
        ax.plot(
            [cidade.lon for cidade in cidades],
            [cidade.lat for cidade in cidades],
            color=cores[indice % len(cores)],
            linewidth=2.8,
            marker="o",
            markersize=3,
            zorder=3,
        )
        ax.set_title(
            f"{rota.identificador}\n"
            f"{rota.distancia_km:.0f} km | {rota.subida_m:.0f} m | "
            f"{rota.energia_j_kg:.0f} J/kg"
        )
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(alpha=0.2)
    for ax in list(eixos.flat)[quantidade:]:
        ax.axis("off")
    figura.suptitle(f"Rotas: {resultado.origem} - {resultado.destino}")
    figura.tight_layout()
    figura.savefig(caminho, dpi=180, bbox_inches="tight")
    plt.close(figura)
    return caminho


def plotar_fronteira_pareto(
    resultado: ResultadoComparacao, caminho: Path
) -> Path:
    figura, ax = plt.subplots(figsize=(8, 6))
    dijkstra_rota = resultado.rotas[0]
    martins_rotas = resultado.rotas[1:]
    ax.scatter(
        [rota.distancia_km for rota in martins_rotas],
        [rota.subida_m for rota in martins_rotas],
        s=70,
        color="#1f77b4",
        label="Fronteira de Martins",
        zorder=3,
    )
    for rota in martins_rotas:
        ax.annotate(
            rota.identificador,
            (rota.distancia_km, rota.subida_m),
            xytext=(6, 6),
            textcoords="offset points",
        )
    ax.scatter(
        [dijkstra_rota.distancia_km],
        [dijkstra_rota.subida_m],
        s=110,
        marker="x",
        linewidths=2.5,
        color="#d62728",
        label="Dijkstra-VSP (referencia externa)",
        zorder=4,
    )
    ax.set_xlabel("Distancia [km]")
    ax.set_ylabel("Ganho de elevacao [m]")
    ax.set_title("Fronteira Pareto e rota energeticamente otima")
    ax.grid(alpha=0.25)
    ax.legend()
    figura.tight_layout()
    figura.savefig(caminho, dpi=180, bbox_inches="tight")
    plt.close(figura)
    return caminho


def plotar_comparacao_metricas(
    resultado: ResultadoComparacao, caminho: Path
) -> Path:
    figura, eixos = plt.subplots(1, 3, figsize=(16, 5))
    nomes = [rota.identificador for rota in resultado.rotas]
    series = [
        ("Energia [J/kg]", [rota.energia_j_kg for rota in resultado.rotas]),
        ("Distancia [km]", [rota.distancia_km for rota in resultado.rotas]),
        ("Ganho de elevacao [m]", [rota.subida_m for rota in resultado.rotas]),
    ]
    cores = ["#d62728"] + ["#1f77b4"] * (len(resultado.rotas) - 1)
    for ax, (titulo, valores) in zip(eixos, series):
        ax.bar(nomes, valores, color=cores)
        ax.set_title(titulo)
        ax.tick_params(axis="x", rotation=30)
        ax.grid(axis="y", alpha=0.25)
    figura.suptitle(f"Comparacao comum das rotas para {resultado.destino}")
    figura.tight_layout()
    figura.savefig(caminho, dpi=180, bbox_inches="tight")
    plt.close(figura)
    return caminho


def gerar_graficos(
    grafo: Grafo, resultado: ResultadoComparacao, diretorio: Path
) -> tuple[Path, ...]:
    return (
        plotar_rotas(grafo, resultado, diretorio / "rotas.png"),
        plotar_fronteira_pareto(resultado, diretorio / "fronteira_pareto.png"),
        plotar_comparacao_metricas(
            resultado, diretorio / "comparacao_metricas.png"
        ),
    )
