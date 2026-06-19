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
                "tabela_vertices.tex",
                "grafo_rota_otima_antofagasta.png",
                "grafo_rota_otima_antofagasta.pdf",
            }
            self.assertEqual(esperados, {item.name for item in artefatos.arquivos})
            self.assertTrue(all(item.exists() for item in artefatos.arquivos))

            tabela = (artefatos.diretorio / "tabela_vertices.tex").read_text(
                encoding="utf-8"
            )
            self.assertIn("Presidente Epitácio & Brasil & 261 & IBGE", tabela)
            self.assertIn("Pozo Hondo & Paraguai & 178 & MOPC--PY", tabela)
            self.assertIn("Paso de Jama & Argentina/Chile & 4.200", tabela)
            self.assertIn("\\textbf{Fonte}", tabela)
            self.assertIn("Instituto Brasileiro de Geografia e Estatística", tabela)
            self.assertIn("Vialidad Nacional Argentina e Vialidad Chile", tabela)


if __name__ == "__main__":
    unittest.main()
