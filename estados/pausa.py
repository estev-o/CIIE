from estados.estado import Estado
from estados.componentes import Boton
import pygame


class Pausa(Estado):
    """Menú de pausa con opciones"""

    def __init__(self, juego):
        Estado.__init__(self, juego)

        font = self.juego.fonts

        #botones
        centro_x = juego.ancho // 2
        centro_y = juego.alto // 2

        self.botones = [
            Boton(centro_x - 150, centro_y - 30, 300, 55, "Continuar", font.medium),
            Boton(centro_x - 150, centro_y + 40, 300, 55, "Configuración", font.medium),
            Boton(centro_x - 150, centro_y + 110, 300, 55, "Menú Principal", font.medium)
        ]

        self.indice_seleccionado = 0
        self.botones[self.indice_seleccionado].seleccionado = True

        self.cooldown_nav = 0
        self.delay_nav = 0.15

        self.mouse_pressed_prev = False

    def actualizar(self, dt, acciones):
        # Actualizar cooldown
        if self.cooldown_nav > 0:
            self.cooldown_nav -= dt

        if acciones.get("back") or acciones.get("toggle_pause"):
            if acciones.get("back"):
                self.juego.actions["back"] = False
            if acciones.get("toggle_pause"):
                self.juego.actions["toggle_pause"] = False
            self.salir_estado()
            return

        # teclado / mando
        if self.cooldown_nav <= 0:
            if acciones.get("arrowUp"):
                self.cambiar_seleccion(-1)
                self.cooldown_nav = self.delay_nav
            elif acciones.get("arrowDown"):
                self.cambiar_seleccion(1)
                self.cooldown_nav = self.delay_nav

        if acciones.get("enter") or acciones.get("attack1"):
            self.activar_opcion()
            self.juego.reset_keys()

        # Mouse
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
        if self.indice_seleccionado == 0:  # Continuar
            self.salir_estado()

        elif self.indice_seleccionado == 1:  # Configuración
            from estados.menu_configuracion import MenuConfiguracion
            MenuConfiguracion(self.juego).entrar_estado()

        elif self.indice_seleccionado == 2:  # Menú Principal
            while len(self.juego.state_stack) > 1:
                self.juego.state_stack.pop()

            from estados.menu_principal import MenuPrincipal
            MenuPrincipal(self.juego).entrar_estado()

    def dibujar(self, pantalla):
        # Dibujar estado anterior (el juego)
        self.estado_prev.dibujar(pantalla)

        # Overlay semi-transparente
        overlay = pygame.Surface((self.juego.ancho, self.juego.alto))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        pantalla.blit(overlay, (0, 0))

        # Marco decorativo
        centro_x = self.juego.ancho // 2
        centro_y = self.juego.alto // 2
        marco = pygame.Rect(centro_x - 250, centro_y - 150, 500, 400)
        pygame.draw.rect(pantalla, (30, 30, 50), marco, border_radius=15)
        pygame.draw.rect(pantalla, (100, 120, 180), marco, 3, border_radius=15)

        # Título "PAUSA"
        titulo = self.juego.fonts.big.render("PAUSA", True, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(centro_x, centro_y - 100))

        sombra = self.juego.fonts.big.render("PAUSA", True, (50, 50, 70))
        sombra_rect = sombra.get_rect(center=(centro_x + 3, centro_y - 97))
        pantalla.blit(sombra, sombra_rect)
        pantalla.blit(titulo, titulo_rect)

        # Dibujar botones
        for boton in self.botones:
            boton.dibujar(pantalla)

        # Instrucciones
        info = self.juego.fonts.small.render(
            "ESC: Continuar | ENTER: Seleccionar",
            True, (180, 180, 200)
        )
        info_rect = info.get_rect(center=(centro_x, self.juego.alto - 40))
        pantalla.blit(info, info_rect)
