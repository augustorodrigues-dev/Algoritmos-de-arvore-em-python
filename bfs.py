from collections import deque
from typing import Generator, Set

def bfs_generator(grafo, origem: str) -> Generator[dict, None, Set[str]]:
    """
    Algoritmo BFS (Busca em Largura) para a Fase 1.
    Recebe:
        grafo: Instância de MapaGalactico
        origem: Nome do planeta inicial
    """
    visitados: Set[str] = set()
    fila = deque([origem])
    visitados.add(origem)
    nivel = {origem: 0}
    
    yield {"tipo": "msg", "texto": f"Iniciando Protocolo de Disseminação Democrática a partir de {origem}!"}
    
    while fila:
        u = fila.popleft()
        yield {"tipo": "bfs_visit", "u": u, "nivel": nivel[u], "visitados": set(visitados)}

        for v, _ in grafo.vizinhos(u):
            if v not in visitados:
                visitados.add(v)
                nivel[v] = nivel[u] + 1
                fila.append(v)
                yield {"tipo": "bfs_enfileira", "de": u, "para": v, "nivel": nivel[v], "visitados": set(visitados)}
                
    yield {"tipo": "msg", "texto": "Todos os planetas alcançáveis foram assegurados!"}
    return visitados