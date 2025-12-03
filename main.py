import pygame
import sys
import math
from typing import List, Optional, Generator, Tuple, Set

from config import *
from ui import UIManager
from graph_system import MapaGalactico
import levels

from bfs import bfs_generator
from dijkstra import dijkstra_generator
from dfs import detecting_ciclo_generator
from bellman_ford import bellman_ford_generator
from mst import mst_prim_generator

class Jogo:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Helldivers: Grafos da Super-Terra v3.5 - High Visibility")
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        self.clock = pygame.time.Clock()
        
        self.fonte_titulo = pygame.font.SysFont("consolas", 22, bold=True)
        self.fonte_normal = pygame.font.SysFont("consolas", 12)
        self.fonte_pequena = pygame.font.SysFont("consolas", 11)
        self.fonte_peso_aresta = pygame.font.SysFont("consolas", 14, bold=True)
        
        self.ui = UIManager(self.tela, self.fonte_titulo, self.fonte_normal, self.fonte_pequena)
        
        try:
            bg_orig = pygame.image.load("assets/background.png").convert()
            self.background = pygame.transform.scale(bg_orig, (LARGURA, ALTURA))
        except (pygame.error, FileNotFoundError):
            self.background = None

        self.game_state = "INTRO"
        self.fase = 1
        self.mapa: MapaGalactico = levels.construir_mapa_fase1()
        self.msgs: List[str] = []
        self.anim: Optional[Generator] = None
        
        self.selecao: Optional[str] = None
        self.selecao2: Optional[str] = None
        
        self.caminho_atual: List[str] = []
        self.ciclo_atual: List[str] = []
        self.mst_atual: List[Tuple[str, str]] = [] 
        
        self.highlight_node: Optional[str] = None
        self.highlight_edge: Optional[Tuple[str, str]] = None
        self.highlight_neighbors: List[str] = []
        self.highlight_color: Tuple[int, int, int] = CYAN_NEON

        self.mostrar_tutorial = True
        self.componentes_visuais: Optional[List[Set[str]]] = None
        self.componentes_timer = 0
        
        self.modo_manual = False
        self.solicitar_proximo_passo = False
        self.timer_animacao = 0 
        self.DELAY_MS = 600
        
        self.intro_text = [
            "> Atualizando Interface Tática...",
            "> Otimização de leitura de dados logísticos.",
            "> Pesos de arestas destacados para melhor visualização.",
            "> Prepare-se para a missão."
        ]
        self.typed_chars = 0
        self.last_char_time = 0

    def set_fase(self, f: int):
        self.fase = f
        self.anim = None
        self._reset_visuals()
        self.selecao = None; self.selecao2 = None; self.componentes_visuais = None
        
        map_funcs = {
            1: levels.construir_mapa_fase1,
            2: levels.construir_mapa_fase2,
            3: levels.construir_mapa_fase3,
            4: levels.construir_mapa_fase4,
            5: levels.construir_mapa_fase5
        }
        self.mapa = map_funcs[f]()
        self._say(f"Fase {f} Pronta. [T] Ajuda | [P] Manual")
        self.mostrar_tutorial = True

    def _reset_visuals(self):
        self.caminho_atual = []
        self.ciclo_atual = []
        self.mst_atual = []
        self.highlight_node = None
        self.highlight_edge = None
        self.highlight_neighbors = []

    def _say(self, texto: str):
        self.msgs.append(texto)
        if len(self.msgs) > 5: self.msgs.pop(0)

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit(0)
            
            if self.game_state == "INTRO":
                if ev.type == pygame.KEYDOWN:
                    self.game_state = "JOGO"
                    self._say("Selecione uma fase [1-5].")
                continue

            if self.mostrar_tutorial:
                if ev.type == pygame.KEYDOWN: self.mostrar_tutorial = False
                continue

            if ev.type == pygame.KEYDOWN:
                key_map = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4, pygame.K_5: 5}
                if ev.key in key_map: self.set_fase(key_map[ev.key])
                elif ev.key == pygame.K_t: self.mostrar_tutorial = True
                elif ev.key == pygame.K_r: self.evento_remover_rota()
                elif ev.key == pygame.K_p: 
                    self.modo_manual = not self.modo_manual
                    self._say(f"Modo Manual: {'ATIVADO' if self.modo_manual else 'DESATIVADO'}")
                elif ev.key == pygame.K_SPACE:
                    if self.modo_manual and self.anim: self.solicitar_proximo_passo = True

               
                elif ev.key == pygame.K_b: self.iniciar_bfs()
                elif ev.key == pygame.K_d: self.iniciar_dijkstra()
                elif ev.key == pygame.K_c: self.iniciar_detecção_ciclo()
                elif ev.key == pygame.K_f: self.iniciar_bellman_ford()
                elif ev.key == pygame.K_m: self.iniciar_mst()

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                
                if self.anim and self.modo_manual and self.ui.rect_btn_proximo.collidepoint(ev.pos):
                    self.solicitar_proximo_passo = True
                    return
                
                if self.ui.rect_btn_menos.collidepoint(ev.pos):
                    self.DELAY_MS = max(50, self.DELAY_MS - 50)
                
                if self.ui.rect_btn_mais.collidepoint(ev.pos):
                    self.DELAY_MS = min(2000, self.DELAY_MS + 50)

                clicado = self._planeta_em(ev.pos)
                if clicado:
                    if not self.selecao or (self.selecao and self.selecao2):
                        self.selecao = clicado; self.selecao2 = None
                        self._say(f"Origem: {clicado}")
                    else:
                        self.selecao2 = clicado
                        self._say(f"Destino: {clicado}")

    def evento_remover_rota(self):
        comps_antes = len(self.mapa.encontrar_componentes_conexos())
        removida = self.mapa.remover_rota_aleatoria()
        if not removida: self._say("Nenhuma rota vulnerável."); return
        self._say(f"Rota {removida[0]} <-> {removida[1]} destruída!")
        comps_depois = self.mapa.encontrar_componentes_conexos()
        if len(comps_depois) > comps_antes:
            self._say(f"ALERTA: Fragmentação! {len(comps_depois)} setores isolados.")
            self.componentes_visuais = comps_depois
            self.componentes_timer = FPS * 5

    def iniciar_bfs(self):
        if self.fase != 1: return
        if self.selecao: self._reset_visuals(); self.anim = bfs_generator(self.mapa, self.selecao)
        else: self._say("Selecione Origem.")

    def iniciar_dijkstra(self):
        if self.fase != 2: return
        if self.selecao and self.selecao2: self._reset_visuals(); self.anim = dijkstra_generator(self.mapa, self.selecao, self.selecao2)
        else: self._say("Selecione Origem e Destino.")

    def iniciar_detecção_ciclo(self):
        if self.fase != 3: return
        self._reset_visuals(); self.anim = detecting_ciclo_generator(self.mapa)

    def iniciar_bellman_ford(self):
        if self.fase != 4: return
        if self.selecao and self.selecao2: self._reset_visuals(); self.anim = bellman_ford_generator(self.mapa, self.selecao, self.selecao2)
        else: self._say("Selecione Origem e Destino.")

    def iniciar_mst(self):
        if self.fase != 5: return
        if self.selecao: self._reset_visuals(); self.anim = mst_prim_generator(self.mapa, self.selecao)
        else: self._say("Selecione Origem.")

    def _planeta_em(self, pos) -> Optional[str]:
        for nome, p in self.mapa.planetas.items():
            if math.hypot(p.pos[0] - pos[0], p.pos[1] - pos[1]) <= RAIO_PLANETA: return nome
        return None

    def update(self):
        if self.game_state == "INTRO":
            if pygame.time.get_ticks() - self.last_char_time > 20:
                self.typed_chars += 1; self.last_char_time = pygame.time.get_ticks()
            return

        avancar = False
        agora = pygame.time.get_ticks()

        if self.anim:
            if not self.modo_manual:
                if agora - self.timer_animacao > self.DELAY_MS:
                    avancar = True
                    self.timer_animacao = agora
            else:
                if self.solicitar_proximo_passo:
                    avancar = True
                    self.solicitar_proximo_passo = False
        
        if avancar and self.anim:
            try:
                passo = next(self.anim)
                self._processa_passo(passo)
            except StopIteration:
                self.anim = None
                self.highlight_node = None
                self.highlight_edge = None
                self.highlight_neighbors = []
        
        if self.componentes_timer > 0:
            self.componentes_timer -= 1
            if self.componentes_timer == 0: self.componentes_visuais = None

    def _processa_passo(self, passo: dict):
        t = passo.get("tipo")
        
        self.highlight_node = None
        self.highlight_edge = None
        self.highlight_neighbors = []

        if t == "msg": self._say(passo["texto"])
        
        elif t == "bfs_visit":
            self.highlight_node = passo["u"]
            self.highlight_color = CYAN_NEON
        elif t == "bfs_enfileira":
            self.highlight_node = passo["de"]
            self.highlight_edge = (passo["de"], passo["para"])
            self.highlight_neighbors = [passo["para"]]
            self.highlight_color = LARANJA_VIVO

        elif t == "djk_visita":
            self.highlight_node = passo["u"]
            self.highlight_color = CYAN_NEON
        elif t == "djk_relax":
            self.highlight_edge = (passo["de"], passo["para"])
            self.highlight_neighbors = [passo["para"]]
            self.highlight_color = MAGENTA_NEON
        elif t == "djk_fim":
            self.caminho_atual = passo.get("caminho", [])
            custo = passo.get("custo", 0)
            if self.caminho_atual: self._say(f"Custo Final: {custo:.1f}")

        elif t == "dfs_enter":
            self.highlight_node = passo["u"]
            self.highlight_color = CYAN_NEON
        elif t == "dfs_tree":
            self.highlight_edge = (passo["de"], passo["para"])
            self.highlight_color = LARANJA_VIVO
        elif t == "dfs_backedge":
            self.highlight_edge = (passo["de"], passo["para"])
            self.highlight_color = VERMELHO
        elif t == "ciclo_encontrado":
            self.ciclo_atual = passo.get("ciclo", [])

        elif t == "bf_relax":
            self.highlight_edge = (passo["de"], passo["para"])
            self.highlight_color = MAGENTA_NEON

        elif t == "mst_check":
            self.highlight_edge = (passo["de"], passo["para"])
            self.highlight_color = CINZA_CLARO
        elif t == "mst_add":
            self.mst_atual = passo.get("mst", [])
            self.highlight_edge = (passo["de"], passo["para"])
            self.highlight_color = VERDE_NEON
        elif t == "mst_fim":
            self.mst_atual = passo.get("mst", [])
            self._say(f"MST Custo: {passo.get('custo_total'):.1f}")

    def draw(self):
        if self.background: self.tela.blit(self.background, (0, 0))
        else: self.tela.fill(PRETO)
        
        if self.game_state == "INTRO":
            self.ui.draw_intro(self.typed_chars, self.intro_text)
            pygame.display.flip(); return

        for e in self.mapa.arestas():
            u_pos = self.mapa.planetas[e.u].pos
            v_pos = self.mapa.planetas[e.v].pos
            cor = CINZA_CLARO; width = 3
            
            if self.mst_atual:
                if (e.u, e.v) in self.mst_atual or (e.v, e.u) in self.mst_atual:
                    cor = (255, 180, 0); width = 6
            
            if not e.ativa: cor = (50, 50, 50); width = 1
            
            pygame.draw.line(self.tela, cor, u_pos, v_pos, width)
            if e.dirigida and e.ativa: self._desenhar_seta(u_pos, v_pos, cor)
            
            if (self.fase in [2, 4, 5]) and e.ativa: 
                self._desenhar_peso(u_pos, v_pos, e.peso, cor)

        if len(self.caminho_atual) >= 2:
            pts = [self.mapa.planetas[p].pos for p in self.caminho_atual]
            pygame.draw.lines(self.tela, VERDE, False, pts, 6)
        if len(self.ciclo_atual) >= 1:
            pts = [self.mapa.planetas[p].pos for p in self.ciclo_atual] + [self.mapa.planetas[self.ciclo_atual[0]].pos]
            pygame.draw.lines(self.tela, VERMELHO, False, pts, 6)

        if self.highlight_edge:
            u, v = self.highlight_edge
            if u in self.mapa.planetas and v in self.mapa.planetas:
                pygame.draw.line(self.tela, self.highlight_color, self.mapa.planetas[u].pos, self.mapa.planetas[v].pos, 8)

        for nome, p in self.mapa.planetas.items():
            cor_base = CORES_FACCAO.get(p.faccao_inimiga, AZUL)
            if self.componentes_visuais and self.componentes_timer > 0:
                for i, comp in enumerate(self.componentes_visuais):
                    if nome in comp and (self.componentes_timer // 10) % 2 == 0:
                        cor_base = [VERDE, VERMELHO, AZUL, AMARELO][i % 4]; break

            pygame.draw.circle(self.tela, cor_base, p.pos, RAIO_PLANETA)
            pygame.draw.circle(self.tela, PRETO, p.pos, RAIO_PLANETA, 2)
            
            if nome == self.selecao: pygame.draw.circle(self.tela, BRANCO, p.pos, RAIO_PLANETA + 4, 2)
            if nome == self.selecao2: pygame.draw.circle(self.tela, VERDE, p.pos, RAIO_PLANETA + 4, 2)
            
            if nome == self.highlight_node:
                pygame.draw.circle(self.tela, self.highlight_color, p.pos, RAIO_PLANETA + 8, 4)
            if nome in self.highlight_neighbors:
                pygame.draw.circle(self.tela, LARANJA_VIVO, p.pos, RAIO_PLANETA + 6, 2)

            self.ui._draw_text(nome, p.pos[0], p.pos[1] - 25, font=self.ui.fonte_pequena, center_x=True)

        self.ui.draw_hud(self.fase, self.msgs, self.modo_manual)
        self.ui.draw_speed_controls(self.DELAY_MS)
        self.ui.draw_playback_controls(bool(self.anim), self.modo_manual)
        if self.mostrar_tutorial: self.ui.draw_tutorial(self.fase)
        pygame.display.flip()

    def _desenhar_seta(self, a, b, cor):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        p1 = (b[0] - 22 * math.cos(ang), b[1] - 22 * math.sin(ang))
        p2 = (p1[0] - 10 * math.cos(ang - 0.5), p1[1] - 10 * math.sin(ang - 0.5))
        p3 = (p1[0] - 10 * math.cos(ang + 0.5), p1[1] - 10 * math.sin(ang + 0.5))
        pygame.draw.polygon(self.tela, cor, [p1, p2, p3])

    def _desenhar_peso(self, a, b, w, cor):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        
        texto_str = f"{int(w)}"
        surf = self.fonte_peso_aresta.render(texto_str, True, BRANCO)
        rect = surf.get_rect(center=(mx, my))
        
        bg_rect = rect.inflate(10, 6)
        
        pygame.draw.rect(self.tela, (20, 20, 30), bg_rect, border_radius=4)
        
        pygame.draw.rect(self.tela, cor, bg_rect, 1, border_radius=4)
        
        self.tela.blit(surf, rect)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Jogo().run()