import math
from typing import Generator, List, Tuple, Dict, Optional, Set

def dijkstra_generator(grafo, origem: str, destino: str) -> Generator[dict, None, Tuple[List[str], float]]:
    """
    Algoritmo de Dijkstra.
    Usa busca linear para encontrar o nó de menor distância.
    """
    dist: Dict[str, float] = {p: math.inf for p in grafo.planetas}
    prev: Dict[str, Optional[str]] = {p: None for p in grafo.planetas}
    dist[origem] = 0.0
    
    nao_visitados = set(grafo.planetas.keys())
    
    yield {"tipo": "msg", "texto": f"Iniciando Dijkstra (Modo Manual). Calculando rotas de {origem}..."}
    
    while nao_visitados:
        u = None
        menor_dist = math.inf
        
        for node in nao_visitados:
            if dist[node] < menor_dist:
                menor_dist = dist[node]
                u = node
        
        if u is None or dist[u] == math.inf:
            break
            
        nao_visitados.remove(u)
        yield {"tipo": "djk_visita", "u": u, "dist": dict(dist), "prev": dict(prev)}
        
        if u == destino:
            break
            
        for v, w in grafo.vizinhos(u):
            if v in nao_visitados:
                alt = dist[u] + w
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    
                    yield {"tipo": "djk_relax", "de": u, "para": v, "nova_dist": dist[v], "prev": dict(prev)}
    
    caminho: List[str] = []
    if dist[destino] < math.inf:
        cur: Optional[str] = destino
        while cur is not None:
            caminho.append(cur)
            cur = prev[cur]
        caminho.reverse()
        
    yield {"tipo": "djk_fim", "caminho": list(caminho), "custo": float(dist[destino])}
    return (caminho, dist[destino])