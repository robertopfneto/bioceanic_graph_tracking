"""Modelos de dados compartilhados pela avaliacao."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConfiguracaoAvaliacao:
    origem: str
    destino: str
    velocidade_kmh: float = 80.0
    diretorio_saida: Path = Path("outputs/evaluation")
    cidades_esperadas: int = 26
    arestas_esperadas: int = 64
    repeticoes_desempenho: int = 1000
    repeticoes_aquecimento: int = 20
    velocidades_sensibilidade: tuple[float, ...] = (40, 60, 80, 100, 120)
    simulacoes_monte_carlo: int = 2000
    seed: int = 42

    def validar(self) -> None:
        if self.velocidade_kmh <= 0:
            raise ValueError("A velocidade deve ser maior que zero.")
        if self.repeticoes_desempenho < 2:
            raise ValueError("O desempenho requer pelo menos duas repeticoes.")
        if self.repeticoes_aquecimento < 0:
            raise ValueError("O aquecimento nao pode ser negativo.")
        if len(self.velocidades_sensibilidade) < 2:
            raise ValueError("A sensibilidade requer pelo menos duas velocidades.")
        if any(velocidade <= 0 for velocidade in self.velocidades_sensibilidade):
            raise ValueError("As velocidades de sensibilidade devem ser positivas.")
        if self.simulacoes_monte_carlo < 2:
            raise ValueError("Monte Carlo requer pelo menos duas simulacoes.")

    @property
    def velocidade_ms(self) -> float:
        return self.velocidade_kmh / 3.6


@dataclass(frozen=True)
class MetricasRota:
    identificador: str
    algoritmo: str
    ponderacao: str
    caminho: list[str]
    energia_j_kg: float
    distancia_km: float
    subida_m: float
    passo_andino: str | None
    tempo_us: float
    expandidos: int


@dataclass(frozen=True)
class ValidacaoGrafo:
    cidades: int
    arestas_direcionadas: int
    cidades_esperadas: int
    arestas_esperadas: int
    erros_integridade: list[dict]
    pesos_negativos: list[tuple[str, str, float]]

    @property
    def valido(self) -> bool:
        return (
            self.cidades == self.cidades_esperadas
            and self.arestas_direcionadas == self.arestas_esperadas
            and not self.erros_integridade
            and not self.pesos_negativos
        )

    def exigir_valido(self) -> None:
        if not self.valido:
            raise ValueError(f"Grafo invalido para o experimento: {self}")


@dataclass(frozen=True)
class ResultadoComparacao:
    origem: str
    destino: str
    velocidade_kmh: float
    validacao: ValidacaoGrafo
    rotas: list[MetricasRota]
    dijkstra_na_fronteira: bool
    dijkstra_dominado: bool


@dataclass(frozen=True)
class ResumoAmostra:
    n: int
    media: float
    desvio_padrao: float
    ic95_inferior: float
    ic95_superior: float


@dataclass(frozen=True)
class ResultadoDesempenho:
    tempos_dijkstra_us: list[float]
    tempos_martins_us: list[float]
    resumo_dijkstra: ResumoAmostra
    resumo_martins: ResumoAmostra
    mann_whitney_u: float
    mann_whitney_p: float
    hipotese_alternativa: str


@dataclass(frozen=True)
class PontoSensibilidade:
    velocidade_kmh: float
    energia_j_kg: float
    distancia_km: float
    subida_m: float
    passo_andino: str | None
    caminho: list[str]


@dataclass(frozen=True)
class ResultadoSensibilidade:
    pontos: list[PontoSensibilidade]
    pearson_v_r: float
    pearson_v_p: float
    pearson_v2_r: float
    pearson_v2_p: float


@dataclass(frozen=True)
class ResultadoRobustez:
    seed: int
    simulacoes: int
    tamanhos_fronteira: list[int]
    resumo_tamanho_fronteira: ResumoAmostra
    frequencias_tamanho: dict[int, int]


@dataclass(frozen=True)
class ResultadosExperimentos:
    desempenho: ResultadoDesempenho
    sensibilidade: ResultadoSensibilidade
    robustez: ResultadoRobustez


@dataclass(frozen=True)
class ArtefatosAvaliacao:
    resultado: ResultadoComparacao
    experimentos: ResultadosExperimentos
    diretorio: Path
    arquivos: tuple[Path, ...]
