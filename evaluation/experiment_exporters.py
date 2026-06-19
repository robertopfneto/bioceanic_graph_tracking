"""Exportacao dos experimentos complementares."""

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .models import ResultadosExperimentos


def _salvar_json(valor, caminho: Path) -> Path:
    caminho.write_text(
        json.dumps(asdict(valor), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return caminho


def _exportar_desempenho(experimentos: ResultadosExperimentos, diretorio: Path):
    resultado = experimentos.desempenho
    csv_path = diretorio / "desempenho.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["repeticao", "dijkstra_us", "martins_us"])
        for indice, (dijkstra_us, martins_us) in enumerate(
            zip(resultado.tempos_dijkstra_us, resultado.tempos_martins_us), start=1
        ):
            escritor.writerow([indice, dijkstra_us, martins_us])
    return csv_path, _salvar_json(resultado, diretorio / "desempenho.json")


def _exportar_sensibilidade(experimentos: ResultadosExperimentos, diretorio: Path):
    resultado = experimentos.sensibilidade
    csv_path = diretorio / "sensibilidade.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(
            [
                "velocidade_kmh",
                "energia_j_kg",
                "distancia_km",
                "subida_m",
                "passo_andino",
                "caminho",
            ]
        )
        for ponto in resultado.pontos:
            escritor.writerow(
                [
                    ponto.velocidade_kmh,
                    ponto.energia_j_kg,
                    ponto.distancia_km,
                    ponto.subida_m,
                    ponto.passo_andino,
                    " -> ".join(ponto.caminho),
                ]
            )
    return csv_path, _salvar_json(resultado, diretorio / "sensibilidade.json")


def _exportar_robustez(experimentos: ResultadosExperimentos, diretorio: Path):
    resultado = experimentos.robustez
    csv_path = diretorio / "robustez.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["simulacao", "tamanho_fronteira"])
        for indice, tamanho in enumerate(resultado.tamanhos_fronteira, start=1):
            escritor.writerow([indice, tamanho])
    return csv_path, _salvar_json(resultado, diretorio / "robustez.json")


def exportar_experimentos(
    experimentos: ResultadosExperimentos, diretorio: Path
) -> tuple[Path, ...]:
    return (
        *_exportar_desempenho(experimentos, diretorio),
        *_exportar_sensibilidade(experimentos, diretorio),
        *_exportar_robustez(experimentos, diretorio),
    )
