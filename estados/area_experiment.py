import pygame, os
from estados.estado import Estado
from personajes.player import Player

class AreaExperiment(Estado):
    def __init__(self, juego):
        Estado.__init__(self,juego)
        # CARGAR FONDO AQUÍ

        self.player = Player(self.juego)       

    def actualizar(self, dt, acciones):
        self.player.update(dt, acciones)

    def dibujar(self, pantalla):
        # Dibujar el Área de Experimento en la pantalla
        pantalla.fill((100, 50, 50))  # Fondo rojo oscuro como ejemplo
        # Puerta de salida (simple rectángulo) a la derecha en el centro
        pygame.draw.rect(pantalla, (50, 200, 50), (self.juego.ancho - 100, self.juego.alto // 2 - 50, 80, 100))
        
        self.juego.draw_text(pantalla, "ÁREA DE EXPERIMENTOS", (255, 255, 255), self.juego.ancho // 2, self.juego.alto // 2)
        self.player.render(pantalla)