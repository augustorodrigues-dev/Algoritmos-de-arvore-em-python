from __future__ import annotations
import random
from typing import Dict, List, Tuple, Optional, Iterable, Set
from models import Planeta, Aresta

class MapaGalactico:
    """Representação por Lista de Adjacência (Dados apenas)."""
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
        """Retorna iterador de (vizinho, peso) para arestas ativas."""
        for e in self.adj.get(u, []):
            if e.ativa:
                yield (e.v, e.peso)

    def arestas(self) -> Iterable[Aresta]:
        for u, lst in self.adj.items():
            for e in lst:
                yield e

    def encontrar_componentes_conexos(self) -> List[Set[str]]:
        """Encontra todos os subgrafos desconectados (usado no evento de dano)."""
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