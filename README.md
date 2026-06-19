# bioceanic_graph_tracking

Modelagem e otimização de rotas na **Rota Bioceânica de Capricórnio (Rota 4)** — trecho Santos (BR) → Antofagasta/Iquique (CL), atravessando Paraguai e Argentina. O projeto fundamenta um artigo acadêmico que compara estratégias de rota por dois critérios: **custo energético** (modelo VSP) e **eficiência multiobjetivo** (fronteira de Pareto distância × ganho de elevação).

---

## Estrutura do projeto

```
bioceanic_graph_tracking/
├── main.py                          # ponto de entrada da avaliação
├── src/
│   ├── graph.py                     # estruturas de dados: Cidade, Aresta, Grafo
│   ├── cost.py                      # função de custo energético (modelo VSP)
│   ├── dados.py                     # dados da rota (26 cidades, 32 arestas bidirecionais)
│   └── search_algorithms/
│       ├── dijkstra.py              # menor caminho mono-critério (energia mínima)
│       └── martins.py               # menor caminho multi-critério (fronteira de Pareto)
└── evaluation/
    ├── models.py                    # configuração e resultados estruturados
    ├── validation.py                # validações de pré-voo
    ├── route_metrics.py             # métricas comuns das rotas
    ├── comparison.py                # Dijkstra-VSP × Martins
    ├── experiments/                 # desempenho, sensibilidade e robustez
    ├── experiment_exporters.py      # CSV/JSON dos experimentos
    ├── experiment_plotting.py       # gráficos dos experimentos
    ├── exporters.py                 # exportação CSV/JSON
    ├── plotting.py                  # gráficos comparativos
    ├── reporting.py                 # resumo textual
    └── pipeline.py                  # orquestração top-down
```

---

## Dados da rota

O grafo representa a **Rota Bioceânica de Capricórnio** com:

- **26 vértices** (cidades/pontos de passagem): 7 no Brasil, 4 no Paraguai, 9 na Argentina, 6 no Chile
- **32 arestas bidirecionais** (64 arestas direcionadas no grafo interno)
- Cada aresta carrega `dist_km` e, quando aplicável, `alt_passo_m` — a cota do pico andino intermediário (presente apenas em Paso de Jama e Paso de Sico)

| País | Cidades |
|------|---------|
| Brasil | Santos, Presidente Epitácio, Três Lagoas, Bataguassu, Nova Alvorada do Sul, Campo Grande, Porto Murtinho |
| Paraguai | Carmelo Peralta, Loma Plata, MJF Estigarribia, Pozo Hondo |
| Argentina | Misión La Paz, Pozo de Maza, Tartagal, San Salvador de Jujuy, Salta, Susques, Paso de Jama, San Antonio de los Cobres, Paso de Sico |
| Chile | San Pedro de Atacama, Calama, Baquedano, Mejillones, Antofagasta, Iquique |

**Fontes dos dados geográficos:** IBGE (BR), MOPC (PY), IGN (AR), IGM (CL), Vialidad Nacional AR/CL, Google Maps, DNIT. Data de coleta: junho de 2026.

As cotas altimétricas revisadas incluem Presidente Epitácio (261 m), Pozo Hondo
(178 m), Misión La Paz (180 m) e Pozo de Maza (152 m). As distâncias dos
trechos rodoviários representam rotas transitáveis, não distâncias geométricas
entre as coordenadas.

---

## Modelo de custo energético (VSP)

O custo de travessia de cada aresta é uma **estimativa de energia específica [J/kg]** derivada da formulação VSP (*Vehicle Specific Power*), sob velocidade constante e aceleração longitudinal nula:

```
E = G·Δh⁺  +  FR_G·d  +  C_AERO·v²·d
Δh⁺ = max(0, Δh)
```

| Termo | Significado |
|-------|-------------|
| `G·Δh⁺` | Energia gravitacional associada apenas ao ganho de altitude (`G = 9,81 m/s²`) |
| `FR_G·d` | Resistência de rolamento (`FR_G = 0,132 m/s²`) |
| `C_AERO·v²·d` | Resistência aerodinâmica (`C_AERO = 0,000302 m⁻¹`) |

Os coeficientes `FR_G` e `C_AERO` são os valores da formulação VSP adotada como referência. Este projeto **não reivindica validação específica para veículos pesados (HDV)**; o resultado deve ser interpretado como indicador energético comparativo entre rotas, e não como previsão calibrada de consumo de combustível ou emissões de uma frota real.

**Adaptação para passos andinos:** quando `alt_passo_m` está definido, Δh é calculado até o pico, e não apenas até o destino. A energia potencial da descida posterior não é recuperada. Essa é uma hipótese de modelagem deste projeto para evitar subestimar o custo de cruzar os Andes; não é uma regra estabelecida pelos trabalhos de VSP citados.

O ganho altimétrico é truncado em zero nas descidas. Essa decisão representa
energia gravitacional não recuperada e garante pesos não negativos, uma
pré-condição do Dijkstra. O grafo continua **direcionado**: o custo de u → v
pode diferir de v → u porque uma direção acumula subida enquanto a inversa
trata a descida como ganho nulo.

Martins também acumula somente ganho positivo de elevação. Ainda assim, energia
e subida acumulada não são objetivos equivalentes, pois o custo VSP inclui os
termos de distância, rolamento e aerodinâmica. Portanto, a rota do Dijkstra não
precisa pertencer à fronteira `(distância, subida)` de Martins.

---

## Algoritmos

### Dijkstra — menor custo energético

Encontra o caminho de **menor energia total [J/kg]** entre origem e destino.

- **Complexidade:** O((V + E) log V) com min-heap
- **Pré-condição:** todos os pesos ≥ 0 (verificável via `verificar_pesos_positivos` em `cost.py`)
- **Saída:** `ResultadoDijkstra` com `caminho`, `custo_total`, `nos_expandidos`, `tempo_us`

### Martins — fronteira de Pareto

Determina os vetores de custo não dominados nos critérios `(distância [km], ganho de elevação [m])` e retorna uma rota representativa para cada par de valores. Caminhos distintos com exatamente o mesmo vetor de custo são consolidados.

- **Complexidade:** dependente da quantidade de rótulos gerados. Como o número de caminhos não dominados pode crescer exponencialmente, não há garantia geral de O(V²); `ResultadoMartins.rotulos_expandidos` permite caracterizar o custo observado.
- **Critérios:** distância total e ganho de elevação acumulado (somente subida; descida dissipada)
- **Saída:** `ResultadoMartins` com `fronteira_pareto` — lista de `(dist_km, subida_m, caminho)` — e `rotulos_expandidos`
- Cada rótulo armazena `(dist, subida, pred_node, pred_idx)` para reconstrução do caminho

---

## Como executar a avaliação

Instale a dependência gráfica e execute a partir da raiz do projeto:

```bash
python -m pip install -r requirements.txt
python main.py
```

Por padrão, o experimento usa origem `Santos`, destinos `Antofagasta` e `Iquique` e velocidade de 80 km/h. Outros valores podem ser informados pela CLI:

```bash
python main.py --origem Santos --destinos Antofagasta --velocidade-kmh 80
```

Para cada destino, o terminal apresenta um bloco para a rota do Dijkstra e um
para cada solução retornada por Martins. Cada bloco informa:

- caminho completo;
- custo energético total em J/kg;
- distância total em quilômetros;
- subida acumulada em metros;
- nós expandidos pelo Dijkstra ou rótulos expandidos pelo Martins;
- tempo da execução principal em microssegundos;
- passo andino utilizado, quando houver.

No caso de Martins, a quantidade de rótulos e o tempo são totais da execução
que produziu toda a fronteira de Pareto; por isso, esses valores se repetem nos
blocos das rotas retornadas.

Os tamanhos padrão dos experimentos podem ser alterados sem modificar o código:

```bash
python main.py \
  --repeticoes-desempenho 1000 \
  --simulacoes-monte-carlo 2000 \
  --seed 42
```

Para cada destino são gerados em `outputs/evaluation/<destino>/`:

- `rotas.csv` e `resultado.json`, com as métricas comuns de todas as rotas;
- `rotas.png`, com a melhor rota VSP e cada solução de Martins;
- `fronteira_pareto.png`, com Dijkstra como referência externa;
- `comparacao_metricas.png`, com energia, distância e subida.
- `desempenho.csv/json/png`, com os tempos brutos, média, desvio padrão, IC 95% e Mann-Whitney unilateral;
- `sensibilidade.csv/json/png`, com as execuções a 40, 60, 80, 100 e 120 km/h e as correlações de Pearson para `v` e `v²`;
- `robustez.csv/json/png`, com o tamanho da fronteira em cada uma das 2.000 simulações Monte Carlo.

A comparação principal é entre duas formas de ponderar as arestas: energia escalar VSP, otimizada por Dijkstra, e custo vetorial `(distância, subida)`, otimizado por Martins. A presença da rota do Dijkstra na fronteira é uma análise de compatibilidade entre objetivos, não um teste de correção dos algoritmos.

No benchmark, a ordem de execução dos algoritmos é randomizada em cada repetição após uma fase de aquecimento. O teste Mann-Whitney usa a hipótese alternativa `tempo(Dijkstra) < tempo(Martins)`. Na sensibilidade, `Pearson(v, energia)` atende à análise proposta, enquanto `Pearson(v², energia)` verifica a relação quadrática esperada pela própria formulação VSP.

No Monte Carlo, cada distância bidirecional recebe uma única perturbação normal com desvio padrão de 5%, preservada nos dois sentidos. As altitudes das cidades e dos passos recebem perturbação normal com desvio padrão de 30 m. Distâncias são truncadas em valor estritamente positivo e a seed é registrada para reprodução. Essa etapa é uma análise de estabilidade sob incerteza, não uma implementação de PARO.

## Execução manual

Execute a partir do diretório `src/`:

```bash
cd src/

# Verificar integridade do grafo e pesos
python -c "
from dados import construir_grafo
from cost import verificar_pesos_positivos

g = construir_grafo()
print(f'Cidades: {len(g.cidades)}, Arestas: {sum(len(v) for v in g.adj.values())}')
neg = verificar_pesos_positivos(g, velocidade_ms=22.2)
print(f'Arestas negativas: {len(neg)}')
"

# Rodar Dijkstra
python -c "
from dados import construir_grafo
from search_algorithms.dijkstra import dijkstra

g = construir_grafo()
r = dijkstra(g, 'Santos', 'Antofagasta', velocidade_ms=22.2)
print('Caminho:', ' -> '.join(r.caminho))
print(f'Custo: {r.custo_total:.0f} J/kg')
"

# Rodar Martins
python -c "
from dados import construir_grafo
from search_algorithms.martins import martins

g = construir_grafo()
m = martins(g, 'Santos', 'Antofagasta')
for dist, subida, caminho in m.fronteira_pareto:
    print(f'{dist:.0f} km | {subida:.0f} m subida | {\" -> \".join(caminho)}')
"
```

Os algoritmos usam apenas a biblioteca padrão do Python 3.10+. A geração dos gráficos da avaliação requer Matplotlib.

---

## Referencias

**Modelo VSP — formulação original:**
> Jiménez-Palacios, J.L. (1999). *Understanding and Quantifying Motor Vehicle Emissions with Vehicle Specific Power and TILDAS Remote Sensing*. Ph.D. Thesis, Massachusetts Institute of Technology. [http://hdl.handle.net/1721.1/44505](http://hdl.handle.net/1721.1/44505)

**Modelo VSP — referência de apoio:**
> Jiang, B. et al. (2025). Impact of Road Gradient on Fuel Consumption of Light-Duty Diesel Vehicles. *Atmosphere*, 16(2):143. O estudo trata de veículos leves a diesel e é usado apenas como apoio sobre os efeitos de inclinação e velocidade, não como validação para HDV. [https://doi.org/10.3390/atmos16020143](https://doi.org/10.3390/atmos16020143)

**Algoritmo de Martins — caminho mínimo multiobjetivo:**
> Martins, E.Q.V. (1984). On a Multicriteria Shortest Path Problem. *European Journal of Operational Research*, 16(2), 236–245. [https://www.sciencedirect.com/science/article/pii/0377221784900778](https://www.sciencedirect.com/science/article/pii/0377221784900778)
