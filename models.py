from typing import Tuple

class Planeta:
    def __init__(self, nome: str, faccao_inimiga: str, pos: Tuple[int, int],
                 status_liberacao: int = 0, ativo_na_missao: bool = True):
        self.nome = nome
        self.faccao_inimiga = faccao_inimiga
        self.status_liberacao = status_liberacao
        self.ativo_na_missao = ativo_na_missao
        self.pos = pos

class Aresta:
    def __init__(self, u: str, v: str, peso: float = 1.0, ativa: bool = True, dirigida: bool = False):
        self.u = u
        self.v = v
        self.peso = peso
        self.ativa = ativa
        self.dirigida = dirigida