import pygame
from estados.menus.menu_base import Menu
from estados.menus.componentes import Boton
from estados.menus.menu_principal import MenuPrincipal


class Muerte(Menu):
    """Estado que implementa el menú de muerte del juego."""
    def __init__(self, juego):
        Menu.__init__(self, juego)

        # Obtener gestor de fuentes del juego
        font = self.juego.fonts

        # Iniciar música del menú si no está ya reproduciéndose
        juego.sound_engine.play_music_if_changed("dead", 3000)

        centro_x = juego.ancho // 2

        # Crear botones usando componentes.py
        self.botones = [
            Boton(centro_x - 150, 200, 300, 60, "Nueva Partida", font.medium,
                  lambda: self.juego.fade_to(lambda: self.juego.start_new_run("hub"))),
            Boton(centro_x - 150, 280, 300, 60, "Menú principal", font.medium,
                  lambda: self.juego.fade_to(lambda: MenuPrincipal(self.juego).entrar_estado()))
        ]

        # Indice de botón seleccionado
        self.botones[self.indice_seleccionado].seleccionado = True

    def dibujar(self, pantalla):
        for y in range(pantalla.get_height()):
            ratio = y / pantalla.get_height()
            color = (
                int(15 + ratio * 25),
                int(15 + ratio * 35),
                int(40 + ratio * 60)
            )
            pygame.draw.line(pantalla, color, (0, y), (pantalla.get_width(), y))

        titulo = self.juego.fonts.big.render("HAS MUERTO", False, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(self.juego.ancho // 2, 100))
        sombra = self.juego.fonts.big.render("HAS MUERTO", False, (50, 50, 80))
        sombra_rect = sombra.get_rect(center=(self.juego.ancho // 2 + 4, 104))
        adn_texto = self.juego.fonts.medium.render(f"ADN acumulado: {self.juego.adn}", False, (255, 255, 255))
        adn_rect = adn_texto.get_rect(center=(self.juego.ancho // 2, 155))

        pantalla.blit(sombra, sombra_rect)
        pantalla.blit(titulo, titulo_rect)
        pantalla.blit(adn_texto, adn_rect)

        for boton in self.botones:
            boton.dibujar(pantalla)