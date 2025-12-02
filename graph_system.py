from __future__ import annotations
import math
import random
import heapq
from collections import deque
from typing import Dict, List, Tuple, Optional, Iterable, Generator, Set
from models import Planeta, Aresta

class MapaGalactico:
    """Representação por Lista de Adjacência e Algoritmos."""
    def __init__(self):
        self.planetas: Dict[str, Planeta] = {}
        self.adj: Dict[str, List[Aresta]] = {}

    def adicionar_planeta(self, p: Planeta) -> None:
        if p.nome not in self.planetas:
            self.planetas[p.nome] = p
            self.adj[p.nome] = []

    def adicionar_rota(self, a: str, b: str, peso: float = 1.0, bidirecional: bool = True) -> None:
        self._add_aresta(a, b, peso, ativa=True, dirigida=not bidirecional)
        if bidirecional:
            self._add_aresta(b, a, peso, ativa=True, dirigida=False)

    def adicionar_rota_dirigida(self, a: str, b: str, peso: float = 1.0) -> None:
        self._add_aresta(a, b, peso, ativa=True, dirigida=True)

    def _add_aresta(self, u: str, v: str, peso: float, ativa: bool, dirigida: bool) -> None:
        if u in self.planetas and v in self.planetas:
            self.adj[u].append(Aresta(u, v, peso, ativa, dirigida))

    def remover_rota_aleatoria(self) -> Optional[Tuple[str, str]]:
        candidatas = [(u, e) for u, lst in self.adj.items() for e in lst if e.ativa]
        if not candidatas:
            return None
        u, e = random.choice(candidatas)
        e.ativa = False
        if not e.dirigida:
            for ex in self.adj.get(e.v, []):
                if (not ex.dirigida) and ex.v == u and ex.ativa:
                    ex.ativa = False
                    break
        return (e.u, e.v)

    def vizinhos(self, u: str) -> Iterable[Tuple[str, float]]:
        for e in self.adj.get(u, []):
            if e.ativa:
                yield (e.v, e.peso)

    def arestas(self) -> Iterable[Aresta]:
        for u, lst in self.adj.items():
            for e in lst:
                yield e

    def bfs_generator(self, origem: str) -> Generator[dict, None, Set[str]]:
        visitados: Set[str] = set()
        fila = deque([origem])
        visitados.add(origem)
        nivel = {origem: 0}
        yield {"tipo": "msg", "texto": f"Iniciando Protocolo de Disseminação Democrática a partir de {origem}!"}
        while fila:
            u = fila.popleft()
            yield {"tipo": "bfs_visit", "u": u, "nivel": nivel[u], "visitados": set(visitados)}
            for v, _ in self.vizinhos(u):
                if v not in visitados:
                    visitados.add(v)
                    nivel[v] = nivel[u] + 1
                    fila.append(v)
                    yield {"tipo": "bfs_enfileira", "de": u, "para": v, "nivel": nivel[v], "visitados": set(visitados)}
        yield {"tipo": "msg", "texto": "Todos os planetas alcançáveis foram assegurados!"}
        return visitados

    def dijkstra_generator(self, origem: str, destino: str) -> Generator[dict, None, Tuple[List[str], float]]:
        dist: Dict[str, float] = {p: math.inf for p in self.planetas}
        prev: Dict[str, Optional[str]] = {p: None for p in self.planetas}
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
            for v, w in self.vizinhos(u):
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

    def detecting_ciclo_generator(self) -> Generator[dict, None, Optional[List[str]]]:
        cor: Dict[str, int] = {p: 0 for p in self.planetas}
        pai: Dict[str, Optional[str]] = {p: None for p in self.planetas}
        achou: Optional[List[str]] = None

        def dfs(u: str) -> Generator[dict, None, bool]:
            nonlocal achou
            cor[u] = 1
            yield {"tipo": "dfs_enter", "u": u, "cor": dict(cor)}
            for v, _ in self.vizinhos(u):
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
        for s in self.planetas:
            if cor[s] == 0:
                if (yield from dfs(s)):
                    break
        if achou:
            yield {"tipo": "ciclo_encontrado", "ciclo": list(achou)}
        else:
            yield {"tipo": "msg", "texto": "Nenhum circuito psíquico detectado."}
        return achou

    def encontrar_componentes_conexos(self) -> List[Set[str]]:
        """Encontra todos os subgrafos desconectados (componentes conexos)."""
        componentes = []
        visitados_globais = set()
        for nome_planeta in self.planetas:
            if nome_planeta not in visitados_globais:
                componente_atual = set()
                fila = [nome_planeta]
                visitados_locais = {nome_planeta}
                
                while fila:
                    u = fila.pop(0)
                    componente_atual.add(u)
                    vizinhos_u = {v for v, _ in self.vizinhos(u)}
                    for v in vizinhos_u:
                        if v not in visitados_locais:
                            visitados_locais.add(v)
                            fila.append(v)
                
                componentes.append(componente_atual)
                visitados_globais.update(componente_atual)
        return componentes