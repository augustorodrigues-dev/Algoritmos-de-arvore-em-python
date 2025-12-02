from models import Planeta
from graph_system import MapaGalactico
import random

def _gerar_planetas_base() -> dict:
    """Retorna um dicionário com 16 planetas e suas coordenadas."""
    return {
        "Super-Terra": (640, 650), 
        "Marte": (640, 580),
        "Malevelon Creek": (300, 450),
        "Draupnir": (200, 500),
        "Ubanea": (150, 350),
        "Tien Kwan": (350, 300),
        "Vandalon IV": (250, 200),
        "Angel's Venture": (980, 450),
        "Heeth": (1080, 500),
        "Veld": (1130, 350),
        "Meridia": (930, 300),
        "Turing": (1030, 200),
        "Hellmire": (640, 100),
        "Estanu": (500, 180),
        "Crimsica": (780, 180),
        "Oshaune": (640, 250)
    }

def construir_mapa_fase1() -> MapaGalactico:
    """Fase 1: BFS (Muitas conexões, não ponderado)"""
    mg = MapaGalactico()
    coords = _gerar_planetas_base()
    faccao = {p: "Autômatos" for p in coords}; faccao["Super-Terra"] = "Aliança"; faccao["Marte"] = "Aliança"
    
    for nome, pos in coords.items(): mg.adicionar_planeta(Planeta(nome, faccao[nome], pos))
    
    rotas = [
        ("Super-Terra", "Marte"), ("Marte", "Malevelon Creek"), ("Marte", "Angel's Venture"), ("Marte", "Oshaune"),
        ("Malevelon Creek", "Draupnir"), ("Malevelon Creek", "Tien Kwan"), ("Draupnir", "Ubanea"), ("Ubanea", "Vandalon IV"),
        ("Tien Kwan", "Vandalon IV"), ("Tien Kwan", "Estanu"),
        ("Angel's Venture", "Heeth"), ("Angel's Venture", "Meridia"), ("Heeth", "Veld"), ("Veld", "Turing"),
        ("Meridia", "Turing"), ("Meridia", "Crimsica"),
        ("Oshaune", "Estanu"), ("Oshaune", "Crimsica"), ("Estanu", "Hellmire"), ("Crimsica", "Hellmire"),
        ("Vandalon IV", "Hellmire"), ("Turing", "Hellmire") 
    ]
    for u, v in rotas: mg.adicionar_rota(u, v)
    return mg

def construir_mapa_fase2() -> MapaGalactico:
    """Fase 2: Dijkstra (Ponderado)"""
    mg = MapaGalactico()
    coords = _gerar_planetas_base()
    faccao = {p: "Terminídeos" for p in coords}; faccao["Super-Terra"] = "Aliança"
    for nome, pos in coords.items(): mg.adicionar_planeta(Planeta(nome, faccao[nome], pos))
    
    def R(a, b, w): mg.adicionar_rota(a, b, peso=w)
    
    R("Super-Terra", "Marte", 2)
    R("Marte", "Malevelon Creek", 8); R("Marte", "Angel's Venture", 8); R("Marte", "Oshaune", 12)
    R("Malevelon Creek", "Draupnir", 3); R("Malevelon Creek", "Tien Kwan", 4)
    R("Draupnir", "Ubanea", 2); R("Ubanea", "Vandalon IV", 5)
    R("Tien Kwan", "Vandalon IV", 3); R("Tien Kwan", "Estanu", 6)
    R("Angel's Venture", "Heeth", 3); R("Angel's Venture", "Meridia", 4)
    R("Heeth", "Veld", 2); R("Veld", "Turing", 5)
    R("Meridia", "Turing", 3); R("Meridia", "Crimsica", 6)
    R("Oshaune", "Estanu", 4); R("Oshaune", "Crimsica", 4)
    R("Estanu", "Hellmire", 10); R("Crimsica", "Hellmire", 10)
    return mg

def construir_mapa_fase3() -> MapaGalactico:
    """Fase 3: Ciclos (Direcionado)"""
    mg = MapaGalactico()
    coords = _gerar_planetas_base()
    faccao = {p: "Iluminados" for p in coords}; faccao["Super-Terra"] = "Aliança"
    for nome, pos in coords.items(): mg.adicionar_planeta(Planeta(nome, faccao[nome], pos))
    
    def RD(a, b): mg.adicionar_rota_dirigida(a, b)
    
    RD("Super-Terra", "Marte")
    RD("Marte", "Malevelon Creek"); RD("Malevelon Creek", "Draupnir"); RD("Draupnir", "Marte") 
    RD("Marte", "Angel's Venture"); RD("Angel's Venture", "Heeth"); RD("Heeth", "Veld")
    RD("Veld", "Meridia"); RD("Meridia", "Angel's Venture")
    RD("Oshaune", "Estanu"); RD("Estanu", "Hellmire"); RD("Hellmire", "Crimsica"); RD("Crimsica", "Oshaune") 
    RD("Tien Kwan", "Vandalon IV"); RD("Vandalon IV", "Ubanea")
    return mg

def construir_mapa_fase4() -> MapaGalactico:
    """Fase 4: Bellman-Ford (Ponderado, pode ser instável)"""
    mg = construir_mapa_fase2()
    mg.adicionar_rota("Super-Terra", "Hellmire", peso=50)
    mg.adicionar_rota("Malevelon Creek", "Meridia", peso=15)
    return mg

def construir_mapa_fase5() -> MapaGalactico:
    """Fase 5: MST (Ponderado, Conectividade total)"""
    return construir_mapa_fase2()