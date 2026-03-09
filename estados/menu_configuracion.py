from estados.estado import Estado
from estados.componentes import SliderHorizontal, OpcionBinaria, Boton, ModalConfirmacion
import pygame


class MenuConfiguracion(Estado):

    def __init__(self, juego):
        Estado.__init__(self, juego)

        imagen_original = pygame.image.load("assets/UI/cursor/cursor.png").convert_alpha()
        self.cursor_img = pygame.transform.scale(imagen_original, (30, 30))

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

        # Boton borrar progreso
        self.btn_borrar_progreso = Boton(
            centro_x - 175,
            410,
            350,
            50,
            "Borrar Progreso",
            font.medium
        )
        self.btn_borrar_progreso.color_normal = (150, 40, 40)
        self.btn_borrar_progreso.color_hover = (180, 60, 60)
        self.btn_borrar_progreso.color_seleccionado = (220, 80, 80)

        # modal confirmacion
        self.modal = None

        # navegación teclado
        self.elementos_navegables = 4
        self.indice_nav = 0
        self.cooldown_nav = 0
        self.delay_nav = 0.15

        self.prev = {}

        # mouse
        self.mouse_pressed_prev = pygame.mouse.get_pressed()[0]
        self.prev_mouse_pos = (0, 0)
        self.mouse_moviendose = False



    def detectar_hover(self, pos):
        if self.slider_musica.rect.collidepoint(pos):
            return 0
        if self.slider_efectos.rect.collidepoint(pos):
            return 1
        if self.opcion_fullscreen.obtener_rect().collidepoint(pos):
            return 2
        if self.btn_borrar_progreso.rect.collidepoint(pos):
            return 3
        return None

    def actualizar(self, dt, acciones):

        if self.modal:
            self.modal.actualizar(dt, acciones)
            return

        if not self.prev:
            self.prev = acciones.copy()

        # -------- teclado edge trigger --------
        up = acciones.get("arrowUp") and not self.prev.get("arrowUp")
        down = acciones.get("arrowDown") and not self.prev.get("arrowDown")
        left = acciones.get("arrowLeft") and not self.prev.get("arrowLeft")
        right = acciones.get("arrowRight") and not self.prev.get("arrowRight")
        enter = acciones.get("enter") and not self.prev.get("enter")
        back = acciones.get("back") and not self.prev.get("back")

        # -------- mouse posición escalada --------
        pos_mouse_escalado = acciones.get("mouse_pos", (0, 0))
        mouse_pressed = pygame.mouse.get_pressed()[0]
        click_mouse = mouse_pressed and not self.mouse_pressed_prev
        self.mouse_pressed_prev = mouse_pressed

        self.mouse_moviendose = pos_mouse_escalado != self.prev_mouse_pos
        self.prev_mouse_pos = pos_mouse_escalado

        # hover → foco
        hover = self.detectar_hover(pos_mouse_escalado)
        if self.mouse_moviendose and hover is not None:
            if hover != self.indice_nav:
                self.juego.sound_engine.play("menu_select")
            self.indice_nav = hover


        # si el ratón se mueve, el teclado no manda
        if self.mouse_moviendose:
            up = down = left = right = enter = False

        # -------- interacción ratón --------
        if self.indice_nav == 0:
            self.slider_musica.actualizar(pos_mouse_escalado, mouse_pressed)
            self.juego.sound_engine.set_music_volume(self.slider_musica.valor)

        elif self.indice_nav == 1:
            self.slider_efectos.actualizar(pos_mouse_escalado, mouse_pressed)
            self.juego.sound_engine.set_sfx_volume(self.slider_efectos.valor)

        elif self.indice_nav == 2:
            if click_mouse and self.opcion_fullscreen.obtener_rect().collidepoint(pos_mouse_escalado):
                self.juego.sound_engine.play("menu_confirm")
                self.opcion_fullscreen.cambiar()
                self.aplicar_fullscreen()

        elif self.indice_nav == 3:
            if click_mouse and self.btn_borrar_progreso.rect.collidepoint(pos_mouse_escalado):
                self.abrir_modal()

        # -------- navegación teclado --------
        if self.cooldown_nav > 0:
            self.cooldown_nav -= dt

        if self.cooldown_nav <= 0:
            if up:
                self.indice_nav = (self.indice_nav - 1) % self.elementos_navegables
                self.cooldown_nav = self.delay_nav
                self.juego.sound_engine.play("menu_select")

            elif down:
                self.indice_nav = (self.indice_nav + 1) % self.elementos_navegables
                self.cooldown_nav = self.delay_nav
                self.juego.sound_engine.play("menu_select")

        # sliders teclado
        if left or right:
            direccion = -1 if left else 1

            if self.indice_nav == 0:
                self.slider_musica.set_valor(self.slider_musica.valor + direccion * 5)
                self.juego.sound_engine.set_music_volume(self.slider_musica.valor)

            elif self.indice_nav == 1:
                self.slider_efectos.set_valor(self.slider_efectos.valor + direccion * 5)
                self.juego.sound_engine.set_sfx_volume(self.slider_efectos.valor)

        # enter teclado
        if enter and self.indice_nav == 2:
            self.opcion_fullscreen.cambiar()
            self.aplicar_fullscreen()
        elif enter and self.indice_nav == 3:
            self.abrir_modal()

        # escape
        if back:
            self.guardar_y_salir()
            self.juego.reset_keys()

        self.btn_borrar_progreso.seleccionado = (self.indice_nav == 3)
        self.btn_borrar_progreso.actualizar(dt)

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

    def abrir_modal(self):
        self.juego.sound_engine.play("menu_confirm")
        self.modal = ModalConfirmacion(
            self.juego,
            "Esto borrará todo tu progreso.\n¿Estás seguro?",
            self.confirmar_borrado,
            self.cerrar_modal
        )

    def cerrar_modal(self):
        self.modal = None

    def confirmar_borrado(self):
        self.config.set("mejoras_persistentes", [])
        self.config.set("adn", 0)
        if hasattr(self.juego, "mejoras"):
            self.juego.mejoras._mejoras.clear()
        self.juego.adn = 0
        self.juego.start_new_run("menu")


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
        elif self.indice_nav == 3:
            return self.btn_borrar_progreso.rect.centery

    def dibujar(self, pantalla):

        pantalla.fill((20, 20, 40))

        titulo = self.juego.fonts.big.render("CONFIGURACIÓN", False, (255, 255, 255))
        pantalla.blit(titulo, titulo.get_rect(center=(self.juego.ancho // 2, 60)))

        pygame.draw.line(pantalla, (100, 100, 150), (100, 100), (self.juego.ancho - 100, 100), 2)

        self.slider_musica.dibujar(pantalla)
        self.slider_efectos.dibujar(pantalla)
        self.opcion_fullscreen.dibujar(pantalla)
        self.btn_borrar_progreso.dibujar(pantalla)

        y = self.obtener_y_indice()
        pygame.draw.circle(pantalla, (255, 200, 100), (60, y), 8)
        pygame.draw.circle(pantalla, (255, 255, 255), (60, y), 8, 2)

        current_mode = self.juego.actions.get("current_mode", "keyboard_mouse")
        info_text = "B: Volver" if current_mode == "controller" else "ESC: Volver"
        info = self.juego.fonts.small.render(
            info_text,
            False, (150, 150, 180)
        )
        pantalla.blit(info, info.get_rect(center=(self.juego.ancho // 2, self.juego.alto - 40)))

        if self.modal:
            self.modal.dibujar(pantalla)
