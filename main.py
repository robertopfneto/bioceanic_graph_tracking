"""Ponto de entrada do experimento comparativo de rotas."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from dados import construir_grafo
from evaluation import (
    ConfiguracaoAvaliacao,
    executar_avaliacao,
    formatar_resumo,
    formatar_resumo_experimentos,
)


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compara a ponderacao energetica VSP/Dijkstra com a ponderacao "
            "vetorial distancia-subida/Martins."
        )
    )
    parser.add_argument("--origem", default="Santos")
    parser.add_argument(
        "--destinos",
        nargs="+",
        default=["Antofagasta", "Iquique"],
    )
    parser.add_argument("--velocidade-kmh", type=float, default=80.0)
    parser.add_argument("--repeticoes-desempenho", type=int, default=1000)
    parser.add_argument("--repeticoes-aquecimento", type=int, default=20)
    parser.add_argument("--simulacoes-monte-carlo", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--saida",
        type=Path,
        default=ROOT / "outputs" / "evaluation",
    )
    return parser


def main() -> int:
    args = criar_parser().parse_args()
    grafo = construir_grafo()

    for destino in args.destinos:
        configuracao = ConfiguracaoAvaliacao(
            origem=args.origem,
            destino=destino,
            velocidade_kmh=args.velocidade_kmh,
            diretorio_saida=args.saida,
            repeticoes_desempenho=args.repeticoes_desempenho,
            repeticoes_aquecimento=args.repeticoes_aquecimento,
            simulacoes_monte_carlo=args.simulacoes_monte_carlo,
            seed=args.seed,
        )
        artefatos = executar_avaliacao(grafo, configuracao)

        print(formatar_resumo(artefatos.resultado))
        print()
        print(formatar_resumo_experimentos(artefatos.experimentos))
        print(f"\nArquivos: {artefatos.diretorio}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
