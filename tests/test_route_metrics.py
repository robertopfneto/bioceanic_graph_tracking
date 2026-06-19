import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from dados import construir_grafo
from evaluation.route_metrics import calcular_metricas_rota


class RouteMetricsTest(unittest.TestCase):
    def test_calcula_metricas_comuns_e_identifica_passo(self):
        grafo = construir_grafo()
        caminho = ["San Antonio de los Cobres", "Paso de Sico", "Calama"]

        metricas = calcular_metricas_rota(
            grafo,
            caminho,
            velocidade_ms=80 / 3.6,
            identificador="teste",
            algoritmo="teste",
            ponderacao="teste",
            tempo_us=0,
            expandidos=0,
        )

        self.assertAlmostEqual(350.0, metricas.distancia_km)
        self.assertEqual("Paso de Sico", metricas.passo_andino)
        self.assertGreater(metricas.energia_j_kg, 0)


if __name__ == "__main__":
    unittest.main()
