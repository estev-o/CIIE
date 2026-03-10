import pygame
from estados.menus.menu_base import Menu
from estados.menus.componentes import Boton
from estados.menus.menu_configuracion import MenuConfiguracion


class MenuPrincipal(Menu):
    """Estado que implementa el menú principal del juego."""
    def __init__(self, juego):
        Menu.__init__(self, juego)

        # Iniciar música del menú si no está ya reproduciéndose
        juego.sound_engine.play_music_if_changed("menu",3000)

        #Obtener gestor de fuentes del juego
        font = self.juego.fonts

        # Crear botones usando componentes.py
        centro_x = juego.ancho // 2
        self.botones = [
            Boton(centro_x - 150, 200, 300, 60, "Jugar", font.medium,
                  lambda: self.juego.fade_to(lambda: self.juego.start_new_run("hub"))),
            Boton(centro_x - 150, 280, 300, 60, "Configuración", font.medium,
                  lambda: MenuConfiguracion(self.juego).entrar_estado()),
            Boton(centro_x - 150, 360, 300, 60, "Salir", font.medium,
                  lambda: setattr(self.juego, "running", False))
        ]

        self.botones[self.indice_seleccionado].seleccionado = True

    def dibujar(self, pantalla):
        # Fondo degradado
        for y in range(pantalla.get_height()):
            ratio = y / pantalla.get_height()
            color = (
                int(15 + ratio * 25),
                int(15 + ratio * 35),
                int(40 + ratio * 60)
            )
            pygame.draw.line(pantalla, color, (0, y), (pantalla.get_width(), y))

        # ---- TITULO ----
        titulo = self.juego.fonts.big.render("BINDING OF BLUB", False, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(self.juego.ancho // 2, 100))

        sombra = self.juego.fonts.big.render("BINDING OF BLUB", False, (50, 50, 80))
        sombra_rect = sombra.get_rect(center=(self.juego.ancho // 2 + 4, 104))
        pantalla.blit(sombra, sombra_rect)
        pantalla.blit(titulo, titulo_rect)

        for boton in self.botones:
            boton.dibujar(pantalla)

        # ---- INFO ----
        current_mode = self.juego.actions.get("current_mode", "keyboard_mouse")
        if current_mode == "controller":
            info_text = "A: Seleccionar  |  B: Salir"
        else:
            info_text = "ENTER: Seleccionar  |  ESC: Salir"
        info = self.juego.fonts.small.render(
            info_text,
            False, (150, 150, 180)
        )
        info_rect = info.get_rect(center=(self.juego.ancho // 2, self.juego.alto - 25))
        pantalla.blit(info, info_rect)