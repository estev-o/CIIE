from estados.estado import Estado
import pygame
import random
import math


class Titulo(Estado):
    """Pantalla de título avanzada con efectos visuales"""

    def __init__(self, juego):
        super().__init__(juego)

        # Fade general
        self.alpha = 0
        self.fade_speed = 180
        self.fase = "fade_in"  # fade_in → idle → fade_out

        # Animación del título
        self.zoom = 0.6
        self.zoom_speed = 0.25

        # Glitch
        self.glitch_timer = 0
        self.glitch_interval = 0.15
        self.glitch_offset = 0

        # Partículas del fondo
        self.particulas = []
        for _ in range(60):
            self.particulas.append([
                random.randint(0, juego.ancho),
                random.randint(0, juego.alto),
                random.uniform(0.2, 1.2),
                random.randint(1, 3)
            ])

        # Texto ENTER
        self.enter_alpha = 0
        self.enter_speed = 200
        self.enter_visible = True
        self.enter_timer = 0

        # Tiempo antes de auto avanzar
        self.timer = 0
        self.tiempo_espera = 6

    def actualizar(self, dt, acciones):

        # --- FADE IN ---
        if self.fase == "fade_in":
            self.alpha += self.fade_speed * dt
            if self.alpha >= 255:
                self.alpha = 255
                self.fase = "idle"

        # --- IDLE ---
        elif self.fase == "idle":
            self.timer += dt

            # Animación de zoom suave
            self.zoom += self.zoom_speed * dt
            if self.zoom > 1.05:
                self.zoom_speed *= -1
            elif self.zoom < 0.95:
                self.zoom_speed *= -1

            # Glitch
            self.glitch_timer += dt
            if self.glitch_timer >= self.glitch_interval:
                self.glitch_offset = random.randint(-4, 4)
                self.glitch_timer = 0

            # Texto ENTER aparece y parpadea
            self.enter_alpha += self.enter_speed * dt
            if self.enter_alpha >= 255:
                self.enter_alpha = 255
                self.enter_speed *= -1
            elif self.enter_alpha <= 0:
                self.enter_alpha = 0
                self.enter_speed *= -1

            # Auto avanzar
            if self.timer >= self.tiempo_espera:
                self.fase = "fade_out"

        # --- FADE OUT ---
        elif self.fase == "fade_out":
            self.alpha -= self.fade_speed * dt
            if self.alpha <= 0:
                self.alpha = 0
                from estados.menu_principal import MenuPrincipal
                MenuPrincipal(self.juego).entrar_estado()

        # ENTER para saltar
        if acciones.get("enter"):
            self.fase = "fade_out"
            self.juego.reset_keys()

        # Actualizar partículas
        for p in self.particulas:
            p[1] -= p[2]
            if p[1] < -5:
                p[0] = random.randint(0, self.juego.ancho)
                p[1] = self.juego.alto + 5

    def dibujar(self, pantalla):

        # Fondo degradado dinámico
        for y in range(pantalla.get_height()):
            ratio = y / pantalla.get_height()
            color = (
                int(20 + ratio * 40),
                int(10 + ratio * 20),
                int(40 + ratio * 80)
            )
            pygame.draw.line(pantalla, color, (0, y), (pantalla.get_width(), y))

        # Partículas
        for x, y, vel, size in self.particulas:
            pygame.draw.rect(pantalla, (180, 180, 255), (x, y, size, size))

        # Título con zoom + glitch
        font = self.juego.fonts.big
        texto = "GILBERTOV EVIL"

        render = font.render(texto, True, (255, 255, 255))
        w, h = render.get_size()

        # Superficie escalada
        escala = pygame.transform.scale(
            render,
            (int(w * self.zoom), int(h * self.zoom))
        )

        rect = escala.get_rect(center=(
            self.juego.ancho // 2 + self.glitch_offset,
            self.juego.alto // 2 - 60
        ))

        # Aplicar alpha general
        escala.set_alpha(int(self.alpha))
        pantalla.blit(escala, rect)

        # Texto ENTER
        if self.fase == "idle":
            font2 = self.juego.fonts.medium
            enter = font2.render("Presiona ENTER", True, (220, 220, 240))
            enter.set_alpha(int(self.enter_alpha))
            rect2 = enter.get_rect(center=(self.juego.ancho // 2, self.juego.alto // 2 + 80))
            pantalla.blit(enter, rect2)
