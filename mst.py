import heapq
from typing import Generator, List, Tuple, Dict, Optional, Set

def mst_prim_generator(grafo, origem: str) -> Generator[dict, None, List[Tuple[str, str]]]:
    """
    Algoritmo de Prim para Árvore Geradora Mínima (MST).
    Recebe:
        grafo: Instância de MapaGalactico
        origem: Nome do planeta inicial
    """
    visitados: Set[str] = set()
    pq: List[Tuple[float, str, Optional[str]]] = [(0.0, origem, None)]
    mst_arestas: List[Tuple[str, str]] = []
    custo_total = 0.0

    yield {"tipo": "msg", "texto": f"Iniciando construção da Rede de Abastecimento (MST) via Prim a partir de {origem}..."}

    while pq:
        peso, u, pai = heapq.heappop(pq)

        if u in visitados:
            continue

        visitados.add(u)
        if pai is not None:
            mst_arestas.append((pai, u))
            custo_total += peso
            yield {"tipo": "mst_add", "de": pai, "para": u, "peso": peso, "mst": list(mst_arestas)}

        if len(visitados) == len(grafo.planetas):
            break

        for v, w in grafo.vizinhos(u):
            if v not in visitados:
                heapq.heappush(pq, (w, v, u))
                yield {"tipo": "mst_check", "de": u, "para": v, "peso": w}

    yield {"tipo": "mst_fim", "mst": list(mst_arestas), "custo_total": custo_total}
    return mst_arestas