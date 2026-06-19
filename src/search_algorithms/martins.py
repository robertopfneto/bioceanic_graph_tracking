
"""
    Referência:
    Martins, E.Q.V. (1984). On a Multicriteria Shortest Path Problem.
    European Journal of Operational Research, 16(2), 236-245.
    DOI: 10.1016/0377-2217(84)90077-8
    url: https://www.sciencedirect.com/science/article/pii/0377221784900778
"""

# O(V^2)

import heapq
from dataclasses import dataclass
from typing import Optional
from graph import Grafo


# ---------------------------------------------------------------------------
# Estrutura de rótulo — correspondência com Martins (1984):
#   [(c1(psi), c2(psi)), (j, l)]
#   c1 = dist acumulada, c2 = subida acumulada
#   j  = pred_node (nó predecessor)
#   l  = pred_idx  (índice do rótulo em j)
# ---------------------------------------------------------------------------


@dataclass
class Label:
    dist: float # dist acumulada (km)
    subida: float # ganho de elevacap (m)
    pred_node: Optional[str] # j: nó anterior no caminho
    pred_idx: int # l: indice do rotulo de j (-1 = rotulo)
    permanent: bool = False # permanente (true) ou temporario(false)
    dominated: bool = False # marcado como dominado (euqivalente à remoção)



def domina(d1: float, s1: float, d2: float, s2: float) -> bool:
    """
    Retorna True se o rótulo (d1, s1) domina (d2, s2).
    Definição 3, Martins (1984), pág. 238:
        c^k(p') <= c^k(p) para todo k, com desigualdade estrita em algum k.
    """
    return d1 <= d2 and s1 <= s2 and (d1 < d2 or s1 < s2)
 
 
def ganho_elevacao(alt_origem: float, alt_destino: float,
                   alt_passo: Optional[float]) -> float:
    """
    Ganho de elevação de uma aresta (somente subida; descida = 0).
    Consistente com cost.py e com a premissa de não-recuperação energética.
    Para passos andinos: sobe até a cota do passo, descida dissipada.
    """
    if alt_passo is not None:
        return max(0.0, alt_passo - alt_origem)
    return max(0.0, alt_destino - alt_origem)
 
 
@dataclass
class ResultadoMartins:
    """Resultado do algoritmo de Martins."""
    fronteira_pareto: list   # [(dist_km, subida_m, caminho: list[str])]
    rotulos_expandidos: int  # total de rótulos tornados permanentes
    tempo_us: float = 0.0
 
 
# ---------------------------------------------------------------------------
# Reconstrução do caminho via ponteiros de predecessor
# Step 3 do Algorithm 1 (Martins, 1984, pág. 240):
#   "the two pointers of each label must be used"
# ---------------------------------------------------------------------------
def _reconstruir_caminho(labels: dict, destino: str, lbl_idx: int) -> list:
    """
    Reconstrói o caminho seguindo os ponteiros (pred_node, pred_idx)
    do rótulo no destino até a origem (pred_node = None).
    """
    caminho = []
    cur_node = destino
    cur_idx = lbl_idx
    while cur_node is not None:
        caminho.append(cur_node)
        lbl = labels[cur_node][cur_idx]
        cur_node = lbl.pred_node
        cur_idx = lbl.pred_idx
    caminho.reverse()
    return caminho
 
 
# ---------------------------------------------------------------------------
# Algorithm 1 — Martins (1984)
# ---------------------------------------------------------------------------
def martins(grafo: Grafo, origem: str, destino: str) -> ResultadoMartins:
    """
    Determina TODOS os caminhos Pareto-ótimos de origem a destino,
    nos critérios (distância [km], ganho de elevação [m]).
 
    Implementação do Algorithm 1 de Martins (1984), pág. 240.
 
    Pré-condição (Assumption 3, pág. 237):
        Todo ciclo deve ter custo >= 0, com pelo menos um estritamente positivo.
        Garantido pelo nosso grafo: arestas de rolamento + aerodinâmica são
        sempre positivas, tornando ciclos sempre mais caros.
 
    Parâmetros:
        grafo   : objeto Grafo com lista de adjacência
        origem  : nome da cidade de origem (s)
        destino : nome da cidade de destino (t)
 
    Retorna:
        ResultadoMartins com fronteira de Pareto em L[t]
    """
    if origem not in grafo.cidades:
        raise ValueError(f"Origem '{origem}' não existe no grafo.")
    if destino not in grafo.cidades:
        raise ValueError(f"Destino '{destino}' não existe no grafo.")
 
    # L[i] = lista de Labels associados ao nó i
    # Índices são ESTÁVEIS (nunca removemos elementos — apenas marcamos dominated)
    # Isso é necessário para que os ponteiros (pred_node, pred_idx) permaneçam válidos
    L = {c: [] for c in grafo.cidades}
 
    # Step 0: rótulo inicial em s — [(0, 0), (-, -)]
    L[origem].append(Label(dist=0.0, subida=0.0, pred_node=None, pred_idx=-1))
 
    # Fila de prioridade min-heap: (dist, subida, node, label_idx)
    # Ordem lexicográfica por (dist, subida) conforme Step 1(1) do paper
    heap = [(0.0, 0.0, origem, 0)]
    rotulos_expandidos = 0
 
    # Step 2: loop
    while heap:
        d, s, u, idx = heapq.heappop(heap)
 
        # Valida o rótulo: pode ter sido marcado permanente ou dominado
        # após ter sido inserido na fila
        lbl = L[u][idx]
        if lbl.permanent or lbl.dominated:
            continue
 
        # Step 1(1): torna permanente o menor rótulo temporário lexicográfico
        lbl.permanent = True
        rotulos_expandidos += 1
 
        # Step 1(2): propagação para todos os vizinhos j de u
        for aresta in grafo.vizinhos(u):
            v = aresta.destino
            alt_u = grafo.cidades[u].altitude_m
            alt_v = grafo.cidades[v].altitude_m
 
            # Computa os custos do novo rótulo candidato em v
            novo_d = d + aresta.dist_km
            novo_s = s + ganho_elevacao(alt_u, alt_v, aresta.alt_passo_m)
 
            # Step 1(2)(2): verifica se candidato é dominado por algum
            # rótulo ativo (não-dominado) em v
            dominado = any(
                domina(l.dist, l.subida, novo_d, novo_s)
                for l in L[v]
                if not l.dominated
            )
            if dominado:
                continue  # descarta — não adiciona à fila
 
            # Remove (marca) de L[v] os rótulos temporários dominados pelo novo
            # Rótulos permanentes nunca são dominados (invariante do algoritmo)
            for l in L[v]:
                if not l.dominated and not l.permanent:
                    if domina(novo_d, novo_s, l.dist, l.subida):
                        l.dominated = True
 
            # Adiciona novo rótulo temporário com ponteiro para (u, idx)
            novo_idx = len(L[v])
            L[v].append(Label(
                dist=novo_d,
                subida=novo_s,
                pred_node=u,
                pred_idx=idx,
            ))
            heapq.heappush(heap, (novo_d, novo_s, v, novo_idx))
 
    # Step 3: coleta rótulos permanentes e não-dominados em t (o destino)
    # Cada rótulo permanente corresponde a um caminho Pareto-ótimo
    rotulos_dest = [
        (lbl.dist, lbl.subida, i)
        for i, lbl in enumerate(L[destino])
        if lbl.permanent and not lbl.dominated
    ]
 
    # Remove duplicatas (mesmo (dist, subida) arredondado) e reconstrói caminhos
    fronteira = []
    vistos = set()
    for d, s, i in sorted(rotulos_dest):
        chave = (round(d, 4), round(s, 4))
        if chave not in vistos:
            vistos.add(chave)
            caminho = _reconstruir_caminho(L, destino, i)
            fronteira.append((d, s, caminho))
 
    return ResultadoMartins(
        fronteira_pareto=fronteira,
        rotulos_expandidos=rotulos_expandidos,
    )
 
