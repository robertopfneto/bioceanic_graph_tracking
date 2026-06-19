# complexidade (O(V+E)LOG V) com fila de prioridade, onde V é o número de vértices e E o numero de arestas

import heapq
import math
from dataclasses import dataclass
from typing import Optional

from graph import Grafo
from cost import calcular_energia


@dataclass
class ResultadoDijkstra:
    caminho: list #lista das cidades da rota
    custo_total: float # (J/kg)
    nos_expandidos: int # nos removidos da fila (metrica de eficiencia)
    tempo_us: float = 0.0 # tempo de exec em microsegundos
    
    
# somente pesos nao negativos
def dijkstra(grafo: Grafo, origem: str, destino: str, velocidade_ms: float) -> ResultadoDijkstra:
    
    if origem not in grafo.cidades:
        raise ValueError(f"Origem '{origem}' não existe no grafo.")
    if destino not in grafo.cidades:
        raise ValueError(f"Destino '{destino}' não existe no grafo.")

    dist = {c: math.inf for c in grafo.cidades} # so sei o inicio da origem, todos os outros sao "infinitos" 
    prev = {c: None for c in grafo.cidades}
    dist[origem] = 0.0
    
    #min heap (custo_acumulado, nome_cidade)
    fila = [(0.0, origem)] # o custo pra sair da origem é zero // cria fila de prioridade
    visitados = set()
    nos_expandidos = 0 
    
    while fila:
        custo_atual, u = heapq.heappop(fila)

        # Protege contra copias obsoletas
        if u in visitados:
            continue

        visitados.add(u)
        nos_expandidos += 1
        
        if u == destino:
            break
        
        for aresta in grafo.vizinhos(u):
            v = aresta.destino
            
            if v in visitados:
                continue
            
            cidade_u = grafo.cidades[u]
            cidade_v = grafo.cidades[v]
            peso = calcular_energia(cidade_u, cidade_v, aresta, velocidade_ms)
            
            novo_custo = custo_atual + peso
            if novo_custo < dist[v]:
                dist[v] = novo_custo
                prev[v] = u
                heapq.heappush(fila, (novo_custo,v)) # coloca na fila de prioridade
                
    # reconstrução do caminho
    
    # verifica se o caminho existe
    if dist[destino] == math.inf:
        return ResultadoDijkstra(
            caminho=[],
            custo_total=math.inf,
            nos_expandidos=nos_expandidos
        )
      
    # inicializa reconstrução  
    caminho = []
    atual = destino
    
    while atual is not None:
        caminho.append(atual)
        atual = prev[atual]
    caminho.reverse()
    
    return ResultadoDijkstra(
        caminho=caminho,
        custo_total=dist[destino],
        nos_expandidos=nos_expandidos
    )