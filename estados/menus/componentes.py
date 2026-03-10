import pygame

"""Componentes reutilizables de los menús."""


# =========================================================
# BOTON
# =========================================================
class Boton:
    def __init__(self, x, y, ancho, alto, texto, fuente, accion=None):
        # Rectángulo que define posición y tamaño del botón
        self.rect = pygame.Rect(x, y, ancho, alto)
        # Texto a mostrar
        self.texto = texto
        # Fuente letra a renderizar
        self.fuente = fuente
        # Acción a ejecutar
        self.accion = accion
        # Variables para controlar hovering y selección
        self.seleccionado = False
        self.hover = False

        # Colores y escalas para animación
        self.color_normal = (40, 40, 60)
        self.color_hover = (60, 60, 90)
        self.color_seleccionado = (80, 120, 180)
        self.color_borde = (150, 150, 200)
        self.color_borde_seleccionado = (255, 255, 255)
        self.color_texto = (255, 255, 255)
        self.escala = 1.0
        self.escala_objetivo = 1.0

    # Animación tamaño botón al seleccionarse
    def actualizar(self, dt):
        self.escala_objetivo = 1.05 if self.seleccionado else 1.0
        self.escala += (self.escala_objetivo - self.escala) * 10 * dt

    def dibujar(self, surface):
        if self.seleccionado:
            color = self.color_seleccionado
            color_borde = self.color_borde_seleccionado
            grosor_borde = 3
        elif self.hover:
            color = self.color_hover
            color_borde = self.color_borde
            grosor_borde = 2
        else:
            color = self.color_normal
            color_borde = self.color_borde
            grosor_borde = 2

        centro = self.rect.center
        ancho_escalado = int(self.rect.width * self.escala)
        alto_escalado = int(self.rect.height * self.escala)
        rect_escalado = pygame.Rect(0, 0, ancho_escalado, alto_escalado)
        rect_escalado.center = centro

        pygame.draw.rect(surface, color, rect_escalado, border_radius=8)
        pygame.draw.rect(surface, color_borde, rect_escalado, grosor_borde, border_radius=8)

        texto_surface = self.fuente.render(self.texto, False, self.color_texto)
        texto_rect = texto_surface.get_rect(center=rect_escalado.center)
        surface.blit(texto_surface, texto_rect)

    # Detectar hovering
    def verificar_hover(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)
        return self.hover

    # Detectar click
    def verificar_click(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)

    # Ejecutar acción
    def activar(self):
        if self.accion:
            self.accion()


# =========================================================
# SLIDER HORIZONTAL
# =========================================================
class SliderHorizontal:
    def __init__(self, x, y, ancho, valor_min, valor_max, valor_inicial, fuente, texto=""):
        # Rectángulo que define posición y tamaño del slider
        self.rect = pygame.Rect(x, y, ancho, 30)

        # Rango de valores
        self.valor_min = valor_min
        self.valor_max = valor_max
        self.valor = valor_inicial

        # Fuente y texto
        self.fuente = fuente
        self.texto = texto

        # Indica si hay arrastre
        self.arrastrando = False

        # Estilo
        self.color_fondo = (40, 40, 60)
        self.color_barra = (80, 120, 180)
        self.color_control = (150, 180, 255)
        self.color_control_hover = (200, 220, 255)
        self.color_borde = (150, 150, 200)

        # Tamaño del control deslizante
        self.control_radio = 12
        # Cursor sobre control
        self.control_hover = False

    # Calcula la posición horizontal del control según el valor actual
    def obtener_pos_control(self):
        porcentaje = (self.valor - self.valor_min) / (self.valor_max - self.valor_min)
        return self.rect.x + int(porcentaje * self.rect.width)

    # Actualiza el estado del slider según la interacción del ratón
    def actualizar(self, pos_mouse, mouse_pressed):
        control_x = self.obtener_pos_control()
        control_y = self.rect.centery

        # Comprobar si el cursor está cerca del control
        dist = ((pos_mouse[0] - control_x) ** 2 + (pos_mouse[1] - control_y) ** 2) ** 0.5
        self.control_hover = dist <= self.control_radio * 1.5

        # Si se pulsa el ratón, permitir arrastrar el control
        if mouse_pressed:
            if self.control_hover or self.arrastrando:
                self.arrastrando = True

                # Calcular posición relativa dentro del slider
                x_relativo = max(0, min(self.rect.width, pos_mouse[0] - self.rect.x))
                porcentaje = x_relativo / self.rect.width

                # Actualizar valor según la posición
                self.valor = int(self.valor_min + porcentaje * (self.valor_max - self.valor_min))
        else:
            self.arrastrando = False

    # Establece un valor manualmente asegurando que esté dentro del rango
    def set_valor(self, nuevo_valor):
        self.valor = max(self.valor_min, min(self.valor_max, nuevo_valor))

    def dibujar(self, surface):
        texto_surface = self.fuente.render(f"{self.texto}: {self.valor}%", False, (255, 255, 255))
        surface.blit(texto_surface, (self.rect.x, self.rect.y - 30))

        pygame.draw.rect(surface, self.color_fondo, self.rect, border_radius=4)
        pygame.draw.rect(surface, self.color_borde, self.rect, 2, border_radius=4)

        porcentaje = (self.valor - self.valor_min) / (self.valor_max - self.valor_min)
        barra_rect = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.width * porcentaje), self.rect.height)
        pygame.draw.rect(surface, self.color_barra, barra_rect, border_radius=4)

        control_x = self.obtener_pos_control()
        control_y = self.rect.centery

        color_control = self.color_control_hover if (self.control_hover or self.arrastrando) else self.color_control

        pygame.draw.circle(surface, color_control, (control_x, control_y), self.control_radio)
        pygame.draw.circle(surface, (255, 255, 255), (control_x, control_y), self.control_radio, 2)


# =========================================================
# OPCION BINARIA (ON / OFF)
# =========================================================
class OpcionBinaria:
    def __init__(self, x, y, ancho, texto, fuente, valor=False):
        # Posición en pantalla
        self.x = x
        self.y = y

        # Ancho
        self.ancho = ancho

        # Texto
        self.texto = texto

        # Fuente usada para renderizar
        self.fuente = fuente

        # Estadode la opción (True = ON, False = OFF)
        self.valor = valor

        # Altura del elemento en el menú
        self.altura = 40

    def cambiar(self):
        self.valor = not self.valor

    # Calcula el rectángulo ocupado por el elemento
    def obtener_rect(self):
        label = self.fuente.render(self.texto, False, (255, 255, 255))

        # Texto que indica el estado actual
        valor_txt = "ON  >" if self.valor else "OFF >"
        valor = self.fuente.render(valor_txt, False, (255, 255, 255))

        # Ajustar tamaño según el texto
        height = max(label.get_height(), valor.get_height())
        width = label.get_width() + 30 + valor.get_width()

        return pygame.Rect(self.x + 10, self.y + (self.altura - height) // 2, width, height)

    def dibujar(self, surface):
        rect = self.obtener_rect()

        # Texto de la opción (lado izquierdo)
        label = self.fuente.render(self.texto, False, (255, 255, 255))
        surface.blit(label, (rect.x, rect.y))

        # Estado actual (lado derecho)
        valor_txt = "<ON>" if self.valor else "<OFF>"
        valor = self.fuente.render(valor_txt, False, (255, 255, 255))
        surface.blit(valor, (rect.right - valor.get_width(), rect.y))


# =========================================================
# CONFIRMACIÓN MODAL - VENTANA EMERGENTE
# =========================================================
class ModalConfirmacion:
    def __init__(self, juego, texto, callback_confirmar, callback_cancelar):

        # Referencia al juego
        self.juego = juego

        # Texto
        self.texto = texto

        # Funciones que se ejecutan al confirmar o cancelar
        self.callback_confirmar = callback_confirmar
        self.callback_cancelar = callback_cancelar

        # Tamaño
        self.ancho = 640
        self.alto = 250

        # Rectángulo del modal
        self.rect = pygame.Rect(0, 0, self.ancho, self.alto)
        self.rect.center = (self.juego.ancho // 2, self.juego.alto // 2)

        # Posición de los botones interiores
        y_botones = self.rect.bottom - 80
        btn_ancho = 200
        btn_alto = 50
        espacio = 40

        # Calcular posición botones
        x_cancelar = self.rect.centerx - btn_ancho - espacio // 2
        x_confirmar = self.rect.centerx + espacio // 2

        # Reutilizar objeto Botón de esta clase
        self.btn_cancelar = Boton(x_cancelar, y_botones, btn_ancho, btn_alto, "Cancelar", self.juego.fonts.medium)
        self.btn_confirmar = Boton(x_confirmar, y_botones, btn_ancho, btn_alto, "Borrar", self.juego.fonts.medium)

        # Colores del botón de acción borrar
        self.btn_confirmar.color_normal = (150, 40, 40)
        self.btn_confirmar.color_hover = (180, 60, 60)
        self.btn_confirmar.color_seleccionado = (220, 80, 80)

        # Lista de botones
        self.botones = [self.btn_cancelar, self.btn_confirmar]

        # Índice
        self.indice_nav = 0

        # Control para controlar cambio rápido entre botones
        self.cooldown_nav = 0
        self.delay_nav = 0.15

        # Detección click ratón
        self.prev_mouse_pos = (0, 0)
        self.mouse_pressed_prev = pygame.mouse.get_pressed()[0]
        self.mouse_moviendose = False

    # Actualiza la lógica del modal (input y navegación)
    def actualizar(self, dt, acciones):

        # Posición del ratón en pantalla
        pos_mouse_escalado = acciones.get("mouse_pos", (0, 0))

        # Detectar click del ratón
        mouse_pressed = pygame.mouse.get_pressed()[0]
        click_mouse = mouse_pressed and not self.mouse_pressed_prev
        self.mouse_pressed_prev = mouse_pressed

        # Detectar movimiento del ratón
        self.mouse_moviendose = pos_mouse_escalado != self.prev_mouse_pos
        self.prev_mouse_pos = pos_mouse_escalado

        # Si el ratón se mueve, comprobar hovering
        if self.mouse_moviendose:
            for i, btn in enumerate(self.botones):
                if btn.verificar_hover(pos_mouse_escalado):
                    if i != self.indice_nav:
                        self.juego.sound_engine.play("menu_select")
                    self.indice_nav = i

        # Controles de navegación por teclado
        left = acciones.get("arrowLeft")
        right = acciones.get("arrowRight")
        enter = acciones.get("enter")
        back = acciones.get("back")

        # Reducir cooldown de navegación
        if self.cooldown_nav > 0:
            self.cooldown_nav -= dt

        # Cambiar selección con las flechas
        if self.cooldown_nav <= 0:
            if left or right:
                self.indice_nav = (self.indice_nav + 1) % 2
                self.juego.sound_engine.play("menu_select")
                self.cooldown_nav = self.delay_nav

        # Actualizar estado visual de los botones
        for i, btn in enumerate(self.botones):
            btn.seleccionado = (i == self.indice_nav)
            btn.actualizar(dt)

        # Confirmar selección
        if (click_mouse and self.botones[self.indice_nav].rect.collidepoint(pos_mouse_escalado)) or enter:
            self.juego.sound_engine.play("menu_accept")

            if self.indice_nav == 0:
                self.callback_cancelar()
            elif self.indice_nav == 1:
                self.callback_confirmar()

        # Cancelar con tecla de retroceso
        elif back:
            self.callback_cancelar()

    def dibujar(self, pantalla):

        overlay = pygame.Surface((self.juego.ancho, self.juego.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        pantalla.blit(overlay, (0, 0))

        pygame.draw.rect(pantalla, (40, 40, 60), self.rect, border_radius=15)
        pygame.draw.rect(pantalla, (150, 150, 200), self.rect, 3, border_radius=15)

        lineas = self.texto.split('\n')

        y_inicial = self.rect.top + 60
        if len(lineas) > 1:
            y_inicial = self.rect.top + 50

        for i, linea in enumerate(lineas):
            texto_surface = self.juego.fonts.medium.render(linea, False, (255, 255, 255))
            texto_rect = texto_surface.get_rect(center=(self.rect.centerx, y_inicial + i * 35))
            pantalla.blit(texto_surface, texto_rect)

        # Dibujar botones del modal
        for btn in self.botones:
            btn.dibujar(pantalla)
