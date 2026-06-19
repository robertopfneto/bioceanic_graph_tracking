# bioceanic_graph_tracking

Modelagem e otimização de rotas na **Rota Bioceânica de Capricórnio (Rota 4)** — trecho Santos (BR) → Antofagasta/Iquique (CL), atravessando Paraguai e Argentina. O projeto fundamenta um artigo acadêmico que compara estratégias de rota por dois critérios: **custo energético** (modelo VSP) e **eficiência multiobjetivo** (fronteira de Pareto distância × ganho de elevação).

---

## Estrutura do projeto

```
bioceanic_graph_tracking/
├── main.py                          # ponto de entrada (stub)
├── src/
│   ├── graph.py                     # estruturas de dados: Cidade, Aresta, Grafo
│   ├── cost.py                      # função de custo energético (modelo VSP)
│   ├── dados.py                     # dados da rota (26 cidades, 31 arestas bidirecionais)
│   └── search_algorithms/
│       ├── dijkstra.py              # menor caminho mono-critério (energia mínima)
│       └── martins.py               # menor caminho multi-critério (fronteira de Pareto)
└── utils/
    └── evaluation.py                # métricas comparativas (stub)
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

---

## Modelo de custo energético (VSP)

O custo de travessia de cada aresta é calculado como **energia específica [J/kg]** pela formulação VSP (*Vehicle Specific Power*):

```
E = G·Δh  +  FR_G·d  +  C_AERO·v²·d
```

| Termo | Significado |
|-------|-------------|
| `G·Δh` | Energia gravitacional (`G = 9,81 m/s²`) |
| `FR_G·d` | Resistência de rolamento (`FR_G = 0,132 m/s²`) |
| `C_AERO·v²·d` | Resistência aerodinâmica (`C_AERO = 0,000302 (m/s)⁻²`) |

Os coeficientes `FR_G` e `C_AERO` são validados para **HDV (veículo pesado de carga) a 80 km/h** em regime de cruzeiro.

**Tratamento especial para passos andinos:** quando `alt_passo_m` está definido, Δh é calculado até o pico (não até o destino), pois a energia de descida é dissipada em frenagem — evita subestimar o custo de cruzar os Andes.

O grafo é **direcionado**: o custo de u → v difere de v → u em razão do Δh assimétrico.

---

## Algoritmos

### Dijkstra — menor custo energético

Encontra o caminho de **menor energia total [J/kg]** entre origem e destino.

- **Complexidade:** O((V + E) log V) com min-heap
- **Pré-condição:** todos os pesos ≥ 0 (verificável via `verificar_pesos_positivos` em `cost.py`)
- **Saída:** `ResultadoDijkstra` com `caminho`, `custo_total`, `nos_expandidos`, `tempo_us`

### Martins — fronteira de Pareto

Determina **todos os caminhos Pareto-ótimos** nos critérios `(distância [km], ganho de elevação [m])`.

- **Complexidade:** O(V²) no pior caso
- **Critérios:** distância total e ganho de elevação acumulado (somente subida; descida dissipada)
- **Saída:** `ResultadoMartins` com `fronteira_pareto` — lista de `(dist_km, subida_m, caminho)` — e `rotulos_expandidos`
- Cada rótulo armazena `(dist, subida, pred_node, pred_idx)` para reconstrução do caminho

---

## Como executar

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

Sem dependências externas — apenas biblioteca padrão do Python 3.10+.

---

## Referencias

**Modelo VSP — formulação original:**
> Jiménez-Palacios, J.L. (1999). *Understanding and Quantifying Motor Vehicle Emissions with Vehicle Specific Power and TILDAS Remote Sensing*. Ph.D. Thesis, Massachusetts Institute of Technology. Conforme citado em Jiang et al. (2025).

**Modelo VSP — aplicação a HDV (veículos pesados):**
> Gonçalves, G.A., Mendes, T. & Coelho, M. (2016). Impact of driving styles on greenhouse gas emissions from urban freight distribution. *Transportation Research Part D*, 46, 15–31. [https://doi.org/10.1016/j.trd.2016.03.009](https://doi.org/10.1016/j.trd.2016.03.009)

**Modelo VSP — referência de apoio:**
> Jiang, Y. et al. (2025). Vehicle Specific Power-Based Emission Characterization. *Atmosphere*, 16(2):143. [https://doi.org/10.3390/atmos16020143](https://doi.org/10.3390/atmos16020143)

**Algoritmo de Martins — caminho mínimo multiobjetivo:**
> Martins, E.Q.V. (1984). On a Multicriteria Shortest Path Problem. *European Journal of Operational Research*, 16(2), 236–245. [https://doi.org/10.1016/0377-2217(84)90077-8](https://doi.org/10.1016/0377-2217(84)90077-8)
