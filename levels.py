from models import Planeta
from graph_system import MapaGalactico

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