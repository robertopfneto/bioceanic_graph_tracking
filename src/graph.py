### Graph data structure

# Grafo DIRECIONADO: custo de v -> u é diferente de u->v (anisotropic cost)

from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True) # imutabilidade dos dados do vértice (cidade)
class Cidade:
    nome: str
    lat: float
    lon: float
    altitude_m: float # acima do nivel do mar

@dataclass(frozen=True)
class Aresta:
    origem: str
    destino: str
    dist_km: float

    alt_passo_m: Optional[float] # passagem de montanha, usado em rotas perto do chile
    
    
@dataclass
class Grafo:
    cidades: dict = field(default_factory=dict) # cria dicionario limpo para cidades
    adj: dict = field(default_factory=dict) # cria dicionario limpo para cidades
    
    ## métodos protegidos
    def __len__(self):
        return len(self.cidades)
    
    # metodos privados
    def vizinhos(self, nome: str) -> list: # lista de adjacencia do grafo
        return self.adj.get(nome, [])

    def _get_degree(self, nome: str) -> int:
        return len(self.vizinhos(nome))

    def adicionar_cidade(self, cidade: Cidade):
        if cidade.nome not in self.adj: # se a cidade não existir
            self.adj[cidade.nome] = []
            self.cidades[cidade.nome] = cidade

    def adicionar_aresta(self, aresta: Aresta):
        # adiciona UMA aresta direcionada (u -> v)
        if aresta.origem not in self.adj:
            raise ValueError(f"Cidade origem '{aresta.origem}' não existe no grafo.")
        if aresta.destino not in self.adj:
            raise ValueError(f"Cidade destino '{aresta.destino}' não existe no grafo.")

        self.adj[aresta.origem].append(aresta)

    def adicionar_aresta_bidirecional(self, aresta: Aresta):
        # adiciona DUAS arestas direcionadas (u -> v) e (v -> u)
        self.adicionar_aresta(aresta)
        aresta_inversa = Aresta(
            origem=aresta.destino,
            destino=aresta.origem,
            dist_km=aresta.dist_km,
            alt_passo_m=aresta.alt_passo_m,
        )
        self.adicionar_aresta(aresta_inversa)

    
    def validate_graph_integrity(self):
        errors = []
        becos = [c for c in self.cidades if self._get_degree(c) == 0]
        if becos:
            errors.append({
                "tipo": "cidade_sem_arestas",
                "cidades": becos
            })

        for cidade in self.cidades:
            for aresta in self.adj.get(cidade, []):
                if aresta.destino not in self.cidades:
                    errors.append({
                        "tipo": "destino_inexistente",
                        "origem": cidade,
                        "destino": aresta.destino
                    })
        
        return errors, len(errors)