import pygame
from config import *

class UIManager:
    def __init__(self, tela, fonte_titulo, fonte_normal, fonte_pequena):
        self.tela = tela
        self.fonte_titulo = fonte_titulo
        self.fonte_normal = fonte_normal
        self.fonte_pequena = fonte_pequena
        
        try:
            self.logo = pygame.image.load("assets/logo.png").convert_alpha()
            self.logo = pygame.transform.scale(self.logo, (300, int(300 * self.logo.get_height() / self.logo.get_width())))
        except (pygame.error, FileNotFoundError):
            self.logo = None
            print("AVISO: 'assets/logo.png' não encontrado. Continuando sem logo.")
        
        self.tutoriais = {
            1: [
                "FASE 1: SETOR AUTÔMATO", "", "CONCEITO: Grafo não-direcionado.",
                "As rotas funcionam nos dois sentidos, como estradas.", "", "MISSÃO: Disseminar a Democracia.",
                "Use o algoritmo BFS para liberar todos os planetas", "alcançáveis a partir de um ponto inicial.",
                "", "CONTROLES:", " • Clique em um planeta para selecioná-lo como origem.",
                " • Pressione [B] para iniciar a varredura BFS.", " • Pressione [R] para simular um ataque inimigo a uma rota."
            ],
            2: [
                "FASE 2: SETOR TERMINÍDEO", "", "CONCEITO: Grafo Ponderado.",
                "Cada rota agora tem um 'custo' (combustível, tempo, risco).", "", "MISSÃO: Encontrar a Rota Logística Ótima.",
                "Use o algoritmo de Dijkstra para achar o caminho de menor", "custo entre dois planetas.",
                "", "CONTROLES:", " • Clique em um planeta para a ORIGEM.", " • Clique em outro para o DESTINO.",
                " • Pressione [D] para calcular a rota."
            ],
            3: [
                "FASE 3: SETOR ILUMINADO", "", "CONCEITO: Dígrafo (Grafo Direcionado).",
                "Rotas podem ser de mão única, como portais.", "", "MISSÃO: Detectar Paradoxo Psíquico.",
                "Use uma varredura (baseada em DFS) para encontrar 'ciclos',", "rotas que levam de volta ao ponto de partida.",
                "", "CONTROLES:", " • Pressione [C] para iniciar a varredura em todo o setor."
            ]
        }

    def _draw_text(self, txt: str, x: int, y: int, color=BRANCO, font=None, center_x=False, center_y=False):
        if font is None:
            font = self.fonte_normal
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
        
        chars_to_render = typed_chars
        for i, line in enumerate(intro_text):
            if chars_to_render <= 0: break
            render_text = line[:int(chars_to_render)]
            self._draw_text(render_text, LARGURA / 2, ALTURA * 0.6 + i * 30, center_x=True)
            chars_to_render -= len(line)

        if typed_chars >= sum(len(s) for s in intro_text):
             self._draw_text("Pressione qualquer tecla para iniciar a missão.", x=LARGURA/2, y=ALTURA - 50, color=AMARELO, center_x=True)

    def draw_hud(self, fase, msgs):
        panel_surf = pygame.Surface((LARGURA, 80))
        panel_surf.set_alpha(COR_PAINEL[3])
        panel_surf.fill(COR_PAINEL[:-1])
        self.tela.blit(panel_surf, (0,0))
        pygame.draw.line(self.tela, AMARELO, (0, 80), (LARGURA, 80), 2)

        fase_nomes = {1: "Autômatos (BFS)", 2: "Terminídeos (Dijkstra)", 3: "Iluminados (Ciclos)"}
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