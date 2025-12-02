import math
from typing import Generator, List, Dict, Optional, Tuple

def bellman_ford_generator(grafo, origem: str, destino: str) -> Generator[dict, None, Tuple[List[str], float]]:
    """
    Algoritmo de Bellman-Ford para caminho mínimo.
    Relaxa todas as arestas |V| - 1 vezes.
    """
    dist: Dict[str, float] = {p: math.inf for p in grafo.planetas}
    prev: Dict[str, Optional[str]] = {p: None for p in grafo.planetas}
    dist[origem] = 0.0
    
    vertices = list(grafo.planetas.keys())
    arestas = list(grafo.arestas())
    num_v = len(vertices)

    yield {"tipo": "msg", "texto": f"Iniciando Bellman-Ford. Relaxando arestas para calibrar rotas de {origem}..."}

    for i in range(num_v - 1):
        mudou_algo = False
        yield {"tipo": "msg", "texto": f"Ciclo de relaxamento {i+1}/{num_v-1}..."}
        
        for aresta in arestas:
            if not aresta.ativa: continue
            
            direcoes = [(aresta.u, aresta.v)]
            if not aresta.dirigida:
                direcoes.append((aresta.v, aresta.u))
            
            for u, v in direcoes:
                if dist[u] != math.inf and dist[u] + aresta.peso < dist[v]:
                    dist[v] = dist[u] + aresta.peso
                    prev[v] = u
                    mudou_algo = True
                    yield {"tipo": "bf_relax", "de": u, "para": v, "nova_dist": dist[v], "prev": dict(prev)}
        
        if not mudou_algo:
            yield {"tipo": "msg", "texto": "Nenhuma melhoria detectada neste ciclo. Otimização concluída prematuramente."}
            break

    for aresta in arestas:
        if not aresta.ativa: continue
        u, v = aresta.u, aresta.v
        if dist[u] != math.inf and dist[u] + aresta.peso < dist[v]:
             yield {"tipo": "msg", "texto": "ERRO CRÍTICO: Ciclo de peso negativo detectado! O sistema é instável."}
             return ([], math.inf)

    caminho: List[str] = []
    if dist[destino] < math.inf:
        cur: Optional[str] = destino
        while cur is not None:
            caminho.append(cur)
            cur = prev[cur]
        caminho.reverse()

    yield {"tipo": "djk_fim", "caminho": list(caminho), "custo": float(dist[destino])} 
    return (caminho, dist[destino])