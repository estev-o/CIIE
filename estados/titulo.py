from estados.estado import Estado
from estados.hub import Hub

class Titulo(Estado):
    def __init__(self, juego):
        Estado.__init__(self, juego)

    def actualizar(self, dt, acciones):
        if acciones.get("enter"):
            Hub(self.juego).entrar_estado()
        self.juego.reset_keys()

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        self.juego.draw_text(pantalla, "PANTALLA DE TÍTULO (presiona enter)", (255, 255, 255), self.juego.ancho //2 , self.juego.alto //2)