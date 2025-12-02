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
        pygame.display.set_caption("Helldivers: Grafos da Super-Terra v3.0 - 16 Planetas")
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
        
        self.mostrar_tutorial = True
        self.componentes_visuais: Optional[List[Set[str]]] = None
        self.componentes_timer = 0
        
        self.intro_text = [
            "> Conexão Segura Estabelecida.",
            "> Atualização de Firmware v3.0: Módulos MST e Bellman-Ford instalados.",
            "> Expansão de Mapa: 16 Setores detectados.",
            "> Prepare-se para espalhar a Democracia Gerenciada."
        ]
        self.typed_chars = 0
        self.last_char_time = 0

    def set_fase(self, f: int):
        self.fase = f
        self.anim = None; self.caminho_atual = []; self.ciclo_atual = []; self.mst_atual = []
        self.selecao = None; self.selecao2 = None; self.componentes_visuais = None
        
        map_funcs = {
            1: levels.construir_mapa_fase1,
            2: levels.construir_mapa_fase2,
            3: levels.construir_mapa_fase3,
            4: levels.construir_mapa_fase4,
            5: levels.construir_mapa_fase5
        }
        self.mapa = map_funcs[f]()
        
        fase_nomes = {
            1: "Autômatos (BFS)", 2: "Terminídeos (Dijkstra)", 
            3: "Iluminados (Ciclos)", 4: "Zona Instável (Bellman-Ford)",
            5: "Abastecimento (MST)"
        }
        self._say(f"Fase {f} Iniciada: {fase_nomes[f]}. [T] para ajuda.")
        self.mostrar_tutorial = True

    def _say(self, texto: str):
        self.msgs.append(texto)
        if len(self.msgs) > 5: self.msgs.pop(0)
        print(f"MSG: {texto}")

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit(0)
            
            if self.game_state == "INTRO":
                if ev.type == pygame.KEYDOWN:
                    self.game_state = "JOGO"
                    self._say("Selecione uma fase [1-5] para começar.")
                continue

            if self.mostrar_tutorial:
                if ev.type == pygame.KEYDOWN: self.mostrar_tutorial = False
                continue

            if ev.type == pygame.KEYDOWN:
                key_map = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4, pygame.K_5: 5}
                if ev.key in key_map: self.set_fase(key_map[ev.key])
                elif ev.key == pygame.K_t: self.mostrar_tutorial = True
                elif ev.key == pygame.K_r: self.evento_remover_rota()
                
                elif ev.key == pygame.K_b: self.iniciar_bfs()
                elif ev.key == pygame.K_d: self.iniciar_dijkstra()
                elif ev.key == pygame.K_c: self.iniciar_detecção_ciclo()
                elif ev.key == pygame.K_f: self.iniciar_bellman_ford()
                elif ev.key == pygame.K_m: self.iniciar_mst()

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                clicado = self._planeta_em(ev.pos)
                if clicado:
                    if not self.selecao or (self.selecao and self.selecao2):
                        self.selecao = clicado
                        self.selecao2 = None
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
            self._say(f"ALERTA: Setor fragmentado em {len(comps_depois)} regiões!")
            self.componentes_visuais = comps_depois
            self.componentes_timer = FPS * 5

    def iniciar_bfs(self):
        if self.fase != 1: self._say("BFS é para Fase 1."); return
        if self.selecao: self.anim = bfs_generator(self.mapa, self.selecao)
        else: self._say("Selecione Origem.")

    def iniciar_dijkstra(self):
        if self.fase != 2: self._say("Dijkstra é para Fase 2."); return
        if self.selecao and self.selecao2: self.anim = dijkstra_generator(self.mapa, self.selecao, self.selecao2)
        else: self._say("Selecione Origem e Destino.")

    def iniciar_detecção_ciclo(self):
        if self.fase != 3: self._say("Ciclos apenas na Fase 3."); return
        self.anim = detecting_ciclo_generator(self.mapa)

    def iniciar_bellman_ford(self):
        if self.fase != 4: self._say("Bellman-Ford é para Fase 4."); return
        if self.selecao and self.selecao2: self.anim = bellman_ford_generator(self.mapa, self.selecao, self.selecao2)
        else: self._say("Selecione Origem e Destino.")

    def iniciar_mst(self):
        if self.fase != 5: self._say("MST é para Fase 5."); return
        if self.selecao: self.anim = mst_prim_generator(self.mapa, self.selecao)
        else: self._say("Selecione um ponto inicial para a Rede.")

    def _planeta_em(self, pos) -> Optional[str]:
        for nome, p in self.mapa.planetas.items():
            if math.hypot(p.pos[0] - pos[0], p.pos[1] - pos[1]) <= RAIO_PLANETA: return nome
        return None

    def update(self):
        if self.game_state == "INTRO":
            if pygame.time.get_ticks() - self.last_char_time > 20:
                self.typed_chars += 1; self.last_char_time = pygame.time.get_ticks()
            return

        if self.anim:
            try:
                passo = next(self.anim)
                t = passo.get("tipo")
                if t == "msg": self._say(passo["texto"])
                elif t == "djk_fim": 
                    self.caminho_atual = passo.get("caminho", [])
                    if self.caminho_atual: self._say(f"Rota Final: {len(self.caminho_atual)} passos. Custo: {passo.get('custo'):.1f}")
                elif t == "ciclo_encontrado": self.ciclo_atual = passo.get("ciclo", [])
                elif t == "mst_add" or t == "mst_fim": 
                    self.mst_atual = passo.get("mst", [])
                    if t == "mst_fim": self._say(f"MST Concluída. Custo Total: {passo.get('custo_total'):.1f}")
            except StopIteration:
                self.anim = None
        
        if self.componentes_timer > 0:
            self.componentes_timer -= 1
            if self.componentes_timer == 0: self.componentes_visuais = None

    def draw(self):
        if self.background: self.tela.blit(self.background, (0, 0))
        else: self.tela.fill(PRETO)
        
        if self.game_state == "INTRO":
            self.ui.draw_intro(self.typed_chars, self.intro_text)
            pygame.display.flip(); return

        for e in self.mapa.arestas():
            u_pos = self.mapa.planetas[e.u].pos
            v_pos = self.mapa.planetas[e.v].pos
            
            cor = CINZA_CLARO
            width = 3
            
            na_mst = False
            if self.mst_atual:
                if (e.u, e.v) in self.mst_atual or (e.v, e.u) in self.mst_atual:
                    cor = AMBER if "AMBER" in globals() else (255, 180, 0)
                    width = 6
                    na_mst = True
            
            if not e.ativa: cor = (50, 50, 50); width = 1

            pygame.draw.line(self.tela, cor, u_pos, v_pos, width)
            if e.dirigida and e.ativa: self._desenhar_seta(u_pos, v_pos, cor)
            if (self.fase in [2, 4, 5]) and e.ativa: self._desenhar_peso(u_pos, v_pos, e.peso, cor, highlight=na_mst)

        if len(self.caminho_atual) >= 2:
            pts = [self.mapa.planetas[p].pos for p in self.caminho_atual]
            pygame.draw.lines(self.tela, VERDE, False, pts, 6)
       
        if len(self.ciclo_atual) >= 1:
            pts = [self.mapa.planetas[p].pos for p in self.ciclo_atual] + [self.mapa.planetas[self.ciclo_atual[0]].pos]
            pygame.draw.lines(self.tela, VERMELHO, False, pts, 6)

        for nome, p in self.mapa.planetas.items():
            cor_base = CORES_FACCAO.get(p.faccao_inimiga, AZUL)
            if self.componentes_visuais and self.componentes_timer > 0:
                for i, comp in enumerate(self.componentes_visuais):
                    if nome in comp and (self.componentes_timer // 10) % 2 == 0:
                        cor_base = [VERDE, VERMELHO, AZUL, AMARELO][i % 4]
                        break

            pygame.draw.circle(self.tela, cor_base, p.pos, RAIO_PLANETA)
            pygame.draw.circle(self.tela, PRETO, p.pos, RAIO_PLANETA, 2)
        
            if nome == self.selecao: 
                pygame.draw.circle(self.tela, BRANCO, p.pos, RAIO_PLANETA + 4, 2)
            if nome == self.selecao2: 
                pygame.draw.circle(self.tela, VERDE, p.pos, RAIO_PLANETA + 4, 2)
                
            self.ui._draw_text(nome, p.pos[0], p.pos[1] - 25, font=self.ui.fonte_pequena, center_x=True)

        self.ui.draw_hud(self.fase, self.msgs)
        if self.mostrar_tutorial: self.ui.draw_tutorial(self.fase)
        pygame.display.flip()

    def _desenhar_seta(self, a, b, cor):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        p1 = (b[0] - 22 * math.cos(ang), b[1] - 22 * math.sin(ang))
        p2 = (p1[0] - 10 * math.cos(ang - 0.5), p1[1] - 10 * math.sin(ang - 0.5))
        p3 = (p1[0] - 10 * math.cos(ang + 0.5), p1[1] - 10 * math.sin(ang + 0.5))
        pygame.draw.polygon(self.tela, cor, [p1, p2, p3])

    def _desenhar_peso(self, a, b, w, cor, highlight=False):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        cor_txt = AMARELO if highlight else cor
        if highlight: 
            pygame.draw.circle(self.tela, PRETO, (int(mx), int(my)), 10) 
        self.ui._draw_text(f"{int(w)}", int(mx), int(my), color=cor_txt, font=self.fonte_peso_aresta, center_x=True, center_y=True)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Jogo().run()