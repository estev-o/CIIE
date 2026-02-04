import pygame
from estados.player import Player
from estados.estado import Estado

class Hub(Estado):
    def __init__(self, juego):
        Estado.__init__(self,juego)
        # CARGAR FONDO AQUÍ

        # Puerta de salida (rectángulo) a la derecha en el centro
        self.puerta_rect = pygame.Rect(
            self.juego.ancho - 100,
            self.juego.alto // 2 - 50,
            80,
            100,
        )

        self.player = Player(self.juego)       

    def actualizar(self, dt, acciones):
        self.player.update(dt, acciones)

        # Si el rect del jugador toca cualquier parte del rectángulo de la puerta, cambiar de área
        if self.player.get_rect().colliderect(self.puerta_rect):
            from estados.area_experiment import AreaExperiment
            AreaExperiment(self.juego).entrar_estado()
            return

    def dibujar(self, pantalla):
        # Dibujar el Hub en la pantalla
        pantalla.fill((50, 50, 100))  # Fondo azul oscuro como ejemplo
        pygame.draw.rect(pantalla, (200, 100, 50), self.puerta_rect)

        self.juego.draw_text(pantalla, "HUB DEL JUEGO", (255, 255, 255), self.juego.ancho // 2, self.juego.alto // 2)
        self.player.render(pantalla)