from estados.estado import Estado
import pygame
import random
import math

#FULL IA
class BurbujaExperimento:
    """Burbujas verdes de laboratorio que flotan"""

    def __init__(self, x, y, ancho_pantalla, alto_pantalla):
        self.x = x
        self.y = y
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        self.velocidad_x = random.uniform(-15, 15)
        self.velocidad_y = random.uniform(-40, -20)
        self.tamaño = random.randint(3, 12)
        self.alpha = random.randint(150, 255)
        # Colores verdes tóxicos del laboratorio
        self.color = random.choice([
            (50, 255, 50),  # Verde brillante (Blub)
            (100, 255, 100),  # Verde claro
            (0, 200, 0),  # Verde medio
            (150, 255, 150),  # Verde pastel
        ])
        self.vida = random.uniform(4, 8)
        self.vida_max = self.vida
        self.oscilacion = random.uniform(0, math.pi * 2)

    def actualizar(self, dt):
        # Movimiento con oscilación (como burbujas reales)
        self.oscilacion += dt * 2
        self.x += self.velocidad_x * dt + math.sin(self.oscilacion) * 10 * dt
        self.y += self.velocidad_y * dt
        self.vida -= dt

        # Fade out gradual
        self.alpha = int(255 * (self.vida / self.vida_max))

        return self.vida > 0 and -50 < self.x < self.ancho_pantalla + 50 and -50 < self.y < self.alto_pantalla + 50


class MoleculaADN:
    """Partículas que forman una cadena de ADN decorativa"""

    def __init__(self, x, y, lado, offset_tiempo):
        self.x_base = x
        self.y = y
        self.lado = lado  # 'izquierdo' o 'derecho'
        self.offset_tiempo = offset_tiempo
        self.tamaño = 4
        self.color = (0, 255, 100) if lado == 'izquierdo' else (100, 255, 0)

    def actualizar(self, dt, tiempo_total):
        pass

    def obtener_posicion(self, tiempo_total):
        # Movimiento helicoidal
        t = tiempo_total + self.offset_tiempo
        offset_x = math.sin(t * 2) * 30
        if self.lado == 'derecho':
            offset_x = -offset_x
        return self.x_base + offset_x, self.y


class Titulo(Estado):
    """Pantalla de título con animación"""

    def __init__(self, juego):
        Estado.__init__(self, juego)

        # Animación de fade
        self.alpha = 0
        self.fade_speed = 120
        self.fade_in = True
        self.tiempo_espera = 5.0
        self.timer = 0

        # Parpadeo del texto "Press ENTER"
        self.blink_timer = 0
        self.mostrar_texto = True

        # Sistema de burbujas de laboratorio
        self.burbujas = []
        self.spawn_timer = 0
        self.spawn_rate = 0.08  # Más burbujas para ambiente de laboratorio

        # Animación del título (escala y pulsación como ser vivo)
        self.titulo_offset_y = 0
        self.titulo_scale = 0.3
        self.titulo_pulse = 1.0
        self.tiempo_total = 0

        # Cadenas de ADN decorativas a los lados
        self.moleculas_adn = []
        margen = 150
        for i in range(8):
            y = 100 + i * 60
            self.moleculas_adn.append(MoleculaADN(margen, y, 'izquierdo', i * 0.5))
            self.moleculas_adn.append(MoleculaADN(self.juego.ancho - margen, y, 'derecho', i * 0.5))

        # Efecto de líquido tóxico del fondo
        self.onda_toxica_timer = 0
        self.ondas_toxicas = []

        # Pantalla de laboratorio con escaneo
        self.escaneo_y = 0
        self.escaneo_velocidad = 100

    def actualizar(self, dt, acciones):
        self.tiempo_total += dt

        # Fade in
        if self.fade_in:
            self.alpha = min(255, self.alpha + self.fade_speed * dt)
            if self.alpha >= 255:
                self.fade_in = False
                self.timer = 0
        else:
            self.timer += dt

        # Animación de escala del título (zoom in inicial con efecto de "nacimiento")
        if self.titulo_scale < 1.0:
            self.titulo_scale = min(1.0, self.titulo_scale + dt * 2.0)

        # Pulsación del título como si estuviera vivo (efecto Blub)
        self.titulo_pulse = 1.0 + math.sin(self.tiempo_total * 3) * 0.03

        # Flotación suave del título
        self.titulo_offset_y = math.sin(self.tiempo_total * 1.5) * 8

        # Sistema de burbujas de experimento
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0
            # Spawn desde abajo (como si salieran de tubos de ensayo)
            x = random.randint(0, self.juego.ancho)
            y = self.juego.alto + 10
            self.burbujas.append(BurbujaExperimento(x, y, self.juego.ancho, self.juego.alto))

        # Actualizar burbujas
        self.burbujas = [b for b in self.burbujas if b.actualizar(dt)]

        # Efecto de ondas tóxicas
        self.onda_toxica_timer += dt
        if self.onda_toxica_timer >= 3.0 and not self.fade_in:
            self.onda_toxica_timer = 0
            self.ondas_toxicas.append({
                'radio': 0,
                'alpha': 180,
                'centro': (random.randint(100, self.juego.ancho - 100),
                           random.randint(100, self.juego.alto - 100))
            })

        # Actualizar ondas tóxicas
        nuevas_ondas = []
        for onda in self.ondas_toxicas:
            onda['radio'] += dt * 150
            onda['alpha'] = max(0, onda['alpha'] - dt * 100)
            if onda['alpha'] > 0 and onda['radio'] < 300:
                nuevas_ondas.append(onda)
        self.ondas_toxicas = nuevas_ondas

        # Línea de escaneo de laboratorio
        self.escaneo_y += self.escaneo_velocidad * dt
        if self.escaneo_y > self.juego.alto:
            self.escaneo_y = 0

        # Actualizar moléculas de ADN
        for molecula in self.moleculas_adn:
            molecula.actualizar(dt, self.tiempo_total)

        # Parpadeo del texto
        self.blink_timer += dt
        if self.blink_timer >= 0.5:
            self.mostrar_texto = not self.mostrar_texto
            self.blink_timer = 0

        # Saltar al menú con ENTER
        if acciones.get("enter"):
            from estados.menu_principal import MenuPrincipal
            MenuPrincipal(self.juego).entrar_estado()
            self.juego.reset_keys()

        # Auto-avanzar después de tiempo de espera
        if self.timer >= self.tiempo_espera and not self.fade_in:
            from estados.menu_principal import MenuPrincipal
            MenuPrincipal(self.juego).entrar_estado()

    def dibujar(self, pantalla):
        # Fondo degradado con tonos de laboratorio (verde oscuro a negro)
        for y in range(pantalla.get_height()):
            ratio = y / pantalla.get_height()
            # Verde oscuro de laboratorio con ligera variación
            offset = math.sin(self.tiempo_total * 0.3 + ratio * 3) * 5
            color = (
                int(5 + ratio * 15 + offset),
                int(20 + ratio * 25 + offset),
                int(10 + ratio * 15 + offset * 0.5)
            )
            pygame.draw.line(pantalla, color, (0, y), (pantalla.get_width(), y))

        # Línea de escaneo de laboratorio (efecto terminal científico)
        if not self.fade_in:
            scan_surface = pygame.Surface((pantalla.get_width(), 3), pygame.SRCALPHA)
            scan_color = (0, 255, 100, 150)
            pygame.draw.rect(scan_surface, scan_color, (0, 0, pantalla.get_width(), 3))
            pantalla.blit(scan_surface, (0, int(self.escaneo_y)))

            # Estela de la línea de escaneo
            for i in range(10):
                alpha = int(80 * (1 - i / 10))
                estela_surface = pygame.Surface((pantalla.get_width(), 2), pygame.SRCALPHA)
                estela_color = (0, 255, 100, alpha)
                pygame.draw.rect(estela_surface, estela_color, (0, 0, pantalla.get_width(), 2))
                pantalla.blit(estela_surface, (0, int(self.escaneo_y - i * 3)))

        # Dibujar cadenas de ADN a los lados
        for i, molecula in enumerate(self.moleculas_adn):
            x, y = molecula.obtener_posicion(self.tiempo_total)

            # Dibujar la molécula
            surface = pygame.Surface((molecula.tamaño * 3, molecula.tamaño * 3), pygame.SRCALPHA)
            alpha = int(self.alpha * 0.6)
            color_con_alpha = (*molecula.color, alpha)
            pygame.draw.circle(surface, color_con_alpha, (molecula.tamaño * 1.5, molecula.tamaño * 1.5),
                               molecula.tamaño)
            pantalla.blit(surface, (int(x - molecula.tamaño * 1.5), int(y - molecula.tamaño * 1.5)))

            # Conectar moléculas con líneas (efecto de doble hélice)
            if i % 2 == 0 and i + 1 < len(self.moleculas_adn):
                molecula_par = self.moleculas_adn[i + 1]
                x2, y2 = molecula_par.obtener_posicion(self.tiempo_total)
                line_surface = pygame.Surface((pantalla.get_width(), pantalla.get_height()), pygame.SRCALPHA)
                line_color = (0, 200, 50, int(alpha * 0.5))
                pygame.draw.line(line_surface, line_color, (int(x), int(y)), (int(x2), int(y2)), 2)
                pantalla.blit(line_surface, (0, 0))

        # Dibujar burbujas de experimento
        for burbuja in self.burbujas:
            # Burbuja principal
            surface = pygame.Surface((burbuja.tamaño * 3, burbuja.tamaño * 3), pygame.SRCALPHA)
            color_con_alpha = (*burbuja.color, burbuja.alpha)
            pygame.draw.circle(surface, color_con_alpha, (burbuja.tamaño * 1.5, burbuja.tamaño * 1.5), burbuja.tamaño)

            # Borde más oscuro de la burbuja
            borde_color = (int(burbuja.color[0] * 0.5), int(burbuja.color[1] * 0.5), int(burbuja.color[2] * 0.5),
                           burbuja.alpha)
            pygame.draw.circle(surface, borde_color, (burbuja.tamaño * 1.5, burbuja.tamaño * 1.5), burbuja.tamaño, 1)

            # Reflejo de luz en la burbuja (efecto líquido)
            if burbuja.tamaño > 4:
                reflejo_color = (255, 255, 255, min(200, burbuja.alpha))
                reflejo_pos = (int(burbuja.tamaño * 1.2), int(burbuja.tamaño * 1.2))
                pygame.draw.circle(surface, reflejo_color, reflejo_pos, max(2, burbuja.tamaño // 3))

            pantalla.blit(surface, (int(burbuja.x - burbuja.tamaño * 1.5), int(burbuja.y - burbuja.tamaño * 1.5)))

        # Dibujar ondas tóxicas
        for onda in self.ondas_toxicas:
            if onda['alpha'] > 0:
                surface = pygame.Surface((pantalla.get_width(), pantalla.get_height()), pygame.SRCALPHA)
                color = (50, 255, 50, int(onda['alpha']))
                pygame.draw.circle(surface, color, onda['centro'], int(onda['radio']), 2)
                # Onda interna más brillante
                color_interna = (100, 255, 100, int(onda['alpha'] * 0.5))
                pygame.draw.circle(surface, color_interna, onda['centro'], int(onda['radio'] * 0.8), 1)
                pantalla.blit(surface, (0, 0))

        # Título con escala, pulsación y fade
        titulo_original = self.juego.fonts.big.render("GILBERTOV EVIL", False, (50, 255, 50))

        # Aplicar escala y pulsación
        escala_final = self.titulo_scale * self.titulo_pulse
        nuevo_ancho = int(titulo_original.get_width() * escala_final)
        nuevo_alto = int(titulo_original.get_height() * escala_final)
        titulo_escalado = pygame.transform.scale(titulo_original, (nuevo_ancho, nuevo_alto))

        titulo_surface = pygame.Surface(titulo_escalado.get_size(), pygame.SRCALPHA)
        titulo_surface.blit(titulo_escalado, (0, 0))
        titulo_surface.set_alpha(int(self.alpha))

        # Posición con flotación
        pos_y = self.juego.alto // 2 - 50 + self.titulo_offset_y
        titulo_rect = titulo_surface.get_rect(center=(self.juego.ancho // 2, pos_y))

        # Sombra verde tóxica con múltiples capas
        if self.alpha > 100:
            for i in range(3, 0, -1):
                sombra = self.juego.fonts.big.render("GILBERTOV EVIL", False, (0, 150, 0))
                sombra_escalada = pygame.transform.scale(sombra, (nuevo_ancho, nuevo_alto))
                sombra_surface = pygame.Surface(sombra_escalada.get_size(), pygame.SRCALPHA)
                sombra_surface.blit(sombra_escalada, (0, 0))
                sombra_surface.set_alpha(int(self.alpha * 0.4 / i))
                offset = i * 3
                sombra_rect = sombra_surface.get_rect(center=(self.juego.ancho // 2 + offset, pos_y + offset))
                pantalla.blit(sombra_surface, sombra_rect)

        # Resplandor verde tóxico detrás del título (efecto radiactivo)
        if not self.fade_in and self.alpha >= 255:
            brillo_size = int(max(nuevo_ancho, nuevo_alto) * 1.8)
            brillo_surface = pygame.Surface((brillo_size, brillo_size), pygame.SRCALPHA)
            brillo_alpha = int(40 + math.sin(self.tiempo_total * 4) * 25)

            # Degradado radial verde tóxico
            for radio in range(brillo_size // 2, 0, -8):
                alpha = int(brillo_alpha * (radio / (brillo_size // 2)))
                color = (50, 255, 50, alpha)
                pygame.draw.circle(brillo_surface, color, (brillo_size // 2, brillo_size // 2), radio)

            brillo_rect = brillo_surface.get_rect(center=(self.juego.ancho // 2, pos_y))
            pantalla.blit(brillo_surface, brillo_rect)

        pantalla.blit(titulo_surface, titulo_rect)

        # Texto "Presiona ENTER" parpadeante con efecto de terminal
        if not self.fade_in and self.timer > 0.5 and self.mostrar_texto:
            # Efecto de brillo verde pulsante
            brillo_alpha = int(120 + math.sin(self.tiempo_total * 6) * 80)

            subtitulo = self.juego.fonts.medium.render("Presiona ENTER", False, (200, 255, 200))
            subtitulo_rect = subtitulo.get_rect(center=(self.juego.ancho // 2, self.juego.alto // 2 + 80))

            # Sombra verde brillante
            sombra_sub = self.juego.fonts.medium.render("Presiona ENTER", False, (0, 255, 0))
            sombra_sub_surface = pygame.Surface(sombra_sub.get_size(), pygame.SRCALPHA)
            sombra_sub_surface.blit(sombra_sub, (0, 0))
            sombra_sub_surface.set_alpha(brillo_alpha)

            # Múltiples capas de brillo
            for offset in [4, 2]:
                sombra_rect = sombra_sub_surface.get_rect(
                    center=(self.juego.ancho // 2 + offset, self.juego.alto // 2 + 80 + offset))
                pantalla.blit(sombra_sub_surface, sombra_rect)

            # Texto principal
            pantalla.blit(subtitulo, subtitulo_rect)

        # Subtítulo adicional (nombre del experimento)
        if not self.fade_in and self.alpha >= 255:
            experimento_text = self.juego.fonts.small.render("Experimento: Estudiante Perfecto", False, (100, 200, 100))
            experimento_alpha = int(180 + math.sin(self.tiempo_total * 2) * 40)
            experimento_surface = pygame.Surface(experimento_text.get_size(), pygame.SRCALPHA)
            experimento_surface.blit(experimento_text, (0, 0))
            experimento_surface.set_alpha(experimento_alpha)
            experimento_rect = experimento_surface.get_rect(center=(self.juego.ancho // 2, self.juego.alto // 2 + 20))
            pantalla.blit(experimento_surface, experimento_rect)

        # Efecto de viñeta verde en los bordes (ambiente de laboratorio)
        vignette = pygame.Surface((pantalla.get_width(), pantalla.get_height()), pygame.SRCALPHA)
        for i in range(80):
            alpha = int(i * 1.2)
            color = (0, 50, 0, alpha)
            pygame.draw.rect(vignette, color, (i, i, pantalla.get_width() - i * 2, pantalla.get_height() - i * 2), 1)
        pantalla.blit(vignette, (0, 0))

        # Overlay de escaneo general (líneas horizontales sutiles estilo CRT)
        if not self.fade_in:
            scanlines = pygame.Surface((pantalla.get_width(), pantalla.get_height()), pygame.SRCALPHA)
            for y in range(0, pantalla.get_height(), 4):
                pygame.draw.line(scanlines, (0, 50, 0, 30), (0, y), (pantalla.get_width(), y), 1)
            pantalla.blit(scanlines, (0, 0))