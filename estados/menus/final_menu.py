import pygame
from estados.menus.menu_base import Menu
from estados.menus.componentes import Boton
from estados.menus.menu_principal import MenuPrincipal


class FinalScreen(Menu):
    """Estado que implementa el menú final de victoria."""
    def __init__(self, juego):
        Menu.__init__(self, juego)

        #Cargar imagen final victoria
        try:
            self.imagen_final = pygame.image.load("assets/pantalla final/pantalla final.png").convert()
            self.imagen_final = pygame.transform.scale(self.imagen_final, (juego.ancho, juego.alto))
        except:
            self.imagen_final = pygame.Surface((juego.ancho, juego.alto))
            self.imagen_final.fill((0, 0, 0))

        #Parámetros animación
        self.fase_animacion = "fade_in"
        self.timer_animacion = 0.0
        self.duracion_fade = 2.0
        self.duracion_mostrar = 4.0

        # Iniciar música del menú si no está ya reproduciéndose
        juego.sound_engine.play_music_if_changed("win", 1000)

        #Obtener gestor fuentes
        font = self.juego.fonts

        centro_x = juego.ancho // 2

        self.botones = [
            Boton(centro_x - 150, 320, 300, 60, "Nueva Partida", font.medium,
                  lambda: self.juego.fade_to(lambda: self.juego.start_new_run("hub"))),
            Boton(centro_x - 150, 400, 300, 60, "Menú principal", font.medium,
                  lambda: self.juego.fade_to(lambda: MenuPrincipal(self.juego).entrar_estado()))
        ]

        self.botones[self.indice_seleccionado].seleccionado = True

    def actualizar(self, dt, acciones):
        # Mientras dure la animación, solo avanzar el timer
        if self.fase_animacion != "stats":
            self.timer_animacion += dt
            if self.fase_animacion == "fade_in":
                if self.timer_animacion >= self.duracion_fade:
                    self.fase_animacion = "mostrar"
                    self.timer_animacion = 0.0
            elif self.fase_animacion == "mostrar":
                if self.timer_animacion >= self.duracion_mostrar:
                    self.fase_animacion = "fade_out"
                    self.timer_animacion = 0.0
            elif self.fase_animacion == "fade_out":
                if self.timer_animacion >= self.duracion_fade:
                    self.fase_animacion = "stats"
                    self.juego.reset_keys()
            return

        # Una vez en fase stats, delegar al actualizar base
        super().actualizar(dt, acciones)

    def dibujar(self, pantalla):
        titulo = self.juego.fonts.big.render("¡VICTORIA!", False, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(self.juego.ancho // 2, 100))
        sombra = self.juego.fonts.big.render("¡VICTORIA!", False, (40, 80, 40))
        sombra_rect = sombra.get_rect(center=(self.juego.ancho // 2 + 4, 100 + 4))

        if self.fase_animacion != "stats":
            pantalla.fill((0, 0, 0))
            alfa = 255
            if self.fase_animacion == "fade_in":
                alfa = int((self.timer_animacion / self.duracion_fade) * 255)
            elif self.fase_animacion == "fade_out":
                alfa = int((1.0 - (self.timer_animacion / self.duracion_fade)) * 255)
            alfa = max(0, min(255, alfa))
            self.imagen_final.set_alpha(alfa)
            pantalla.blit(self.imagen_final, (0, 0))

            sombra.set_alpha(alfa)
            titulo.set_alpha(alfa)
            pantalla.blit(sombra, sombra_rect)
            pantalla.blit(titulo, titulo_rect)
            return

        for y in range(pantalla.get_height()):
            ratio = y / pantalla.get_height()
            color = (
                int(8 + ratio * 18),
                int(30 + ratio * 55),
                int(18 + ratio * 25),
            )
            pygame.draw.line(pantalla, color, (0, y), (pantalla.get_width(), y))

        subtitulo = self.juego.fonts.medium.render(
            "¡Has derrotado a Gilbertov!",
            False,
            (230, 255, 230),
        )
        subtitulo_rect = subtitulo.get_rect(center=(self.juego.ancho // 2, 190))

        adn_texto = self.juego.fonts.medium.render(
            f"ADN acumulado: {self.juego.adn}",
            False,
            (255, 255, 255),
        )
        adn_rect = adn_texto.get_rect(center=(self.juego.ancho // 2, 240))

        pantalla.blit(sombra, sombra_rect)
        pantalla.blit(titulo, titulo_rect)
        pantalla.blit(subtitulo, subtitulo_rect)
        pantalla.blit(adn_texto, adn_rect)

        for boton in self.botones:
            boton.dibujar(pantalla)