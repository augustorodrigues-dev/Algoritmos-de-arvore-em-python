from typing import Generator, List, Dict, Optional

def detecting_ciclo_generator(grafo) -> Generator[dict, None, Optional[List[str]]]:
    """
    Algoritmo DFS para detecção de ciclos (Fase 3).
    Recebe:
        grafo: Instância de MapaGalactico
    """
    cor: Dict[str, int] = {p: 0 for p in grafo.planetas} # 0: branco, 1: cinza, 2: preto
    pai: Dict[str, Optional[str]] = {p: None for p in grafo.planetas}
    achou: Optional[List[str]] = None

    def dfs(u: str) -> Generator[dict, None, bool]:
        nonlocal achou
        cor[u] = 1 # Cinza (visitando)
        yield {"tipo": "dfs_enter", "u": u, "cor": dict(cor)}
        
        for v, _ in grafo.vizinhos(u):
            if cor[v] == 0:
                pai[v] = u
                yield {"tipo": "dfs_tree", "de": u, "para": v}
                if (yield from dfs(v)):
                    return True
            elif cor[v] == 1:
                yield {"tipo": "dfs_backedge", "de": u, "para": v}
                ciclo = [v, u]
                x = u
                while pai[x] is not None and pai[x] != v:
                    x = pai[x]
                    ciclo.append(x)
                ciclo.reverse()
                achou = ciclo
                return True
                
        cor[u] = 2 
        yield {"tipo": "dfs_exit", "u": u, "cor": dict(cor)}
        return False

    yield {"tipo": "msg", "texto": "Varredura psíquica iniciada. Procurando paradoxos de rota..."}
    
    for s in grafo.planetas:
        if cor[s] == 0:
            if (yield from dfs(s)):
                break
                
    if achou:
        yield {"tipo": "ciclo_encontrado", "ciclo": list(achou)}
    else:
        yield {"tipo": "msg", "texto": "Nenhum circuito psíquico detectado."}
    return achou