import pygame
import sys
import math
from typing import List, Optional, Generator, Tuple, Set

from config import *
from ui import UIManager
from graph_system import MapaGalactico
import levels

class Jogo:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Helldivers: Grafos da Super-Terra v2.0")
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        self.clock = pygame.time.Clock()
        
        self.fonte_titulo = pygame.font.SysFont("consolas", 22, bold=True)
        self.fonte_normal = pygame.font.SysFont("consolas", 12)
        self.fonte_pequena = pygame.font.SysFont("consolas", 11)
        self.fonte_peso_aresta = pygame.font.SysFont("consolas", 20, bold=True)
        
        self.ui = UIManager(self.tela, self.fonte_titulo, self.fonte_normal, self.fonte_pequena)
        
        try:
            bg_orig = pygame.image.load("assets/background.png").convert()
            self.background = pygame.transform.scale(bg_orig, (LARGURA, ALTURA))
        except (pygame.error, FileNotFoundError):
            self.background = None
            print("AVISO: 'assets/background.png' não encontrado. Usando fundo sólido.")

        self.game_state = "INTRO"
        self.fase = 1
        self.mapa: MapaGalactico = levels.construir_mapa_fase1()
        self.msgs: List[str] = []
        self.anim: Optional[Generator] = None
        self.selecao: Optional[str] = None
        self.selecao2: Optional[str] = None
        self.caminho_atual: List[str] = []
        self.ciclo_atual: List[str] = []
        self.mostrar_tutorial = True
        
        self.componentes_visuais: Optional[List[Set[str]]] = None
        self.componentes_timer = 0

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
        
        if f == 1: self.mapa = levels.construir_mapa_fase1()
        elif f == 2: self.mapa = levels.construir_mapa_fase2()
        else: self.mapa = levels.construir_mapa_fase3()
            
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
        lista_componentes_depois = self.mapa.encontrar_componentes_conexos()
        num_componentes_depois = len(lista_componentes_depois)
        
        if num_componentes_depois > componentes_antes:
            self._say(f"GRAVE: A perda da rota dividiu o setor! Temos {num_componentes_depois} zonas isoladas.")
            self.componentes_visuais = lista_componentes_depois
            self.componentes_timer = FPS * 5
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
        self.anim = self.mapa.detecting_ciclo_generator()

    def _planeta_em(self, pos) -> Optional[str]:
        for nome, p in self.mapa.planetas.items():
            if math.hypot(p.pos[0] - pos[0], p.pos[1] - pos[1]) <= RAIO_PLANETA:
                return nome
        return None

    def update(self):
        if self.game_state == "INTRO":
            if pygame.time.get_ticks() - self.last_char_time > 30:
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
        if self.background: self.tela.blit(self.background, (0, 0))
        else: self.tela.fill(PRETO)
        
        if self.game_state == "INTRO":
            self.ui.draw_intro(self.typed_chars, self.intro_text)
            pygame.display.flip()
            return

        for e in self.mapa.arestas():
            u_pos = self.mapa.planetas[e.u].pos
            v_pos = self.mapa.planetas[e.v].pos
            cor = CINZA_CLARO if e.ativa else (70, 70, 80)
            pygame.draw.line(self.tela, cor, u_pos, v_pos, 3)
            if e.dirigida and e.ativa: self._desenhar_seta(u_pos, v_pos, cor)
            if self.fase == 2 and e.ativa: self._desenhar_peso(u_pos, v_pos, e.peso, cor)

        if len(self.caminho_atual) >= 2:
            pts = [self.mapa.planetas[p].pos for p in self.caminho_atual]
            pygame.draw.lines(self.tela, VERDE, False, pts, 6)
        if len(self.ciclo_atual) >= 1:
            pts = [self.mapa.planetas[p].pos for p in self.ciclo_atual] + [self.mapa.planetas[self.ciclo_atual[0]].pos]
            pygame.draw.lines(self.tela, VERMELHO, False, pts, 6)

        for nome, p in self.mapa.planetas.items():
            cor_base = CORES_FACCAO.get(p.faccao_inimiga, AZUL)
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
        ax, ay = a; bx, by = b
        mx, my = (ax + bx) / 2, (ay + by) / 2
        dx, dy = bx - ax, by - ay
        nx, ny = -dy, dx
        magnitude = math.hypot(nx, ny)
        if magnitude == 0: unx, uny = 0, -1
        else: unx, uny = nx / magnitude, ny / magnitude
        offset = 15
        text_x, text_y = mx + offset * unx, my + offset * uny
        self.ui._draw_text(f"{w:.0f}", text_x, text_y, color=cor, font=self.fonte_peso_aresta, center_x=True, center_y=True)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Jogo().run()