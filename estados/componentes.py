import pygame


import pygame


# =========================================================
# BOTON
# =========================================================
class Boton:
    def __init__(self, x, y, ancho, alto, texto, fuente, accion=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.fuente = fuente
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

    def verificar_hover(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)
        return self.hover

    def verificar_click(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)

    def activar(self):
        if self.accion:
            self.accion()


# =========================================================
# SLIDER
# =========================================================
class SliderHorizontal:

    def __init__(self, x, y, ancho, valor_min, valor_max, valor_inicial, fuente, texto=""):
        self.rect = pygame.Rect(x, y, ancho, 30)
        self.valor_min = valor_min
        self.valor_max = valor_max
        self.valor = valor_inicial
        self.fuente = fuente
        self.texto = texto
        self.arrastrando = False

        self.color_fondo = (40, 40, 60)
        self.color_barra = (80, 120, 180)
        self.color_control = (150, 180, 255)
        self.color_control_hover = (200, 220, 255)
        self.color_borde = (150, 150, 200)

        self.control_radio = 12
        self.control_hover = False

    def obtener_pos_control(self):
        porcentaje = (self.valor - self.valor_min) / (self.valor_max - self.valor_min)
        return self.rect.x + int(porcentaje * self.rect.width)

    def actualizar(self, pos_mouse, mouse_pressed):
        control_x = self.obtener_pos_control()
        control_y = self.rect.centery

        dist = ((pos_mouse[0] - control_x) ** 2 + (pos_mouse[1] - control_y) ** 2) ** 0.5
        self.control_hover = dist <= self.control_radio * 1.5

        if mouse_pressed:
            if self.control_hover or self.arrastrando:
                self.arrastrando = True
                x_relativo = max(0, min(self.rect.width, pos_mouse[0] - self.rect.x))
                porcentaje = x_relativo / self.rect.width
                self.valor = int(self.valor_min + porcentaje * (self.valor_max - self.valor_min))
        else:
            self.arrastrando = False

    def set_valor(self, nuevo_valor):
        self.valor = max(self.valor_min, min(self.valor_max, nuevo_valor))

    def dibujar(self, surface):
        texto_surface = self.fuente.render(f"{self.texto}: {self.valor}%", False, (255,255,255))
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
        pygame.draw.circle(surface, (255,255,255), (control_x, control_y), self.control_radio, 2)


# =========================================================
# OPCION BINARIA (ON / OFF)
# =========================================================
class OpcionBinaria:

    def __init__(self, x, y, ancho, texto, fuente, valor=False):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.texto = texto
        self.fuente = fuente
        self.valor = valor
        self.altura = 40

    def cambiar(self):
        self.valor = not self.valor

    def obtener_rect(self):
        label = self.fuente.render(self.texto, False, (255, 255, 255))
        valor_txt = "ON  >" if self.valor else "OFF >"
        valor = self.fuente.render(valor_txt, False, (255, 255, 255))

        height = max(label.get_height(), valor.get_height())
        width = label.get_width() + 30 + valor.get_width()

        return pygame.Rect(self.x + 10, self.y + (self.altura - height) // 2, width, height)

    def dibujar(self, surface):
        rect = self.obtener_rect()

        # texto izquierda
        label = self.fuente.render(self.texto, False, (255, 255, 255))
        surface.blit(label, (rect.x, rect.y))

        # valor derecha
        valor_txt = "<ON>" if self.valor else "<OFF>"
        valor = self.fuente.render(valor_txt, False, (255, 255, 255))
        surface.blit(valor, (rect.right - valor.get_width(), rect.y))


