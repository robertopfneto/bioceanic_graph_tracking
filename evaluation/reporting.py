"""Representacao textual dos resultados."""

from .models import ResultadoComparacao, ResultadosExperimentos


def _formatar_p(valor: float) -> str:
    return "<1e-300" if valor == 0 else f"{valor:.6g}"


def formatar_resumo(resultado: ResultadoComparacao) -> str:
    linhas = [
        f"{resultado.origem} -> {resultado.destino} "
        f"({resultado.velocidade_kmh:g} km/h)",
        "",
        "Rota             Energia [J/kg]  Distancia [km]  Subida [m]  Passo",
    ]
    for rota in resultado.rotas:
        linhas.append(
            f"{rota.identificador:<17} {rota.energia_j_kg:>14.2f}  "
            f"{rota.distancia_km:>14.2f}  {rota.subida_m:>10.2f}  "
            f"{rota.passo_andino or '-'}"
        )
    linhas.extend(
        [
            "",
            f"Dijkstra na fronteira de Martins: {resultado.dijkstra_na_fronteira}",
            f"Dijkstra dominado em (distancia, subida): {resultado.dijkstra_dominado}",
        ]
    )
    return "\n".join(linhas)


def formatar_resumo_experimentos(experimentos: ResultadosExperimentos) -> str:
    desempenho = experimentos.desempenho
    sensibilidade = experimentos.sensibilidade
    robustez = experimentos.robustez
    return "\n".join(
        [
            "Desempenho:",
            f"  Dijkstra: {desempenho.resumo_dijkstra.media:.2f} us "
            f"(IC95% {desempenho.resumo_dijkstra.ic95_inferior:.2f}-"
            f"{desempenho.resumo_dijkstra.ic95_superior:.2f})",
            f"  Martins:  {desempenho.resumo_martins.media:.2f} us "
            f"(IC95% {desempenho.resumo_martins.ic95_inferior:.2f}-"
            f"{desempenho.resumo_martins.ic95_superior:.2f})",
            f"  Mann-Whitney unilateral: p={_formatar_p(desempenho.mann_whitney_p)}",
            "Sensibilidade:",
            f"  Pearson(v, energia): r={sensibilidade.pearson_v_r:.6f}, "
            f"p={_formatar_p(sensibilidade.pearson_v_p)}",
            f"  Pearson(v2, energia): r={sensibilidade.pearson_v2_r:.6f}, "
            f"p={_formatar_p(sensibilidade.pearson_v2_p)}",
            "Robustez de Martins:",
            f"  Tamanho medio da fronteira: "
            f"{robustez.resumo_tamanho_fronteira.media:.3f}",
            f"  Frequencias: {robustez.frequencias_tamanho}",
        ]
    )
