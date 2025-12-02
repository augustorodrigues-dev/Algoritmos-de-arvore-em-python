import math
import heapq
from typing import Generator, List, Tuple, Dict, Optional, Set

def dijkstra_generator(grafo, origem: str, destino: str) -> Generator[dict, None, Tuple[List[str], float]]:
    """
    Algoritmo de Dijkstra para a Fase 2.
    Recebe:
        grafo: Instância de MapaGalactico
        origem: Nome do planeta inicial
        destino: Nome do planeta final
    """

    dist: Dict[str, float] = {p: math.inf for p in grafo.planetas}
    prev: Dict[str, Optional[str]] = {p: None for p in grafo.planetas}
    dist[origem] = 0.0
    pq: List[Tuple[float, str]] = [(0.0, origem)]
    visitados: Set[str] = set()
    
    yield {"tipo": "msg", "texto": f"Calculando logística ótima (Dijkstra) de {origem} até {destino}..."}
    
    while pq:
        d, u = heapq.heappop(pq)
        
        if u in visitados:
            continue
        visitados.add(u)
        
        yield {"tipo": "djk_visita", "u": u, "dist": dict(dist), "prev": dict(prev)}
        
        if u == destino:
            break
            
        for v, w in grafo.vizinhos(u):
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))
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