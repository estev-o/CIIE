from estados.estado import Estado
from estados.componentes import SliderHorizontal, Toggle
import pygame


class MenuConfiguracion(Estado):

    def __init__(self, juego):
        Estado.__init__(self, juego)

        self.config = juego.configuracion
        centro_x = juego.ancho // 2

        # estado real de la ventana
        self.fullscreen_actual = bool(self.juego.screen.get_flags() & pygame.FULLSCREEN)

        # Sliders
        self.slider_musica = SliderHorizontal(
            centro_x - 200, 150, 400, 0, 100,
            self.config.get("volumen_musica", 70),
            "Volumen Música"
        )

        self.slider_efectos = SliderHorizontal(
            centro_x - 200, 240, 400, 0, 100,
            self.config.get("volumen_efectos", 80),
            "Volumen Efectos"
        )

        # Toggle
        self.toggle_pantalla = Toggle(
            centro_x + 120, 330,
            "Pantalla Completa",
            self.config.get("pantalla_completa", False)
        )


        # navegación
        self.elementos_navegables = 3
        self.indice_nav = 0
        self.cooldown_nav = 0
        self.delay_nav = 0.15

        # detector de flancos
        self.prev = {}

        # mouse
        self.mouse_pressed_prev = False

    # -----------------------------------------------------

    def actualizar(self, dt, acciones):

        # ---- detector de pulsación única ----
        if not self.prev:
            self.prev = acciones.copy()

        up    = acciones.get("arrowUp")    and not self.prev.get("arrowUp")
        down  = acciones.get("arrowDown")  and not self.prev.get("arrowDown")
        left  = acciones.get("arrowLeft")  and not self.prev.get("arrowLeft")
        right = acciones.get("arrowRight") and not self.prev.get("arrowRight")
        enter = acciones.get("enter")      and not self.prev.get("enter")
        esc   = acciones.get("esc")        and not self.prev.get("esc")

        # ---- mouse ----
        pos_mouse = pygame.mouse.get_pos()
        escala_x = self.juego.ancho / self.juego.screen.get_width()
        escala_y = self.juego.alto / self.juego.screen.get_height()
        pos_mouse_escalado = (int(pos_mouse[0] * escala_x), int(pos_mouse[1] * escala_y))
        mouse_pressed = pygame.mouse.get_pressed()[0]

        self.slider_musica.actualizar(pos_mouse_escalado, mouse_pressed)
        self.slider_efectos.actualizar(pos_mouse_escalado, mouse_pressed)
        self.toggle_pantalla.actualizar(dt, pos_mouse_escalado)


        self.mouse_pressed_prev = mouse_pressed

        # ---- navegación vertical ----
        if self.cooldown_nav > 0:
            self.cooldown_nav -= dt

        if self.cooldown_nav <= 0:
            if up:
                self.indice_nav = (self.indice_nav - 1) % self.elementos_navegables
                self.cooldown_nav = self.delay_nav

            elif down:
                self.indice_nav = (self.indice_nav + 1) % self.elementos_navegables
                self.cooldown_nav = self.delay_nav

        # ---- sliders ----
        if left or right:
            direccion = -1 if left else 1

            if self.indice_nav == 0:
                self.slider_musica.set_valor(self.slider_musica.valor + direccion * 5)

            elif self.indice_nav == 1:
                self.slider_efectos.set_valor(self.slider_efectos.valor + direccion * 5)

        # ---- enter ----
        if enter:

            # guardar
            if self.indice_nav == 3:
                self.guardar_y_salir()

            # toggle fullscreen instantáneo
            elif self.indice_nav == 2:
                self.toggle_pantalla.valor = not self.toggle_pantalla.valor

                nuevo = self.toggle_pantalla.valor
                if nuevo != self.fullscreen_actual:
                    if nuevo:
                        self.juego.screen = pygame.display.set_mode(
                            (self.juego.ancho, self.juego.alto), pygame.FULLSCREEN
                        )
                    else:
                        self.juego.screen = pygame.display.set_mode(
                            (self.juego.ancho, self.juego.alto)
                        )
                    self.fullscreen_actual = nuevo

        # ---- escape ----
        if esc:
            self.guardar_y_salir()
            self.juego.reset_keys()

        # guardar estado anterior
        self.prev = acciones.copy()

    # -----------------------------------------------------

    def guardar_y_salir(self):
        self.config.set("volumen_musica", self.slider_musica.valor)
        self.config.set("volumen_efectos", self.slider_efectos.valor)
        self.config.set("pantalla_completa", self.toggle_pantalla.valor)
        self.salir_estado()

    # -----------------------------------------------------

    def obtener_y_indice(self):
        if self.indice_nav == 0:
            return self.slider_musica.rect.centery
        elif self.indice_nav == 1:
            return self.slider_efectos.rect.centery
        elif self.indice_nav == 2:
            return self.toggle_pantalla.rect.centery


    def dibujar(self, pantalla):

        pantalla.fill((20, 20, 40))

        font_titulo = pygame.font.Font(None, 76)
        titulo = font_titulo.render("CONFIGURACIÓN", True, (255, 255, 255))
        pantalla.blit(titulo, titulo.get_rect(center=(self.juego.ancho // 2, 60)))

        pygame.draw.line(pantalla, (100, 100, 150), (100, 100), (self.juego.ancho - 100, 100), 2)

        self.slider_musica.dibujar(pantalla)
        self.slider_efectos.dibujar(pantalla)
        self.toggle_pantalla.dibujar(pantalla)

        y = self.obtener_y_indice()
        pygame.draw.circle(pantalla, (255, 200, 100), (60, y), 8)
        pygame.draw.circle(pantalla, (255, 255, 255), (60, y), 8, 2)

        font_info = pygame.font.Font(None, 24)
        info = font_info.render(
            "↑/↓: Navegar  |  ←/→: Ajustar  |  ENTER: Confirmar  |  ESC: Volver",
            True, (150, 150, 180)
        )
        pantalla.blit(info, info.get_rect(center=(self.juego.ancho // 2, self.juego.alto - 40)))
