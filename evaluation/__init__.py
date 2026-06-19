"""API publica da avaliacao comparativa de rotas."""

from .models import ConfiguracaoAvaliacao
from .pipeline import executar_avaliacao
from .reporting import formatar_resumo, formatar_resumo_experimentos

__all__ = [
    "ConfiguracaoAvaliacao",
    "executar_avaliacao",
    "formatar_resumo",
    "formatar_resumo_experimentos",
]
