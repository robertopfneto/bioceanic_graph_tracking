"""Exportacao dos resultados estruturados."""

import csv
import json
import re
import unicodedata
from dataclasses import asdict
from pathlib import Path

from .models import ResultadoComparacao


def preparar_diretorio_saida(base: Path, destino: str) -> Path:
    normalizado = unicodedata.normalize("NFKD", destino)
    ascii_texto = normalizado.encode("ascii", "ignore").decode("ascii")
    nome = re.sub(r"[^a-z0-9]+", "_", ascii_texto.lower()).strip("_")
    diretorio = base / nome
    diretorio.mkdir(parents=True, exist_ok=True)
    return diretorio


def exportar_csv(resultado: ResultadoComparacao, caminho: Path) -> Path:
    campos = [
        "identificador",
        "algoritmo",
        "ponderacao",
        "energia_j_kg",
        "distancia_km",
        "subida_m",
        "passo_andino",
        "tempo_us",
        "expandidos",
        "caminho",
    ]
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        for rota in resultado.rotas:
            linha = asdict(rota)
            linha["caminho"] = " -> ".join(rota.caminho)
            escritor.writerow(linha)
    return caminho


def exportar_json(resultado: ResultadoComparacao, caminho: Path) -> Path:
    caminho.write_text(
        json.dumps(asdict(resultado), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return caminho


def exportar_resultados(
    resultado: ResultadoComparacao, diretorio: Path
) -> tuple[Path, ...]:
    return (
        exportar_csv(resultado, diretorio / "rotas.csv"),
        exportar_json(resultado, diretorio / "resultado.json"),
    )
