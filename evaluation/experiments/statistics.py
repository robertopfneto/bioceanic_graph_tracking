"""Estatisticas descritivas compartilhadas pelos experimentos."""

import statistics

from scipy.stats import t

from ..models import ResumoAmostra


def resumir_amostra(valores: list[float] | list[int]) -> ResumoAmostra:
    n = len(valores)
    media = statistics.fmean(valores)
    desvio = statistics.stdev(valores)
    erro_padrao = desvio / (n**0.5)
    margem = float(t.ppf(0.975, df=n - 1)) * erro_padrao
    return ResumoAmostra(
        n=n,
        media=media,
        desvio_padrao=desvio,
        ic95_inferior=media - margem,
        ic95_superior=media + margem,
    )
