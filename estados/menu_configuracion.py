from estados.estado import Estado
from estados.componentes import SliderHorizontal, OpcionBinaria
import pygame


class MenuConfiguracion(Estado):

    def __init__(self, juego):
        Estado.__init__(self, juego)

        font = self.juego.fonts
        self.config = juego.configuracion
        centro_x = juego.ancho // 2

        # Sliders
        self.slider_musica = SliderHorizontal(
            centro_x - 200, 150, 400, 0, 100,
            self.config.get("volumen_musica", 70),
            font.medium,
            "Volumen Música"
        )

        self.slider_efectos = SliderHorizontal(
            centro_x - 200, 240, 400, 0, 100,
            self.config.get("volumen_efectos", 80),
            font.medium,
            "Volumen Efectos"
        )

        # Opción binaria fullscreen
        self.opcion_fullscreen = OpcionBinaria(
            centro_x - 200,
            330,
            400,
            "Pantalla Completa",
            font.medium,
            self.config.get("pantalla_completa", False)
        )

        # navegación teclado
        self.elementos_navegables = 3
        self.indice_nav = 0
        self.cooldown_nav = 0
        self.delay_nav = 0.15

        self.prev = {}

        # mouse
        self.mouse_pressed_prev = False
        self.prev_mouse_pos = (0, 0)
        self.mouse_moviendose = False



    def detectar_hover(self, pos):
        if self.slider_musica.rect.collidepoint(pos):
            return 0
        if self.slider_efectos.rect.collidepoint(pos):
            return 1
        if self.opcion_fullscreen.obtener_rect().collidepoint(pos):
            return 2
        return None



    def actualizar(self, dt, acciones):

        if not self.prev:
            self.prev = acciones.copy()

        # -------- teclado edge trigger --------
        up    = acciones.get("arrowUp")    and not self.prev.get("arrowUp")
        down  = acciones.get("arrowDown")  and not self.prev.get("arrowDown")
        left  = acciones.get("arrowLeft")  and not self.prev.get("arrowLeft")
        right = acciones.get("arrowRight") and not self.prev.get("arrowRight")
        enter = acciones.get("enter")      and not self.prev.get("enter")
        esc   = acciones.get("esc")        and not self.prev.get("esc")

        # -------- mouse posición escalada --------
        pos_mouse = pygame.mouse.get_pos()
        escala_x = self.juego.ancho / self.juego.screen.get_width()
        escala_y = self.juego.alto / self.juego.screen.get_height()
        pos_mouse_escalado = (int(pos_mouse[0] * escala_x), int(pos_mouse[1] * escala_y))

        # detectar movimiento
        self.mouse_moviendose = pos_mouse != self.prev_mouse_pos
        self.prev_mouse_pos = pos_mouse

        # hover → foco
        hover = self.detectar_hover(pos_mouse_escalado)
        if self.mouse_moviendose and hover is not None:
            self.indice_nav = hover

        # click real
        mouse_pressed = pygame.mouse.get_pressed()[0]
        click = mouse_pressed and not self.mouse_pressed_prev
        self.mouse_pressed_prev = mouse_pressed

        # si el ratón se mueve, el teclado no manda
        if self.mouse_moviendose:
            up = down = left = right = enter = False

        # -------- interacción ratón --------
        if self.indice_nav == 0:
            self.slider_musica.actualizar(pos_mouse_escalado, mouse_pressed)

        elif self.indice_nav == 1:
            self.slider_efectos.actualizar(pos_mouse_escalado, mouse_pressed)

        elif self.indice_nav == 2:
            if click and self.opcion_fullscreen.obtener_rect().collidepoint(pos_mouse_escalado):
                self.opcion_fullscreen.cambiar()
                self.aplicar_fullscreen()

        # -------- navegación teclado --------
        if self.cooldown_nav > 0:
            self.cooldown_nav -= dt

        if self.cooldown_nav <= 0:
            if up:
                self.indice_nav = (self.indice_nav - 1) % self.elementos_navegables
                self.cooldown_nav = self.delay_nav

            elif down:
                self.indice_nav = (self.indice_nav + 1) % self.elementos_navegables
                self.cooldown_nav = self.delay_nav

        # sliders teclado
        if left or right:
            direccion = -1 if left else 1

            if self.indice_nav == 0:
                self.slider_musica.set_valor(self.slider_musica.valor + direccion * 5)

            elif self.indice_nav == 1:
                self.slider_efectos.set_valor(self.slider_efectos.valor + direccion * 5)

        # enter teclado
        if enter and self.indice_nav == 2:
            self.opcion_fullscreen.cambiar()
            self.aplicar_fullscreen()

        # escape
        if esc:
            self.guardar_y_salir()
            self.juego.reset_keys()

        self.prev = acciones.copy()


    def aplicar_fullscreen(self):
        if self.opcion_fullscreen.valor:
            self.juego.screen = pygame.display.set_mode(
                (self.juego.ancho, self.juego.alto), pygame.FULLSCREEN
            )
        else:
            self.juego.screen = pygame.display.set_mode(
                (self.juego.ancho, self.juego.alto)
            )



    def guardar_y_salir(self):
        self.config.set("volumen_musica", self.slider_musica.valor)
        self.config.set("volumen_efectos", self.slider_efectos.valor)
        self.config.set("pantalla_completa", self.opcion_fullscreen.valor)
        self.salir_estado()


    def obtener_y_indice(self):
        if self.indice_nav == 0:
            return self.slider_musica.rect.centery
        elif self.indice_nav == 1:
            return self.slider_efectos.rect.centery
        elif self.indice_nav == 2:
            return self.opcion_fullscreen.obtener_rect().centery

    def dibujar(self, pantalla):

        pantalla.fill((20, 20, 40))

        titulo = self.juego.fonts.big.render("CONFIGURACIÓN", False, (255, 255, 255))
        pantalla.blit(titulo, titulo.get_rect(center=(self.juego.ancho // 2, 60)))

        pygame.draw.line(pantalla, (100, 100, 150), (100, 100), (self.juego.ancho - 100, 100), 2)

        self.slider_musica.dibujar(pantalla)
        self.slider_efectos.dibujar(pantalla)
        self.opcion_fullscreen.dibujar(pantalla)

        y = self.obtener_y_indice()
        pygame.draw.circle(pantalla, (255, 200, 100), (60, y), 8)
        pygame.draw.circle(pantalla, (255, 255, 255), (60, y), 8, 2)

        info = self.juego.fonts.small.render(
            "ESC: Volver",
            False, (150, 150, 180)
        )
        pantalla.blit(info, info.get_rect(center=(self.juego.ancho // 2, self.juego.alto - 40)))
