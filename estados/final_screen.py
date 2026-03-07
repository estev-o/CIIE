import pygame

from estados.componentes import Boton
from estados.estado import Estado


class FinalScreen(Estado):
    def __init__(self, juego):
        super().__init__(juego)

        imagen_original = pygame.image.load("assets/UI/cursor/cursor.png").convert_alpha()
        self.cursor_img = pygame.transform.scale(imagen_original, (30, 30))

        juego.sound_engine.play_music_if_changed("win", 1000)

        font = self.juego.fonts
        centro_x = juego.ancho // 2
        self.botones = [
            Boton(centro_x - 150, 220, 300, 60, "Nueva Partida", font.medium),
            Boton(centro_x - 150, 300, 300, 60, "Menú principal", font.medium),
        ]

        self.indice_seleccionado = 0
        self.botones[self.indice_seleccionado].seleccionado = True

        self.cooldown_nav = 0.0
        self.delay_nav = 0.15
        self.mouse_pressed_prev = pygame.mouse.get_pressed()[0]

    def actualizar(self, dt, acciones):
        if self.cooldown_nav > 0:
            self.cooldown_nav -= dt

        if self.cooldown_nav <= 0:
            if acciones.get("arrowUp"):
                self.cambiar_seleccion(-1)
                self.cooldown_nav = self.delay_nav
            elif acciones.get("arrowDown"):
                self.cambiar_seleccion(1)
                self.cooldown_nav = self.delay_nav
            elif acciones.get("back"):
                self.juego.running = False

        if acciones.get("enter") or acciones.get("interact"):
            self.activar_opcion()
            self.juego.reset_keys()
            return

        pos_mouse_escalado = acciones.get("mouse_pos", (0, 0))

        for i, boton in enumerate(self.botones):
            if boton.verificar_hover(pos_mouse_escalado) and i != self.indice_seleccionado:
                self.botones[self.indice_seleccionado].seleccionado = False
                self.indice_seleccionado = i
                self.botones[self.indice_seleccionado].seleccionado = True
                self.juego.sound_engine.play("menu_select")

        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed and not self.mouse_pressed_prev:
            for i, boton in enumerate(self.botones):
                if boton.verificar_click(pos_mouse_escalado):
                    self.indice_seleccionado = i
                    return

        self.mouse_pressed_prev = mouse_pressed

        for boton in self.botones:
            boton.actualizar(dt)

    def cambiar_seleccion(self, direccion):
        self.botones[self.indice_seleccionado].seleccionado = False
        self.indice_seleccionado = (self.indice_seleccionado + direccion) % len(self.botones)
        self.botones[self.indice_seleccionado].seleccionado = True
        self.juego.sound_engine.play("menu_select")

    def activar_opcion(self):
        if self.indice_seleccionado == 0:
            self.juego.fade_to(lambda: self.juego.start_new_run("hub"))
            self.juego.sound_engine.play("menu_confirm")
        elif self.indice_seleccionado == 1:
            from estados.menu_principal import MenuPrincipal
            self.juego.fade_to(lambda: MenuPrincipal(self.juego).entrar_estado())
            self.juego.sound_engine.play("menu_confirm")

    def dibujar(self, pantalla):
        for y in range(pantalla.get_height()):
            ratio = y / pantalla.get_height()
            color = (
                int(8 + ratio * 18),
                int(30 + ratio * 55),
                int(18 + ratio * 25),
            )
            pygame.draw.line(pantalla, color, (0, y), (pantalla.get_width(), y))

        titulo = self.juego.fonts.big.render("¡VICTORIA!", False, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(self.juego.ancho // 2, 100))
        sombra = self.juego.fonts.big.render("¡VICTORIA!", False, (40, 80, 40))
        sombra_rect = sombra.get_rect(center=(self.juego.ancho // 2 + 4, 104))

        subtitulo = self.juego.fonts.medium.render(
            "¡Has derrotado a Gilbertov!",
            False,
            (230, 255, 230),
        )
        subtitulo_rect = subtitulo.get_rect(center=(self.juego.ancho // 2, 155))

        adn_texto = self.juego.fonts.medium.render(
            f"ADN acumulado: {self.juego.adn}",
            False,
            (255, 255, 255),
        )
        adn_rect = adn_texto.get_rect(center=(self.juego.ancho // 2, 185))

        pantalla.blit(sombra, sombra_rect)
        pantalla.blit(titulo, titulo_rect)
        pantalla.blit(subtitulo, subtitulo_rect)
        pantalla.blit(adn_texto, adn_rect)

        for boton in self.botones:
            boton.dibujar(pantalla)
