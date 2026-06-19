import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from dados import construir_grafo
from evaluation.comparison import comparar_ponderacoes
from evaluation.models import ConfiguracaoAvaliacao
from evaluation.validation import validar_grafo


class ComparisonTest(unittest.TestCase):
    def test_compara_as_duas_ponderacoes(self):
        grafo = construir_grafo()
        configuracao = ConfiguracaoAvaliacao("Santos", "Antofagasta")
        validacao = validar_grafo(grafo, configuracao)

        resultado = comparar_ponderacoes(grafo, configuracao, validacao)

        self.assertTrue(validacao.valido)
        self.assertEqual(2, len(resultado.rotas))
        self.assertEqual("Dijkstra-VSP", resultado.rotas[0].identificador)
        self.assertEqual("Martins-M1", resultado.rotas[1].identificador)
        self.assertEqual(resultado.rotas[0].caminho, resultado.rotas[1].caminho)
        self.assertAlmostEqual(3552.0, resultado.rotas[0].distancia_km)
        self.assertAlmostEqual(4541.0, resultado.rotas[0].subida_m)
        self.assertTrue(resultado.dijkstra_na_fronteira)
        self.assertFalse(resultado.dijkstra_dominado)


if __name__ == "__main__":
    unittest.main()
