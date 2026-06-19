import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from dados import construir_grafo
from evaluation import ConfiguracaoAvaliacao, executar_avaliacao


class PipelineTest(unittest.TestCase):
    def test_executa_receita_e_gera_todos_os_artefatos(self):
        with tempfile.TemporaryDirectory() as temporario:
            configuracao = ConfiguracaoAvaliacao(
                origem="Santos",
                destino="Antofagasta",
                diretorio_saida=Path(temporario),
                repeticoes_desempenho=10,
                repeticoes_aquecimento=1,
                simulacoes_monte_carlo=10,
            )

            artefatos = executar_avaliacao(construir_grafo(), configuracao)

            esperados = {
                "rotas.csv",
                "resultado.json",
                "rotas.png",
                "fronteira_pareto.png",
                "comparacao_metricas.png",
                "desempenho.csv",
                "desempenho.json",
                "desempenho.png",
                "sensibilidade.csv",
                "sensibilidade.json",
                "sensibilidade.png",
                "robustez.csv",
                "robustez.json",
                "robustez.png",
            }
            self.assertEqual(esperados, {item.name for item in artefatos.arquivos})
            self.assertTrue(all(item.exists() for item in artefatos.arquivos))


if __name__ == "__main__":
    unittest.main()
