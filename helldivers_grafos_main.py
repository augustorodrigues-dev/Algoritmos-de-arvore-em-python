# helldivers_grafos_main.py
#
# Projeto Helldivers: Desbravando Grafos pela Super-Terra
# Versão 2.0 - Edição Aprimorada com UI, Tutoriais e Análise de Conectividade
#
# Requisitos: Python 3.10+, pygame
# Instalação: pip install pygame
# Execução: python helldivers_grafos_main.py
#
# Controles in-game (PT-BR):
#  [1] Fase 1 (Autômatos): grafo não-direcionado, não-ponderado (BFS/DFS)
#  [2] Fase 2 (Terminídeos): grafo ponderado (Dijkstra)
#  [3] Fase 3 (Iluminados): dígrafo (detecção de ciclos)
#  [B] Rodar BFS a partir do planeta selecionado (clique um planeta)
#  [D] Rodar Dijkstra (clique origem e depois destino)
#  [C] Detectar ciclo (fase 3)
#  [R] Evento aleatório (remove/derruba uma rota ativa e analisa conectividade)
#  [T] Mostrar/Esconder Tutorial da fase atual
#  [ESC] Sair
#  Clique com o mouse em um planeta para selecioná-lo.

from __future__ import annotations
import pygame
import sys
import math
import random
import heapq
from typing import Dict, List, Tuple, Optional, Iterable, Generator, Set

# ==================================================================
# ========================= CONFIGURAÇÕES ==========================
# ==================================================================

LARGURA, ALTURA = 1280, 720
RAIO_PLANETA = 20
FPS = 60

CORES_FACCAO = {
    "Aliança": (90, 180, 255),      # azul
    "Autômatos": (220, 70, 70),      # vermelho
    "Terminídeos": (240, 200, 60),  # amarelo
    "Iluminados": (170, 140, 220),  # roxo
}

# Paleta de cores
BRANCO = (240, 240, 240)
CINZA = (50, 50, 60)
CINZA_CLARO = (140, 140, 160)
VERDE = (60, 200, 120)
AMARELO = (240, 200, 60)
VERMELHO = (230, 80, 80)
AZUL = (90, 180, 255)
PRETO = (10, 12, 14)
COR_PAINEL = (28, 30, 36, 230) # Com transparência

# ==================================================================
# ============================ MODELOS =============================
# ==================================================================

class Planeta:
    # (Sem alterações nesta classe)
    def __init__(self, nome: str, faccao_inimiga: str, pos: Tuple[int, int],
                 status_liberacao: int = 0, ativo_na_missao: bool = True):
        self.nome = nome
        self.faccao_inimiga = faccao_inimiga
        self.status_liberacao = status_liberacao
        self.ativo_na_missao = ativo_na_missao
        self.pos = pos

class Aresta:
    # (Sem alterações nesta classe)
    def __init__(self, u: str, v: str, peso: float = 1.0, ativa: bool = True, dirigida: bool = False):
        self.u, self.v, self.peso, self.ativa, self.dirigida = u, v, peso, ativa, dirigida

class MapaGalactico:
    """Representação por Lista de Adjacência."""
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
        assert u in self.planetas and v in self.planetas, "Planeta inexistente"
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

    # ==================================================================
    # ========================== ALGORITMOS ============================
    # ==================================================================

    def bfs_generator(self, origem: str) -> Generator[dict, None, Set[str]]:
        # (Sem alterações neste gerador)
        from collections import deque
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
        # (Sem alterações neste gerador)
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

    def detectar_ciclo_generator(self) -> Generator[dict, None, Optional[List[str]]]:
        # (Sem alterações neste gerador)
        cor: Dict[str, int] = {p: 0 for p in self.planetas}
        pai: Dict[str, Optional[str]] = {p: None for p in self.planetas}
        achou: Optional[List[str]] = None

        def dfs(u: str) -> bool:
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

    # ---- NOVO ALGORITMO: Análise de Conectividade ----
    def encontrar_componentes_conexos(self) -> List[Set[str]]:
        """Encontra todos os subgrafos desconectados (componentes conexos)."""
        componentes = []
        visitados_globais = set()
        for nome_planeta in self.planetas:
            if nome_planeta not in visitados_globais:
                # Inicia um BFS a partir de um planeta ainda não visitado
                componente_atual = set()
                fila = [nome_planeta]
                visitados_locais = {nome_planeta}
                
                while fila:
                    u = fila.pop(0)
                    componente_atual.add(u)
                    # Para grafos não-direcionados, precisamos checar vizinhos de ambos os lados
                    vizinhos_u = {v for v, _ in self.vizinhos(u)}
                    todos_vizinhos = vizinhos_u
                    
                    for v in todos_vizinhos:
                        if v not in visitados_locais:
                            visitados_locais.add(v)
                            fila.append(v)
                
                componentes.append(componente_atual)
                visitados_globais.update(componente_atual)
        return componentes


# ==================================================================
# ======================== DADOS DAS FASES =========================
# ==================================================================

def construir_mapa_fase1() -> MapaGalactico:
    mg = MapaGalactico()
    coords = {"Super-Terra": (160, 360), "Marte": (300, 300), "Kepler": (320, 520), "Malevelon Creek": (480, 280), "Draupnir": (640, 360), "Erata Prime": (500, 130), "Zegema Beach": (320, 120), "Heeth": (800, 200), "Angel's Venture": (850, 450)}
    faccao = {p: "Autômatos" for p in coords}; faccao["Super-Terra"] = "Aliança"
    for nome, pos in coords.items(): mg.adicionar_planeta(Planeta(nome, faccao[nome], pos))
    mg.adicionar_rota("Super-Terra", "Marte"); mg.adicionar_rota("Super-Terra", "Kepler"); mg.adicionar_rota("Marte", "Malevelon Creek"); mg.adicionar_rota("Malevelon Creek", "Draupnir"); mg.adicionar_rota("Kepler", "Malevelon Creek"); mg.adicionar_rota("Marte", "Zegema Beach"); mg.adicionar_rota("Zegema Beach", "Erata Prime"); mg.adicionar_rota("Erata Prime", "Malevelon Creek"); mg.adicionar_rota("Draupnir", "Heeth"); mg.adicionar_rota("Heeth", "Angel's Venture")
    return mg

def construir_mapa_fase2() -> MapaGalactico:
    mg = MapaGalactico(); coords = {"Super-Terra": (160, 360), "Marte": (300, 300), "Kepler": (320, 520), "Malevelon Creek": (480, 280), "Draupnir": (640, 360), "Erata Prime": (500, 130), "Zegema Beach": (320, 120), "Heeth": (800, 200), "Angel's Venture": (850, 450)}
    faccao = {p: "Terminídeos" for p in coords}; faccao["Super-Terra"] = "Aliança"
    for nome, pos in coords.items(): mg.adicionar_planeta(Planeta(nome, faccao[nome], pos))
    def R(a,b,w): mg.adicionar_rota(a,b,peso=w)
    R("Super-Terra", "Marte", 2); R("Super-Terra", "Kepler", 5); R("Marte", "Malevelon Creek", 3); R("Malevelon Creek", "Draupnir", 4); R("Kepler", "Malevelon Creek", 2); R("Marte", "Zegema Beach", 5); R("Zegema Beach", "Erata Prime", 6); R("Erata Prime", "Malevelon Creek", 2); R("Draupnir", "Heeth", 7); R("Heeth", "Angel's Venture", 3)
    return mg

def construir_mapa_fase3() -> MapaGalactico:
    mg = MapaGalactico(); coords = {"Super-Terra": (160, 360), "Marte": (300, 300), "Kepler": (320, 520), "Malevelon Creek": (480, 280), "Draupnir": (640, 360), "Erata Prime": (500, 130), "Zegema Beach": (320, 120), "Heeth": (800, 200), "Angel's Venture": (850, 450)}
    faccao = {p: "Iluminados" for p in coords}; faccao["Super-Terra"] = "Aliança"
    for nome, pos in coords.items(): mg.adicionar_planeta(Planeta(nome, faccao[nome], pos))
    def RD(a,b,w=1): mg.adicionar_rota_dirigida(a,b,peso=w)
    RD("Super-Terra", "Marte"); RD("Marte", "Malevelon Creek"); RD("Malevelon Creek", "Draupnir"); RD("Draupnir", "Marte"); RD("Super-Terra", "Kepler"); RD("Kepler", "Zegema Beach"); RD("Zegema Beach", "Erata Prime"); RD("Erata Prime", "Malevelon Creek"); RD("Draupnir", "Heeth"); RD("Angel's Venture", "Heeth")
    return mg

# ==================================================================
# ======================= GERENCIADOR DE UI ========================
# ==================================================================

class UIManager:
    def __init__(self, tela, fonte_titulo, fonte_normal, fonte_pequena):
        self.tela = tela
        self.fonte_titulo = fonte_titulo
        self.fonte_normal = fonte_normal
        self.fonte_pequena = fonte_pequena
        
        try:
            self.logo = pygame.image.load("assets/logo.png").convert_alpha()
            self.logo = pygame.transform.scale(self.logo, (300, int(300 * self.logo.get_height() / self.logo.get_width())))
        except pygame.error:
            self.logo = None
            print("AVISO: 'assets/logo.png' não encontrado. Continuando sem logo.")
        
        self.tutoriais = {
            1: [
                "FASE 1: SETOR AUTÔMATO",
                "",
                "CONCEITO: Grafo não-direcionado.",
                "As rotas funcionam nos dois sentidos, como estradas.",
                "",
                "MISSÃO: Disseminar a Democracia.",
                "Use o algoritmo BFS para liberar todos os planetas",
                "alcançáveis a partir de um ponto inicial.",
                "",
                "CONTROLES:",
                " • Clique em um planeta para selecioná-lo como origem.",
                " • Pressione [B] para iniciar a varredura BFS.",
                " • Pressione [R] para simular um ataque inimigo a uma rota."
            ],
            2: [
                "FASE 2: SETOR TERMINÍDEO",
                "",
                "CONCEITO: Grafo Ponderado.",
                "Cada rota agora tem um 'custo' (combustível, tempo, risco).",
                "",
                "MISSÃO: Encontrar a Rota Logística Ótima.",
                "Use o algoritmo de Dijkstra para achar o caminho de menor",
                "custo entre dois planetas.",
                "",
                "CONTROLES:",
                " • Clique em um planeta para a ORIGEM.",
                " • Clique em outro para o DESTINO.",
                " • Pressione [D] para calcular a rota."
            ],
            3: [
                "FASE 3: SETOR ILUMINADO",
                "",
                "CONCEITO: Dígrafo (Grafo Direcionado).",
                "Rotas podem ser de mão única, como portais.",
                "",
                "MISSÃO: Detectar Paradoxo Psíquico.",
                "Use uma varredura (baseada em DFS) para encontrar 'ciclos',",
                "rotas que levam de volta ao ponto de partida.",
                "",
                "CONTROLES:",
                " • Pressione [C] para iniciar a varredura em todo o setor."
            ]
        }

    # --- CORREÇÃO APLICADA AQUI ---
    # O parâmetro 'font' agora é opcional. Se não for passado, usa a fonte normal.
    def _draw_text(self, txt: str, x: int, y: int, color=BRANCO, font=None, center_x=False, center_y=False):
        if font is None:
            font = self.fonte_normal # Usa a fonte normal como padrão
            
        surf = font.render(txt, True, color)
        rect = surf.get_rect()
        if center_x and center_y: rect.center = (x, y)
        elif center_x: rect.centerx, rect.top = x, y
        elif center_y: rect.left, rect.centery = x, y
        else: rect.topleft = (x, y)
        self.tela.blit(surf, rect)

    def draw_intro(self, typed_chars, intro_text):
        self.tela.fill(PRETO)
        if self.logo:
            self.tela.blit(self.logo, self.logo.get_rect(center=(LARGURA / 2, ALTURA / 3)))
        
        current_line = 0
        chars_to_render = typed_chars
        for i, line in enumerate(intro_text):
            if chars_to_render <= 0: break
            render_text = line[:int(chars_to_render)]
            self._draw_text(render_text, LARGURA / 2, ALTURA * 0.6 + i * 30, center_x=True)
            chars_to_render -= len(line)

        if typed_chars >= sum(len(s) for s in intro_text):
             # --- CORREÇÃO APLICADA AQUI ---
             # Usando argumentos nomeados (keyword arguments) para evitar confusão
             self._draw_text("Pressione qualquer tecla para iniciar a missão.", x=LARGURA/2, y=ALTURA - 50, color=AMARELO, center_x=True)

    def draw_hud(self, fase, msgs):
        panel_surf = pygame.Surface((LARGURA, 80))
        panel_surf.set_alpha(COR_PAINEL[3])
        panel_surf.fill(COR_PAINEL[:-1])
        self.tela.blit(panel_surf, (0,0))
        pygame.draw.line(self.tela, AMARELO, (0, 80), (LARGURA, 80), 2)

        fase_nomes = {1: "Autômatos (BFS)", 2: "Terminídeos (Dijkstra)", 3: "Iluminados (Ciclos)"}
        
        # --- CORREÇÃO APLICADA AQUI ---
        self._draw_text(f"HELLDIVERS: OPERAÇÃO GRAFOS | FASE {fase}: {fase_nomes[fase]}", x=20, y=15, font=self.fonte_titulo)
        controles = "[1-3] Mudar Fase | [T] Tutorial | [R] Evento Aleatório | [ESC] Sair"
        self._draw_text(controles, x=20, y=50)
        
        if msgs:
            last_msg = msgs[-1]
            last_msg_surf = self.fonte_normal.render(f"ÚLTIMA TRANSMISSÃO: {last_msg}", True, BRANCO)
            last_msg_rect = last_msg_surf.get_rect(topright=(LARGURA - 20, 50))
            self.tela.blit(last_msg_surf, last_msg_rect)

    def draw_tutorial(self, fase):
        panel_w, panel_h = 600, 400
        panel_x, panel_y = (LARGURA - panel_w) / 2, (ALTURA - panel_h) / 2
        
        panel_surf = pygame.Surface((panel_w, panel_h))
        panel_surf.set_alpha(COR_PAINEL[3])
        panel_surf.fill(COR_PAINEL[:-1])
        self.tela.blit(panel_surf, (panel_x, panel_y))
        pygame.draw.rect(self.tela, AMARELO, (panel_x, panel_y, panel_w, panel_h), 3)

        tutorial_text = self.tutoriais.get(fase, ["Tutorial não encontrado."])
        for i, line in enumerate(tutorial_text):
            font = self.fonte_titulo if i == 0 else self.fonte_normal
            color = AMARELO if i == 0 or "CONTROLES:" in line else BRANCO
            self._draw_text(line, x=LARGURA / 2, y=panel_y + 40 + i * 22, color=color, font=font, center_x=True)
            
        self._draw_text("Pressione qualquer tecla para fechar.", x=LARGURA / 2, y=panel_y + panel_h - 30, color=CINZA_CLARO, center_x=True)

# ==================================================================
# ======================== CLASSE PRINCIPAL ========================
# ==================================================================

class Jogo:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Helldivers: Grafos da Super-Terra v2.0")
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        self.clock = pygame.time.Clock()
        
        # Carregar Fontes
        self.fonte_titulo = pygame.font.SysFont("consolas", 22, bold=True)
        self.fonte_normal = pygame.font.SysFont("consolas", 12)
        self.fonte_pequena = pygame.font.SysFont("consolas", 11)
        self.fonte_peso_aresta = pygame.font.SysFont("consolas", 20, bold=True) # Fonte para os pesos das arestas
        
        # Gerenciador de UI
        self.ui = UIManager(self.tela, self.fonte_titulo, self.fonte_normal, self.fonte_pequena)
        
        # Carregar Background
        try:
            bg_orig = pygame.image.load("assets/background.png").convert()
            self.background = pygame.transform.scale(bg_orig, (LARGURA, ALTURA))
        except pygame.error:
            self.background = None
            print("AVISO: 'assets/background.png' não encontrado. Usando fundo sólido.")

        # Estado do Jogo
        self.game_state = "INTRO"
        self.fase = 1
        self.mapa: MapaGalactico = construir_mapa_fase1()
        self.msgs: List[str] = []
        self.anim: Optional[Generator] = None
        self.pausado = False
        self.selecao: Optional[str] = None
        self.selecao2: Optional[str] = None
        self.caminho_atual: List[str] = []
        self.ciclo_atual: List[str] = []
        self.mostrar_tutorial = True
        
        # Efeitos visuais temporários
        self.componentes_visuais: Optional[List[Set[str]]] = None
        self.componentes_timer = 0

        # Lore Intro
        self.intro_text = [
            "> Estamos sob ataque, os cara tão no teto...",
            "> Estabilizando Conexão com o Terminal de Grafos...",
            "> Conexão Estabelecida. Bem-vindo, Helldiver.",
            "> Sua Missão: Analise os Setores Inimigos usando Grafos.",
            "> Pelo Aprendizado!. Pela Super-Terra."
        ]
        self.typed_chars = 0
        self.last_char_time = 0

    def set_fase(self, f: int):
        self.fase = f
        self.anim = None; self.caminho_atual = []; self.ciclo_atual = []
        self.selecao = None; self.selecao2 = None; self.componentes_visuais = None
        
        if f == 1: self.mapa = construir_mapa_fase1()
        elif f == 2: self.mapa = construir_mapa_fase2()
        else: self.mapa = construir_mapa_fase3()
            
        fase_nomes = {1: "Autômatos", 2: "Terminídeos", 3: "Iluminados"}
        self._say(f"Setor dos {fase_nomes[f]} online. Pressione [T] para briefing da missão.")
        self.mostrar_tutorial = True

    def _say(self, texto: str):
        if len(self.msgs) > 5: self.msgs.pop(0)
        self.msgs.append(texto)
        print(f"MSG: {texto}")

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit(0)
            
            if self.game_state == "INTRO":
                if ev.type == pygame.KEYDOWN:
                    self.game_state = "JOGO"
                    self._say("Sistema operacional pronto. Selecione uma fase para começar.")
                continue

            if self.mostrar_tutorial:
                if ev.type == pygame.KEYDOWN:
                    self.mostrar_tutorial = False
                continue

            # Eventos do Jogo Principal
            if ev.type == pygame.KEYDOWN:
                key_map = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3}
                if ev.key in key_map: self.set_fase(key_map[ev.key])
                elif ev.key == pygame.K_t: self.mostrar_tutorial = True
                elif ev.key == pygame.K_r: self.evento_remover_rota()
                elif ev.key == pygame.K_b: self.iniciar_bfs()
                elif ev.key == pygame.K_d: self.iniciar_dijkstra()
                elif ev.key == pygame.K_c: self.iniciar_detecção_ciclo()

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                clicado = self._planeta_em(ev.pos)
                if clicado:
                    if not self.selecao or (self.selecao and self.selecao2):
                        self.selecao = clicado
                        self.selecao2 = None
                        self._say(f"Origem selecionada: {clicado}")
                    else:
                        self.selecao2 = clicado
                        self._say(f"Destino selecionado: {clicado}")

    def evento_remover_rota(self):
        componentes_antes = len(self.mapa.encontrar_componentes_conexos())
        removida = self.mapa.remover_rota_aleatoria()
        
        if not removida:
            self._say("Nenhuma rota disponível para sabotagem inimiga.")
            return
            
        self._say(f"Alerta! Frota inimiga destruiu a rota {removida[0]} <-> {removida[1]}.")
        
        # --- CORREÇÃO APLICADA AQUI ---
        # 1. Armazenamos a LISTA de componentes em uma nova variável.
        lista_componentes_depois = self.mapa.encontrar_componentes_conexos()
        # 2. Contamos o NÚMERO de componentes usando len().
        num_componentes_depois = len(lista_componentes_depois)
        
        # 3. Comparamos NÚMERO com NÚMERO.
        if num_componentes_depois > componentes_antes:
            # 4. Usamos o NÚMERO na mensagem e a LISTA no efeito visual.
            self._say(f"GRAVE: A perda da rota dividiu o setor! Temos {num_componentes_depois} zonas isoladas.")
            self.componentes_visuais = lista_componentes_depois
            self.componentes_timer = FPS * 5 # Efeito visual por 5 segundos
        else:
            self._say("A rede de suprimentos permanece conectada... por enquanto.")

    
    def iniciar_bfs(self):
        if self.fase != 1: self._say("BFS é um protocolo para setores não-ponderados (Fase 1)."); return
        if self.selecao:
            self.anim = self.mapa.bfs_generator(self.selecao)
        else: self._say("Selecione um planeta de origem para o BFS.")

    def iniciar_dijkstra(self):
        if self.fase != 2: self._say("Dijkstra é para logística em setores ponderados (Fase 2)."); return
        if self.selecao and self.selecao2:
            self.anim = self.mapa.dijkstra_generator(self.selecao, self.selecao2)
        else: self._say("Selecione um planeta de ORIGEM e um de DESTINO.")

    def iniciar_detecção_ciclo(self):
        if self.fase != 3: self._say("Detecção de ciclo é para paradoxos em dígrafos (Fase 3)."); return
        self.anim = self.mapa.detectar_ciclo_generator()

    def _planeta_em(self, pos) -> Optional[str]:
        for nome, p in self.mapa.planetas.items():
            if math.hypot(p.pos[0] - pos[0], p.pos[1] - pos[1]) <= RAIO_PLANETA:
                return nome
        return None

    def update(self):
        if self.game_state == "INTRO":
            if pygame.time.get_ticks() - self.last_char_time > 30: # Velocidade da digitação
                self.typed_chars += 1
                self.last_char_time = pygame.time.get_ticks()
            return

        if self.anim:
            try:
                passo = next(self.anim)
                self._processa_passo(passo)
            except StopIteration:
                self.anim = None
        
        if self.componentes_timer > 0:
            self.componentes_timer -= 1
            if self.componentes_timer == 0:
                self.componentes_visuais = None

    def _processa_passo(self, passo: dict):
        t = passo.get("tipo")
        if t == "msg": self._say(passo["texto"])
        elif t == "djk_fim":
            self.caminho_atual = passo.get("caminho", [])
            custo = passo.get("custo", math.inf)
            if self.caminho_atual: self._say(f"Rota ótima: {' -> '.join(self.caminho_atual)} (custo {custo:.1f}).")
            else: self._say("Falha logística: destino inalcançável.")
        elif t == "ciclo_encontrado":
            self.ciclo_atual = passo.get("ciclo", [])
            if self.ciclo_atual: self._say(f"ALERTA! Circuito psíquico: {' -> '.join(self.ciclo_atual)} -> {self.ciclo_atual[0]}")

    def draw(self):
        # Fundo
        if self.background: self.tela.blit(self.background, (0, 0))
        else: self.tela.fill(PRETO)
        
        if self.game_state == "INTRO":
            self.ui.draw_intro(self.typed_chars, self.intro_text)
            pygame.display.flip()
            return

        # --- Desenho do Jogo Principal ---
        # Arestas
        for e in self.mapa.arestas():
            u_pos = self.mapa.planetas[e.u].pos
            v_pos = self.mapa.planetas[e.v].pos
            cor = CINZA_CLARO if e.ativa else (70, 70, 80)
            pygame.draw.line(self.tela, cor, u_pos, v_pos, 3)
            if e.dirigida and e.ativa: self._desenhar_seta(u_pos, v_pos, cor)
            if self.fase == 2 and e.ativa: self._desenhar_peso(u_pos, v_pos, e.peso, cor)

        # Realce de caminho/ciclo
        if len(self.caminho_atual) >= 2:
            pts = [self.mapa.planetas[p].pos for p in self.caminho_atual]
            pygame.draw.lines(self.tela, VERDE, False, pts, 6)
        if len(self.ciclo_atual) >= 1:
            pts = [self.mapa.planetas[p].pos for p in self.ciclo_atual] + [self.mapa.planetas[self.ciclo_atual[0]].pos]
            pygame.draw.lines(self.tela, VERMELHO, False, pts, 6)

        # Planetas (Nós)
        for nome, p in self.mapa.planetas.items():
            cor_base = CORES_FACCAO.get(p.faccao_inimiga, AZUL)
            # Efeito de piscar para componentes
            if self.componentes_visuais and self.componentes_timer > 0:
                componente_id = -1
                for i, comp in enumerate(self.componentes_visuais):
                    if nome in comp: componente_id = i; break
                if componente_id != -1 and (self.componentes_timer // 15) % 2 == 0:
                    cor_base = [VERDE, VERMELHO, AZUL, AMARELO][componente_id % 4]

            pygame.draw.circle(self.tela, cor_base, p.pos, RAIO_PLANETA)
            pygame.draw.circle(self.tela, PRETO, p.pos, RAIO_PLANETA, 2)
            if nome == self.selecao: pygame.draw.circle(self.tela, AMARELO, p.pos, RAIO_PLANETA + 4, 3)
            if nome == self.selecao2: pygame.draw.circle(self.tela, VERDE, p.pos, RAIO_PLANETA + 4, 3)
            self.ui._draw_text(txt=nome, x=p.pos[0], y=p.pos[1] - RAIO_PLANETA - 12, font=self.ui.fonte_pequena, center_x=True)

        # UI
        self.ui.draw_hud(self.fase, self.msgs)
        if self.mostrar_tutorial:
            self.ui.draw_tutorial(self.fase)
            
        pygame.display.flip()

    def _desenhar_seta(self, a, b, cor):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        p1 = (b[0] - (RAIO_PLANETA+2) * math.cos(ang), b[1] - (RAIO_PLANETA+2) * math.sin(ang))
        L = 14
        p2 = (p1[0] - L * math.cos(ang - 0.5), p1[1] - L * math.sin(ang - 0.5))
        p3 = (p1[0] - L * math.cos(ang + 0.5), p1[1] - L * math.sin(ang + 0.5))
        pygame.draw.polygon(self.tela, cor, [p1, p2, p3])

    def _desenhar_peso(self, a: Tuple[int,int], b: Tuple[int,int], w: float, cor):
        # Posições dos planetas a e b
        ax, ay = a
        bx, by = b

        # 1. Achar o ponto médio da linha, como antes
        mx = (ax + bx) / 2
        my = (ay + by) / 2

        # 2. Calcular o vetor da linha (direção e magnitude)
        dx = bx - ax
        dy = by - ay

        # 3. Achar um vetor perpendicular (girado 90 graus)
        # Se o vetor da linha é (dx, dy), o perpendicular é (-dy, dx)
        nx = -dy
        ny = dx

        # 4. Normalizar o vetor perpendicular (transformá-lo para ter "tamanho 1")
        # Isso nos dá apenas a direção, sem a distância
        magnitude = math.hypot(nx, ny)
        if magnitude == 0:  # Evita divisão por zero
            unx, uny = 0, -1 # Se não houver distância, apenas move para cima
        else:
            unx = nx / magnitude
            uny = ny / magnitude

        # 5. Calcular a nova posição com um deslocamento "para fora"
        offset = 15  # Distância de 15 pixels "acima" da linha
        
        text_x = mx + offset * unx
        text_y = my + offset * uny

        # 6. Desenhar o texto na nova posição calculada
        self.ui._draw_text(f"{w:.0f}", text_x, text_y, color=cor, font=self.fonte_peso_aresta, center_x=True, center_y=True)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Jogo().run()