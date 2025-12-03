from typing import Generator, List, Tuple, Dict, Optional, Set

def mst_prim_generator(grafo, origem: str) -> Generator[dict, None, List[Tuple[str, str]]]:
    """
    Seleciona a aresta de menor peso varrendo uma lista de candidatos.
    """
    visitados: Set[str] = {origem}
    mst_arestas: List[Tuple[str, str]] = []
    custo_total = 0.0

    fronteira: List[Tuple[float, str, str]] = []
    
    for v, w in grafo.vizinhos(origem):
        fronteira.append((w, origem, v))
        yield {"tipo": "mst_check", "de": origem, "para": v, "peso": w}

    yield {"tipo": "msg", "texto": f"Construindo MST via Prim (Manual) a partir de {origem}..."}

    while len(visitados) < len(grafo.planetas) and fronteira:
        
        fronteira = [aresta for aresta in fronteira if aresta[2] not in visitados]
        
        if not fronteira:
            break
            
        melhor_aresta = fronteira[0]
        idx_melhor = 0
        
        for i in range(1, len(fronteira)):
            if fronteira[i][0] < melhor_aresta[0]:
                melhor_aresta = fronteira[i]
                idx_melhor = i
        
        peso, u, v = fronteira.pop(idx_melhor)
        
        visitados.add(v)
        mst_arestas.append((u, v))
        custo_total += peso
        
        yield {"tipo": "mst_add", "de": u, "para": v, "peso": peso, "mst": list(mst_arestas)}
        
        for vizinho, w_vizinho in grafo.vizinhos(v):
            if vizinho not in visitados:
                fronteira.append((w_vizinho, v, vizinho))
                yield {"tipo": "mst_check", "de": v, "para": vizinho, "peso": w_vizinho}

    yield {"tipo": "mst_fim", "mst": list(mst_arestas), "custo_total": custo_total}
    return mst_arestas