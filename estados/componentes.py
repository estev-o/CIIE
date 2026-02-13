import pygame


class Boton:
    def __init__(self, x, y, ancho, alto, texto, accion=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.accion = accion
        self.seleccionado = False
        self.hover = False

        self.color_normal = (40, 40, 60)
        self.color_hover = (60, 60, 90)
        self.color_seleccionado = (80, 120, 180)
        self.color_borde = (150, 150, 200)
        self.color_borde_seleccionado = (255, 255, 255)
        self.color_texto = (255, 255, 255)

        self.escala = 1.0
        self.escala_objetivo = 1.0

    def actualizar(self, dt):
        if self.seleccionado:
            self.escala_objetivo = 1.05
        else:
            self.escala_objetivo = 1.0

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

        # Calcular rectángulo con escala
        centro = self.rect.center
        ancho_escalado = int(self.rect.width * self.escala)
        alto_escalado = int(self.rect.height * self.escala)
        rect_escalado = pygame.Rect(0, 0, ancho_escalado, alto_escalado)
        rect_escalado.center = centro

        #  fondo
        pygame.draw.rect(surface, color, rect_escalado, border_radius=8)

        #  borde
        pygame.draw.rect(surface, color_borde, rect_escalado, grosor_borde, border_radius=8)

        #  texto
        font = pygame.font.Font(None, 42)
        texto_surface = font.render(self.texto, True, self.color_texto)
        texto_rect = texto_surface.get_rect(center=rect_escalado.center)
        surface.blit(texto_surface, texto_rect)

    def verificar_hover(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)
        return self.hover

    def verificar_click(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)

    def activar(self):
        if self.accion:
            self.accion()


class SliderHorizontal:

    def __init__(self, x, y, ancho, valor_min, valor_max, valor_inicial, texto=""):
        self.rect = pygame.Rect(x, y, ancho, 30)
        self.valor_min = valor_min
        self.valor_max = valor_max
        self.valor = valor_inicial
        self.texto = texto
        self.arrastrando = False

        # Colores
        self.color_fondo = (40, 40, 60)
        self.color_barra = (80, 120, 180)
        self.color_control = (150, 180, 255)
        self.color_control_hover = (200, 220, 255)
        self.color_borde = (150, 150, 200)

        # Control deslizante
        self.control_radio = 12
        self.control_hover = False

    def obtener_pos_control(self):
        porcentaje = (self.valor - self.valor_min) / (self.valor_max - self.valor_min)
        return self.rect.x + int(porcentaje * self.rect.width)

    def actualizar(self, pos_mouse, mouse_pressed):
        control_x = self.obtener_pos_control()
        control_y = self.rect.centery

        #  hover en el control
        dist = ((pos_mouse[0] - control_x) ** 2 + (pos_mouse[1] - control_y) ** 2) ** 0.5
        self.control_hover = dist <= self.control_radio * 1.5

        #  arrastre
        if mouse_pressed:
            if self.control_hover or self.arrastrando:
                self.arrastrando = True
                # Calcular nuevo valor basado en posición del mouse
                x_relativo = max(0, min(self.rect.width, pos_mouse[0] - self.rect.x))
                porcentaje = x_relativo / self.rect.width
                self.valor = int(self.valor_min + porcentaje * (self.valor_max - self.valor_min))
        else:
            self.arrastrando = False

    def set_valor(self, nuevo_valor):
        # limitar al rango real del slider
        self.valor = max(self.valor_min, min(self.valor_max, nuevo_valor))

    def dibujar(self, surface):
        font = pygame.font.Font(None, 32)
        texto_surface = font.render(f"{self.texto}: {self.valor}%", True, (255, 255, 255))
        surface.blit(texto_surface, (self.rect.x, self.rect.y - 30))

        #  fondo de la barra
        pygame.draw.rect(surface, self.color_fondo, self.rect, border_radius=4)
        pygame.draw.rect(surface, self.color_borde, self.rect, 2, border_radius=4)

        #  barra de progreso
        porcentaje = (self.valor - self.valor_min) / (self.valor_max - self.valor_min)
        barra_rect = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.width * porcentaje), self.rect.height)
        pygame.draw.rect(surface, self.color_barra, barra_rect, border_radius=4)

        # slider
        control_x = self.obtener_pos_control()
        control_y = self.rect.centery

        color_control = self.color_control_hover if (self.control_hover or self.arrastrando) else self.color_control

        pygame.draw.circle(surface, color_control, (control_x, control_y), self.control_radio)
        pygame.draw.circle(surface, (255, 255, 255), (control_x, control_y), self.control_radio, 2)


class Toggle:
    """Botón de alternancia"""

    def __init__(self, x, y, texto, valor_inicial=False):
        self.rect = pygame.Rect(x, y, 80, 40)
        self.texto = texto
        self.valor = valor_inicial
        self.hover = False

        self.color_off = (60, 60, 80)
        self.color_on = (80, 180, 120)
        self.color_control = (255, 255, 255)

        self.pos_control = 0.0
        self.pos_objetivo = 1.0 if valor_inicial else 0.0

    def actualizar(self, dt, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)

        # Animar
        self.pos_objetivo = 1.0 if self.valor else 0.0
        self.pos_control += (self.pos_objetivo - self.pos_control) * 12 * dt

    def verificar_click(self, pos_mouse):
        if self.rect.collidepoint(pos_mouse):
            self.valor = not self.valor
            return True
        return False

    def dibujar(self, surface):
        font = pygame.font.Font(None, 32)
        texto_surface = font.render(self.texto, True, (255, 255, 255))
        surface.blit(texto_surface, (self.rect.x - 250, self.rect.y + 8))

        color_fondo = self.color_on if self.valor else self.color_off

        pygame.draw.rect(surface, color_fondo, self.rect, border_radius=20)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=20)

        radio_control = 16
        margen = 6
        x_min = self.rect.x + radio_control + margen
        x_max = self.rect.right - radio_control - margen
        control_x = int(x_min + (x_max - x_min) * self.pos_control)
        control_y = self.rect.centery

        pygame.draw.circle(surface, (0, 0, 0, 50), (control_x + 2, control_y + 2), radio_control)

        pygame.draw.circle(surface, self.color_control, (control_x, control_y), radio_control)
        pygame.draw.circle(surface, (220, 220, 220), (control_x, control_y), radio_control, 2)


class Selector:

    def __init__(self, x, y, ancho, texto, opciones, indice_inicial=0):
        self.rect = pygame.Rect(x, y, ancho, 50)
        self.texto = texto
        self.opciones = opciones
        self.indice = indice_inicial

        tam_flecha = 40
        margen = 10
        self.btn_izq = pygame.Rect(self.rect.x + margen, self.rect.y + 5, tam_flecha, tam_flecha)
        self.btn_der = pygame.Rect(self.rect.right - tam_flecha - margen, self.rect.y + 5, tam_flecha, tam_flecha)

        self.hover_izq = False
        self.hover_der = False

    def actualizar(self, pos_mouse):
        """Actualizar estados de hover"""
        self.hover_izq = self.btn_izq.collidepoint(pos_mouse)
        self.hover_der = self.btn_der.collidepoint(pos_mouse)

    def click_izquierda(self, pos_mouse):
        """Verificar click en flecha izquierda"""
        if self.btn_izq.collidepoint(pos_mouse):
            self.indice = (self.indice - 1) % len(self.opciones)
            return True
        return False

    def click_derecha(self, pos_mouse):
        """Verificar click en flecha derecha"""
        if self.btn_der.collidepoint(pos_mouse):
            self.indice = (self.indice + 1) % len(self.opciones)
            return True
        return False

    def obtener_valor(self):
        """Obtener opción seleccionada"""
        return self.opciones[self.indice]

    def dibujar(self, surface):
        """Dibujar el selector"""
        # Dibujar texto
        font = pygame.font.Font(None, 32)
        texto_surface = font.render(self.texto, True, (255, 255, 255))
        surface.blit(texto_surface, (self.rect.x, self.rect.y - 35))

        # Dibujar fondo
        pygame.draw.rect(surface, (40, 40, 60), self.rect, border_radius=8)
        pygame.draw.rect(surface, (150, 150, 200), self.rect, 2, border_radius=8)

        # Dibujar botón izquierdo
        color_izq = (80, 80, 120) if self.hover_izq else (60, 60, 90)
        pygame.draw.rect(surface, color_izq, self.btn_izq, border_radius=6)
        pygame.draw.rect(surface, (180, 180, 220), self.btn_izq, 2, border_radius=6)
        # Flecha izquierda
        centro = self.btn_izq.center
        puntos = [(centro[0] + 8, centro[1] - 10), (centro[0] + 8, centro[1] + 10), (centro[0] - 8, centro[1])]
        pygame.draw.polygon(surface, (255, 255, 255), puntos)

        # Dibujar botón derecho
        color_der = (80, 80, 120) if self.hover_der else (60, 60, 90)
        pygame.draw.rect(surface, color_der, self.btn_der, border_radius=6)
        pygame.draw.rect(surface, (180, 180, 220), self.btn_der, 2, border_radius=6)
        # Flecha derecha
        centro = self.btn_der.center
        puntos = [(centro[0] - 8, centro[1] - 10), (centro[0] - 8, centro[1] + 10), (centro[0] + 8, centro[1])]
        pygame.draw.polygon(surface, (255, 255, 255), puntos)

        # Dibujar valor actual
        font_valor = pygame.font.Font(None, 44)
        valor_text = font_valor.render(self.obtener_valor(), True, (255, 255, 255))
        valor_rect = valor_text.get_rect(center=self.rect.center)
        surface.blit(valor_text, valor_rect)
