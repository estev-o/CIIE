from estados.estado import Estado
import pygame

from estados.hub import Hub
from estados.area_experiment import AreaExperiment

class Titulo(Estado):
    """Pantalla de título con animación"""

    def __init__(self, juego):
        Estado.__init__(self, juego)

        # Animación de fade
        self.alpha = 0
        self.fade_speed = 150
        self.fade_in = True
        self.tiempo_espera = 5.0
        self.timer = 0

        # Parpadeo del texto "Press ENTER"
        self.blink_timer = 0
        self.mostrar_texto = True

    def actualizar(self, dt, acciones):
        # Fade in
        if self.fade_in:
            self.alpha = min(255, self.alpha + self.fade_speed * dt)
            if self.alpha >= 255:
                self.fade_in = False
                self.timer = 0
        else:
            self.timer += dt

        # Parpadeo del texto
        self.blink_timer += dt
        if self.blink_timer >= 0.5:
            self.mostrar_texto = not self.mostrar_texto
            self.blink_timer = 0

        # Saltar al menú con ENTER
        if acciones.get("enter"):
            from estados.menu_principal import MenuPrincipal
            MenuPrincipal(self.juego).entrar_estado()
            self.juego.reset_keys()

        # Auto-avanzar después de tiempo de espera
        if self.timer >= self.tiempo_espera and not self.fade_in:
            from estados.menu_principal import MenuPrincipal
            MenuPrincipal(self.juego).entrar_estado()

    def dibujar(self, pantalla):
        # Fondo degradado
        for y in range(pantalla.get_height()):
            ratio = y / pantalla.get_height()
            color = (
                int(10 + ratio * 20),
                int(10 + ratio * 30),
                int(30 + ratio * 60)
            )
            pygame.draw.line(pantalla, color, (0, y), (pantalla.get_width(), y))

        # Título con fade
        font_titulo = self.juego.fonts.big
        titulo = font_titulo.render("MANOLO", False, (255, 255, 255))
        titulo_surface = pygame.Surface(titulo.get_size(), pygame.SRCALPHA)
        titulo_surface.blit(titulo, (0, 0))
        titulo_surface.set_alpha(int(self.alpha))

        titulo_rect = titulo_surface.get_rect(center=(self.juego.ancho // 2, self.juego.alto // 2 - 50))

        # Sombra del título
        if self.alpha > 100:
            sombra = font_titulo.render("GILBERTOV EVIL", False, (50, 50, 80))
            sombra_surface = pygame.Surface(sombra.get_size(), pygame.SRCALPHA)
            sombra_surface.blit(sombra, (0, 0))
            sombra_surface.set_alpha(int(self.alpha * 0.5))
            sombra_rect = sombra_surface.get_rect(center=(self.juego.ancho // 2 + 4, self.juego.alto // 2 - 46))
            pantalla.blit(sombra_surface, sombra_rect)

        pantalla.blit(titulo_surface, titulo_rect)

        # Texto "Presiona ENTER" parpadeante
        if not self.fade_in and self.timer > 0.5 and self.mostrar_texto:
            font_sub = self.juego.fonts.medium
            subtitulo = font_sub.render("Presiona ENTER", False, (200, 200, 220))
            subtitulo_rect = subtitulo.get_rect(center=(self.juego.ancho // 2, self.juego.alto // 2 + 80))
            pantalla.blit(subtitulo, subtitulo_rect)
