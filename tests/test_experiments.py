import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from dados import construir_grafo
from evaluation.experiments import (
    avaliar_desempenho,
    avaliar_robustez,
    avaliar_sensibilidade,
)
from evaluation.models import ConfiguracaoAvaliacao


class ExperimentsTest(unittest.TestCase):
    def setUp(self):
        self.grafo = construir_grafo()
        self.configuracao = ConfiguracaoAvaliacao(
            origem="Santos",
            destino="Antofagasta",
            repeticoes_desempenho=10,
            repeticoes_aquecimento=1,
            simulacoes_monte_carlo=10,
            seed=7,
        )

    def test_desempenho_preserva_amostras_brutas(self):
        resultado = avaliar_desempenho(self.grafo, self.configuracao)

        self.assertEqual(10, len(resultado.tempos_dijkstra_us))
        self.assertEqual(10, len(resultado.tempos_martins_us))
        self.assertGreater(resultado.resumo_dijkstra.desvio_padrao, 0)
        self.assertGreaterEqual(resultado.mann_whitney_p, 0)
        self.assertLessEqual(resultado.mann_whitney_p, 1)

    def test_sensibilidade_confirma_termo_quadratico(self):
        resultado = avaliar_sensibilidade(self.grafo, self.configuracao)

        self.assertEqual(5, len(resultado.pontos))
        self.assertAlmostEqual(1.0, resultado.pearson_v2_r, places=12)
        self.assertTrue(
            all(ponto.passo_andino == "Paso de Sico" for ponto in resultado.pontos)
        )

    def test_monte_carlo_e_reprodutivel(self):
        primeiro = avaliar_robustez(self.grafo, self.configuracao)
        segundo = avaliar_robustez(self.grafo, self.configuracao)

        self.assertEqual(primeiro.tamanhos_fronteira, segundo.tamanhos_fronteira)
        self.assertEqual(10, sum(primeiro.frequencias_tamanho.values()))


if __name__ == "__main__":
    unittest.main()
