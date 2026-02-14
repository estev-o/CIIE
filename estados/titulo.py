from estados.estado import Estado
from estados.hub import Hub
from estados.area_experiment import AreaExperiment

class Titulo(Estado):
    def __init__(self, juego):
        Estado.__init__(self, juego)

    def actualizar(self, dt, acciones):
        if acciones.get("enter"):
            if self.juego.debug and getattr(self.juego, "skip_hub", False):
                AreaExperiment(self.juego).entrar_estado()
            else:
                Hub(self.juego).entrar_estado()
        self.juego.reset_keys()

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        self.juego.draw_text(pantalla, "PANTALLA DE TÍTULO (presiona enter)", (255, 255, 255), self.juego.ancho //2 , self.juego.alto //2)