from estados.estado import Estado
from estados.componentes import Boton
import pygame


class MenuPrincipal(Estado):

    def __init__(self, juego):
        Estado.__init__(self, juego)

        font = self.juego.fonts

        # crear botones
        centro_x = juego.ancho // 2
        self.botones = [
            Boton(centro_x - 150, 200, 300, 60, "Nueva Partida", font.medium),
            Boton(centro_x - 150, 280, 300, 60, "Continuar", font.medium),
            Boton(centro_x - 150, 360, 300, 60, "Configuración", font.medium),
            Boton(centro_x - 150, 440, 300, 60, "Salir", font.medium)
        ]

        self.indice_seleccionado = 0
        self.botones[self.indice_seleccionado].seleccionado = True

        # control  navegación
        self.cooldown_nav = 0
        self.delay_nav = 0.15

        self.mouse_pressed_prev = False

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
            elif acciones.get("esc"):
                self.juego.running = False

        if acciones.get("enter") or acciones.get("attack1"):
            self.activar_opcion()
            self.juego.reset_keys()

        pos_mouse = pygame.mouse.get_pos()
        escala_x = self.juego.ancho / self.juego.screen.get_width()
        escala_y = self.juego.alto / self.juego.screen.get_height()
        pos_mouse_escalado = (int(pos_mouse[0] * escala_x), int(pos_mouse[1] * escala_y))

        mouse_pressed = pygame.mouse.get_pressed()[0]

        for i, boton in enumerate(self.botones):
            if boton.verificar_hover(pos_mouse_escalado):
                if i != self.indice_seleccionado:
                    self.botones[self.indice_seleccionado].seleccionado = False
                    self.indice_seleccionado = i
                    self.botones[self.indice_seleccionado].seleccionado = True

        if mouse_pressed and not self.mouse_pressed_prev:
            for i, boton in enumerate(self.botones):
                if boton.verificar_click(pos_mouse_escalado):
                    self.indice_seleccionado = i
                    self.activar_opcion()
                    break

        self.mouse_pressed_prev = mouse_pressed

        for boton in self.botones:
            boton.actualizar(dt)

    def cambiar_seleccion(self, direccion):
        self.botones[self.indice_seleccionado].seleccionado = False
        self.indice_seleccionado = (self.indice_seleccionado + direccion) % len(self.botones)
        self.botones[self.indice_seleccionado].seleccionado = True

    def activar_opcion(self):
        if self.indice_seleccionado == 0:
            from estados.hub import Hub
            Hub(self.juego).entrar_estado()

        elif self.indice_seleccionado == 1:
            from estados.hub import Hub
            Hub(self.juego).entrar_estado()

        elif self.indice_seleccionado == 2:
            from estados.menu_configuracion import MenuConfiguracion
            MenuConfiguracion(self.juego).entrar_estado()

        elif self.indice_seleccionado == 3:
            self.juego.running = False

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
        titulo = self.juego.fonts.big.render("GILBERTOV EVIL", False, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(self.juego.ancho // 2, 100))

        sombra = self.juego.fonts.big.render("GILBERTOV EVIL", False, (50, 50, 80))
        sombra_rect = sombra.get_rect(center=(self.juego.ancho // 2 + 4, 104))
        pantalla.blit(sombra, sombra_rect)
        pantalla.blit(titulo, titulo_rect)

        for boton in self.botones:
            boton.dibujar(pantalla)

        # ---- INFO ----
        info = self.juego.fonts.small.render(
            "ENTER: Seleccionar  |  ESC: Salir",
            False, (150, 150, 180)
        )
        info_rect = info.get_rect(center=(self.juego.ancho // 2, self.juego.alto - 25))
        pantalla.blit(info, info_rect)
