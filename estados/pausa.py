from estados.estado import Estado
import pygame

class Pausa(Estado):
    def __init__(self, juego):
        Estado.__init__(self, juego)

    def actualizar(self, dt, acciones):
        if acciones.get("toggle_pause"):
            self.juego.actions["toggle_pause"] = False
            self.salir_estado()

    def dibujar(self, pantalla):
        # Render the previous state in the background
        self.estado_prev.dibujar(pantalla)

        # Draw a semi-transparent black overlay
        overlay = pygame.Surface((self.juego.ancho, self.juego.alto))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        pantalla.blit(overlay, (0, 0))

        # Draw "PAUSA" text in the center
        self.juego.draw_text(pantalla, "PAUSA", (255, 255, 255), self.juego.ancho // 2, self.juego.alto // 2)
