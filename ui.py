import pygame
from config import *

class UIManager:
    def __init__(self, tela, fonte_titulo, fonte_normal, fonte_pequena):
        self.tela = tela
        self.fonte_titulo = fonte_titulo
        self.fonte_normal = fonte_normal
        self.fonte_pequena = fonte_pequena
        
        self.rect_btn_proximo = pygame.Rect(LARGURA - 180, ALTURA - 60, 160, 40)
        
        self.rect_btn_menos = pygame.Rect(LARGURA - 150, 45, 30, 30)
        self.rect_btn_mais = pygame.Rect(LARGURA - 40, 45, 30, 30)
        
        try:
            self.logo = pygame.image.load("assets/logo.png").convert_alpha()
            self.logo = pygame.transform.scale(self.logo, (300, int(300 * self.logo.get_height() / self.logo.get_width())))
        except (pygame.error, FileNotFoundError):
            self.logo = None
        
        self.tutoriais = {
            1: [
                "FASE 1: SETOR AUTÔMATO (BFS)", "", 
                "MISSÃO: Expandir fronteiras.",
                "O algoritmo BFS (Busca em Largura) explora o mapa em camadas,",
                "garantindo que visitamos os planetas mais próximos primeiro.",
                "", "CONTROLES: [1] Selecionar | [B] Executar BFS | [R] Destruir Rota"
            ],
            2: [
                "FASE 2: SETOR TERMINÍDEO (Dijkstra)", "", 
                "MISSÃO: Logística de Precisão.",
                "O algoritmo de Dijkstra encontra o caminho de MENOR CUSTO.",
                "Crucial quando o combustível (peso da aresta) é limitado.",
                "", "CONTROLES: [2] Selecionar | [D] Executar Dijkstra | Clique Origem+Destino"
            ],
            3: [
                "FASE 3: SETOR ILUMINADO (DFS/Ciclos)", "", 
                "MISSÃO: Detecção de Anomalias.",
                "Grafos direcionados podem conter 'loops' infinitos.",
                "A Busca em Profundidade (DFS) ajuda a detectar esses ciclos.",
                "", "CONTROLES: [3] Selecionar | [C] Detectar Ciclos"
            ],
            4: [
                "FASE 4: ZONA INSTÁVEL (Bellman-Ford)", "",
                "MISSÃO: Navegação Robusta.",
                "Bellman-Ford é mais lento que Dijkstra, mas mais robusto.",
                "Ele relaxa todas as rotas repetidamente para garantir a otimização,",
                "mesmo em sistemas complexos.",
                "", "CONTROLES: [4] Selecionar | [F] Executar Bellman-Ford | Clique Origem+Destino"
            ],
            5: [
                "FASE 5: REDE DE ABASTECIMENTO (MST - Prim)", "",
                "MISSÃO: Conexão Total Econômica.",
                "Precisamos conectar TODOS os planetas gastando o mínimo possível.",
                "A Árvore Geradora Mínima (MST) cria essa espinha dorsal.",
                "", "CONTROLES: [5] Selecionar | [M] Gerar MST | Clique Origem"
            ]
        }

    def _draw_text(self, txt: str, x: int, y: int, color=BRANCO, font=None, center_x=False, center_y=False):
        if font is None: font = self.fonte_normal
        surf = font.render(txt, True, color)
        rect = surf.get_rect()
        if center_x and center_y: rect.center = (x, y)
        elif center_x: rect.centerx, rect.top = x, y
        elif center_y: rect.left, rect.centery = x, y
        else: rect.topleft = (x, y)
        self.tela.blit(surf, rect)

    def draw_intro(self, typed_chars, intro_text):
        self.tela.fill(PRETO)
        if self.logo: self.tela.blit(self.logo, self.logo.get_rect(center=(LARGURA / 2, ALTURA / 3)))
        chars_to_render = typed_chars
        for i, line in enumerate(intro_text):
            if chars_to_render <= 0: break
            render_text = line[:int(chars_to_render)]
            self._draw_text(render_text, LARGURA / 2, ALTURA * 0.6 + i * 30, center_x=True)
            chars_to_render -= len(line)
        if typed_chars >= sum(len(s) for s in intro_text):
             self._draw_text("Pressione qualquer tecla para iniciar.", x=LARGURA/2, y=ALTURA - 50, color=AMARELO, center_x=True)

    def draw_hud(self, fase, msgs, modo_manual):
        panel_surf = pygame.Surface((LARGURA, 80)); panel_surf.set_alpha(COR_PAINEL[3]); panel_surf.fill(COR_PAINEL[:-1])
        self.tela.blit(panel_surf, (0,0))
        pygame.draw.line(self.tela, AMARELO, (0, 80), (LARGURA, 80), 2)

        fase_nomes = {
            1: "Fase 1: Autômatos (BFS)", 2: "Fase 2: Terminídeos (Dijkstra)", 
            3: "Fase 3: Iluminados (Ciclos)", 4: "Fase 4: Instável (Bellman-Ford)",
            5: "Fase 5: Abastecimento (MST)"
        }
        
        self._draw_text(f"OPERAÇÃO GRAFOS | {fase_nomes.get(fase, 'Desconhecido')}", x=20, y=15, font=self.fonte_titulo)
        
        status_txt = "MODO: MANUAL" if modo_manual else "MODO: AUTO"
        cor_status = AMARELO if modo_manual else VERDE
        largura_txt = self.fonte_titulo.size(status_txt)[0]
        self._draw_text(status_txt, x=LARGURA - largura_txt - 20, y=10, color=cor_status, font=self.fonte_titulo)

        controles = "[1-5] Mudar Fase | [T] Tutorial | [R] Evento | [P] Auto/Manual"
        self._draw_text(controles, x=20, y=50)
        
        if msgs:
            last_msg = msgs[-1]
            last_msg_surf = self.fonte_normal.render(f"> {last_msg}", True, BRANCO)
            self.tela.blit(last_msg_surf, (LARGURA/2, 50)) 

    def draw_speed_controls(self, delay_ms):
        """Desenha os controles de velocidade no HUD."""
        mouse_pos = pygame.mouse.get_pos()
        
        cor_menos = (80, 80, 90) if self.rect_btn_menos.collidepoint(mouse_pos) else (60, 60, 70)
        pygame.draw.rect(self.tela, cor_menos, self.rect_btn_menos, border_radius=5)
        pygame.draw.rect(self.tela, BRANCO, self.rect_btn_menos, 1, border_radius=5)
        self._draw_text("-", self.rect_btn_menos.centerx, self.rect_btn_menos.centery, font=self.fonte_titulo, center_x=True, center_y=True)

        cor_mais = (80, 80, 90) if self.rect_btn_mais.collidepoint(mouse_pos) else (60, 60, 70)
        pygame.draw.rect(self.tela, cor_mais, self.rect_btn_mais, border_radius=5)
        pygame.draw.rect(self.tela, BRANCO, self.rect_btn_mais, 1, border_radius=5)
        self._draw_text("+", self.rect_btn_mais.centerx, self.rect_btn_mais.centery, font=self.fonte_titulo, center_x=True, center_y=True)

        texto_speed = f"{delay_ms}ms"
        centro_x = (self.rect_btn_menos.right + self.rect_btn_mais.left) / 2
        self._draw_text(texto_speed, centro_x, 52, font=self.fonte_normal, center_x=True, center_y=True)
        self._draw_text("DELAY", centro_x, 40, font=self.fonte_pequena, color=CINZA_CLARO, center_x=True, center_y=True)

    def draw_playback_controls(self, anim_ativa: bool, modo_manual: bool):
        if anim_ativa and modo_manual:
            mouse_pos = pygame.mouse.get_pos()
            cor_btn = (80, 80, 90) if self.rect_btn_proximo.collidepoint(mouse_pos) else (60, 60, 70)
            
            pygame.draw.rect(self.tela, cor_btn, self.rect_btn_proximo, border_radius=5)
            pygame.draw.rect(self.tela, BRANCO, self.rect_btn_proximo, 2, border_radius=5)
            
            self._draw_text("PRÓXIMO [Espaço]", self.rect_btn_proximo.centerx, self.rect_btn_proximo.centery, font=self.fonte_titulo, center_x=True, center_y=True)

    def draw_tutorial(self, fase):
        panel_w, panel_h = 700, 450
        panel_x, panel_y = (LARGURA - panel_w) / 2, (ALTURA - panel_h) / 2
        panel_surf = pygame.Surface((panel_w, panel_h)); panel_surf.set_alpha(COR_PAINEL[3]); panel_surf.fill(COR_PAINEL[:-1])
        self.tela.blit(panel_surf, (panel_x, panel_y))
        pygame.draw.rect(self.tela, AMARELO, (panel_x, panel_y, panel_w, panel_h), 3)

        tutorial_text = self.tutoriais.get(fase, ["Dados corrompidos."])
        for i, line in enumerate(tutorial_text):
            font = self.fonte_titulo if i == 0 else self.fonte_normal
            color = AMARELO if i == 0 or "CONTROLES:" in line else BRANCO
            self._draw_text(line, x=LARGURA / 2, y=panel_y + 40 + i * 25, color=color, font=font, center_x=True)
        self._draw_text("Pressione qualquer tecla para fechar.", x=LARGURA / 2, y=panel_y + panel_h - 30, color=CINZA_CLARO, center_x=True)