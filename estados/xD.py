from estados.estado import Estado
import pygame
import random
import math
import colorsys


class ParticularCaotica:
    """Partícula con física compleja y comportamiento caótico"""

    def __init__(self, x, y, tipo, ancho, alto):
        self.x = x
        self.y = y
        self.tipo = tipo  # 'explosion', 'orbital', 'helix', 'vortex', 'quantum'
        self.ancho = ancho
        self.alto = alto

        # Física
        self.vx = random.uniform(-100, 100)
        self.vy = random.uniform(-100, 100)
        self.ax = 0
        self.ay = 0
        self.friccion = 0.98

        # Propiedades visuales
        self.tamaño = random.uniform(1, 8)
        self.tamaño_original = self.tamaño
        self.vida = random.uniform(2, 6)
        self.vida_max = self.vida
        self.rotacion = random.uniform(0, math.pi * 2)
        self.velocidad_rotacion = random.uniform(-3, 3)

        # Color dinámico basado en HSV
        self.hue = random.uniform(0, 1)
        self.sat = random.uniform(0.6, 1.0)
        self.val = random.uniform(0.7, 1.0)

        # Comportamiento específico del tipo
        self.angulo = random.uniform(0, math.pi * 2)
        self.radio = random.uniform(50, 200)
        self.velocidad_angular = random.uniform(1, 3)
        self.fase = random.uniform(0, math.pi * 2)

        # Estela
        self.trail = []
        self.max_trail = 15

    def actualizar(self, dt, tiempo_total, centro_x, centro_y):
        # Comportamientos según tipo
        if self.tipo == 'orbital':
            # Órbita alrededor del centro con cambio de radio
            self.angulo += self.velocidad_angular * dt
            self.radio += math.sin(tiempo_total * 2 + self.fase) * 20 * dt
            self.x = centro_x + math.cos(self.angulo) * self.radio
            self.y = centro_y + math.sin(self.angulo) * self.radio

        elif self.tipo == 'helix':
            # Hélice 3D simulada
            self.angulo += self.velocidad_angular * dt * 2
            z_offset = math.sin(tiempo_total * 3 + self.fase) * 100
            escala = 1 + z_offset / 200
            self.x = centro_x + math.cos(self.angulo) * self.radio * escala
            self.y = centro_y + math.sin(self.angulo) * self.radio * 0.5 * escala + z_offset
            self.tamaño = self.tamaño_original * escala

        elif self.tipo == 'vortex':
            # Vórtice que se contrae hacia el centro
            dx = centro_x - self.x
            dy = centro_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 10:
                self.ax = (dx / dist) * 150 + dy * 0.5
                self.ay = (dy / dist) * 150 - dx * 0.5
            self.vx += self.ax * dt
            self.vy += self.ay * dt
            self.vx *= self.friccion
            self.vy *= self.friccion
            self.x += self.vx * dt
            self.y += self.vy * dt

        elif self.tipo == 'quantum':
            # Teletransportación cuántica
            if random.random() < 0.02:
                self.x = random.uniform(0, self.ancho)
                self.y = random.uniform(0, self.alto)
            else:
                self.vx += random.uniform(-50, 50) * dt
                self.vy += random.uniform(-50, 50) * dt
                self.vx *= 0.95
                self.vy *= 0.95
                self.x += self.vx * dt
                self.y += self.vy * dt

        elif self.tipo == 'explosion':
            # Movimiento balístico con gravedad
            self.vy += 200 * dt  # Gravedad
            self.vx *= self.friccion
            self.vy *= self.friccion
            self.x += self.vx * dt
            self.y += self.vy * dt

        # Actualizar trail
        self.trail.append((self.x, self.y, self.tamaño))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        # Actualizar color con efecto arcoíris
        self.hue = (self.hue + dt * 0.3) % 1.0

        # Rotación
        self.rotacion += self.velocidad_rotacion * dt

        # Vida
        self.vida -= dt

        return self.vida > 0


class FragmentoLogoExplosivo:
    """Fragmento del logo que explota y se reconstruye"""

    def __init__(self, x, y, fragmento_id, centro_x, centro_y):
        self.x_objetivo = x
        self.y_objetivo = y
        self.x = centro_x + random.uniform(-50, 50)
        self.y = centro_y + random.uniform(-50, 50)
        self.fragmento_id = fragmento_id

        # Física de explosión
        angulo = random.uniform(0, math.pi * 2)
        velocidad = random.uniform(200, 400)
        self.vx = math.cos(angulo) * velocidad
        self.vy = math.sin(angulo) * velocidad
        self.rotacion = random.uniform(0, math.pi * 2)
        self.velocidad_rotacion = random.uniform(-5, 5)

        # Estado
        self.fase = 'explosion'  # 'explosion', 'reconstruccion', 'final'
        self.timer = 0
        self.alpha = 255
        self.escala = 0.5


class OndaShockwave:
    """Onda de choque expansiva con distorsión"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radio = 0
        self.grosor = 20
        self.alpha = 255
        self.velocidad = 400
        self.color_hue = random.uniform(0, 1)


class RayoElectrico:
    """Rayo eléctrico entre dos puntos con ramificaciones"""

    def __init__(self, x1, y1, x2, y2):
        self.puntos = self.generar_rayo(x1, y1, x2, y2, 5)
        self.alpha = 255
        self.vida = 0.3
        self.grosor = random.uniform(2, 5)

    def generar_rayo(self, x1, y1, x2, y2, detalle):
        if detalle == 0:
            return [(x1, y1), (x2, y2)]

        mid_x = (x1 + x2) / 2 + random.uniform(-30, 30)
        mid_y = (y1 + y2) / 2 + random.uniform(-30, 30)

        return (self.generar_rayo(x1, y1, mid_x, mid_y, detalle - 1) +
                self.generar_rayo(mid_x, mid_y, x2, y2, detalle - 1))


class Titulo(Estado):
    """Pantalla de título con la intro más ÉPICA y compleja jamás creada"""

    def __init__(self, juego):
        Estado.__init__(self, juego)

        self.tiempo_total = 0
        self.fase_actual = 0  # 0: blackout, 1: big_bang, 2: caos, 3: formacion, 4: final
        self.duracion_fases = [0.5, 2.0, 3.0, 2.5, 999]
        self.timer_fase = 0

        # Sistemas de partículas múltiples
        self.particulas = []
        self.fragmentos_logo = []
        self.ondas_shock = []
        self.rayos = []

        # Efectos de fondo
        self.campo_distorsion = []
        self.vortices = []

        # Camera shake
        self.shake_intensidad = 0
        self.shake_x = 0
        self.shake_y = 0

        # Flash effects
        self.flash_alpha = 0
        self.flash_color = (255, 255, 255)

        # Glitch effect
        self.glitch_activo = False
        self.glitch_timer = 0
        self.glitch_offset = 0

        # Zoom cinematográfico
        self.zoom = 0.1
        self.zoom_objetivo = 1.0

        # Rotación 3D simulada del espacio
        self.rotacion_espacio = 0

        # Chromatic aberration
        self.aberracion_intensidad = 0

        # Texto
        self.alpha_texto = 0
        self.texto_offset_y = 100

        # Partículas de fondo continuas
        self.particulas_ambiente = []

        # Grid de matriz (efecto Matrix)
        self.matrix_drops = []
        for i in range(50):
            self.matrix_drops.append({
                'x': random.randint(0, self.juego.ancho),
                'y': random.randint(-500, 0),
                'velocidad': random.uniform(100, 300),
                'chars': [chr(random.randint(33, 126)) for _ in range(20)]
            })

    def iniciar_fase(self, fase):
        """Inicializar efectos de cada fase"""
        centro_x = self.juego.ancho // 2
        centro_y = self.juego.alto // 2

        if fase == 1:  # BIG BANG
            # Explosión masiva de partículas desde el centro
            for _ in range(200):
                tipo = random.choice(['explosion', 'orbital', 'vortex'])
                self.particulas.append(ParticularCaotica(centro_x, centro_y, tipo,
                                                         self.juego.ancho, self.juego.alto))

            # Ondas de choque
            for i in range(5):
                self.ondas_shock.append(OndaShockwave(centro_x, centro_y))

            # Camera shake intenso
            self.shake_intensidad = 20
            self.flash_alpha = 255
            self.aberracion_intensidad = 15

        elif fase == 2:  # CAOS
            # Añadir más partículas de diferentes tipos
            for _ in range(150):
                tipo = random.choice(['helix', 'quantum', 'vortex', 'orbital'])
                x = random.uniform(0, self.juego.ancho)
                y = random.uniform(0, self.juego.alto)
                self.particulas.append(ParticularCaotica(x, y, tipo,
                                                         self.juego.ancho, self.juego.alto))

            # Rayos eléctricos aleatorios
            for _ in range(10):
                x1, y1 = random.uniform(0, self.juego.ancho), random.uniform(0, self.juego.alto)
                x2, y2 = random.uniform(0, self.juego.ancho), random.uniform(0, self.juego.alto)
                self.rayos.append(RayoElectrico(x1, y1, x2, y2))

            self.glitch_activo = True

        elif fase == 3:  # FORMACIÓN
            # Crear fragmentos del logo que se ensamblan
            self.particulas.clear()  # Limpiar partículas anteriores

            # Generar grid de fragmentos que formarán el texto
            texto = "GILBERTOV EVIL"
            for i, char in enumerate(texto):
                x = 200 + i * 40
                for j in range(3):
                    y = centro_y - 20 + j * 20
                    self.fragmentos_logo.append(FragmentoLogoExplosivo(x, y, i, centro_x, centro_y))

            # Vórtice que atrae todo
            for _ in range(100):
                x = random.uniform(0, self.juego.ancho)
                y = random.uniform(0, self.juego.alto)
                self.particulas.append(ParticularCaotica(x, y, 'vortex',
                                                         self.juego.ancho, self.juego.alto))

        elif fase == 4:  # FINAL
            # Efecto final estabilizado
            self.zoom_objetivo = 1.0
            self.glitch_activo = False

    def actualizar(self, dt, acciones):
        self.tiempo_total += dt
        self.timer_fase += dt

        # Cambio de fase
        if self.timer_fase >= self.duracion_fases[self.fase_actual]:
            self.fase_actual += 1
            if self.fase_actual < len(self.duracion_fases):
                self.iniciar_fase(self.fase_actual)
                self.timer_fase = 0

        centro_x = self.juego.ancho // 2
        centro_y = self.juego.alto // 2

        # Actualizar partículas
        self.particulas = [p for p in self.particulas if p.actualizar(dt, self.tiempo_total, centro_x, centro_y)]

        # Actualizar fragmentos del logo
        for fragmento in self.fragmentos_logo:
            fragmento.timer += dt

            if fragmento.fase == 'explosion' and fragmento.timer > 0.5:
                fragmento.fase = 'reconstruccion'

            if fragmento.fase == 'explosion':
                fragmento.x += fragmento.vx * dt
                fragmento.y += fragmento.vy * dt
                fragmento.vy += 500 * dt  # Gravedad
                fragmento.rotacion += fragmento.velocidad_rotacion * dt
                fragmento.escala = max(0.1, fragmento.escala - dt * 0.5)

            elif fragmento.fase == 'reconstruccion':
                # Interpolación suave hacia la posición objetivo
                dx = fragmento.x_objetivo - fragmento.x
                dy = fragmento.y_objetivo - fragmento.y
                fragmento.x += dx * dt * 3
                fragmento.y += dy * dt * 3
                fragmento.rotacion += (0 - fragmento.rotacion) * dt * 5
                fragmento.escala = min(1.0, fragmento.escala + dt * 2)

                if abs(dx) < 5 and abs(dy) < 5:
                    fragmento.fase = 'final'

        # Actualizar ondas de choque
        nuevas_ondas = []
        for onda in self.ondas_shock:
            onda.radio += onda.velocidad * dt
            onda.alpha = max(0, onda.alpha - 300 * dt)
            onda.grosor = max(1, onda.grosor - 10 * dt)
            if onda.alpha > 0:
                nuevas_ondas.append(onda)
        self.ondas_shock = nuevas_ondas

        # Actualizar rayos
        nuevos_rayos = []
        for rayo in self.rayos:
            rayo.vida -= dt
            rayo.alpha = max(0, int(255 * (rayo.vida / 0.3)))
            if rayo.vida > 0:
                nuevos_rayos.append(rayo)
        self.rayos = nuevos_rayos

        # Generar nuevos rayos en fase de caos
        if self.fase_actual == 2 and random.random() < 0.1:
            x1, y1 = random.uniform(0, self.juego.ancho), random.uniform(0, self.juego.alto)
            x2, y2 = centro_x, centro_y
            self.rayos.append(RayoElectrico(x1, y1, x2, y2))

        # Camera shake
        self.shake_intensidad = max(0, self.shake_intensidad - 50 * dt)
        if self.shake_intensidad > 0:
            self.shake_x = random.uniform(-self.shake_intensidad, self.shake_intensidad)
            self.shake_y = random.uniform(-self.shake_intensidad, self.shake_intensidad)
        else:
            self.shake_x = 0
            self.shake_y = 0

        # Flash
        self.flash_alpha = max(0, self.flash_alpha - 500 * dt)

        # Glitch
        if self.glitch_activo:
            self.glitch_timer += dt
            if self.glitch_timer > 0.1:
                self.glitch_offset = random.uniform(-10, 10)
                self.glitch_timer = 0

        # Zoom
        self.zoom += (self.zoom_objetivo - self.zoom) * dt * 2

        # Chromatic aberration
        self.aberracion_intensidad = max(0, self.aberracion_intensidad - 20 * dt)

        # Rotación del espacio
        self.rotacion_espacio += dt * 0.5

        # Alpha del texto final
        if self.fase_actual >= 3:
            self.alpha_texto = min(255, self.alpha_texto + 150 * dt)
            self.texto_offset_y = max(0, self.texto_offset_y - 100 * dt)

        # Matrix effect
        for drop in self.matrix_drops:
            drop['y'] += drop['velocidad'] * dt
            if drop['y'] > self.juego.alto + 200:
                drop['y'] = random.randint(-200, 0)
                drop['x'] = random.randint(0, self.juego.ancho)

        # Salir con ENTER (solo en fase final)
        if acciones.get("enter") and self.fase_actual >= 4:
            from estados.menu_principal import MenuPrincipal
            MenuPrincipal(self.juego).entrar_estado()
            self.juego.reset_keys()

    def dibujar(self, pantalla):
        # Limpiar pantalla con color base
        pantalla.fill((0, 0, 0))

        # Crear surface para efectos
        effect_surface = pygame.Surface((self.juego.ancho, self.juego.alto), pygame.SRCALPHA)

        # === FASE 0: BLACKOUT ===
        if self.fase_actual == 0:
            # Solo negro
            pass

        # === EFECTOS DE FONDO CONTINUO ===

        # Matrix rain (muy sutil en el fondo)
        if self.fase_actual >= 1:
            for drop in self.matrix_drops:
                for i, char in enumerate(drop['chars']):
                    y = drop['y'] - i * 15
                    if 0 < y < self.juego.alto:
                        alpha = int(100 * (1 - i / len(drop['chars'])))
                        color = (0, 255, 0, alpha)
                        try:
                            char_surf = self.juego.fonts.small.render(char, False, (0, 255, 0))
                            char_surf.set_alpha(alpha)
                            effect_surface.blit(char_surf, (int(drop['x']), int(y)))
                        except:
                            pass

        # Grid 3D de fondo (perspectiva)
        if self.fase_actual >= 2:
            for i in range(10):
                for j in range(10):
                    # Simular profundidad con escala
                    z = i / 10
                    escala = 0.5 + z * 0.5
                    x = int(self.juego.ancho * (j / 10) * escala + self.juego.ancho * (1 - escala) / 2)
                    y = int(self.juego.alto * (i / 10) * escala + self.juego.alto * (1 - escala) / 2)

                    color = (0, int(50 * z), int(100 * z), int(50 * z))
                    pygame.draw.circle(effect_surface, color, (x, y), int(2 * escala))

        # === DIBUJAR ONDAS DE CHOQUE ===
        for onda in self.ondas_shock:
            r, g, b = colorsys.hsv_to_rgb(onda.color_hue, 1.0, 1.0)
            for i in range(3):
                radio_actual = int(onda.radio - i * 5)
                if radio_actual > 0:
                    alpha = int(onda.alpha * (1 - i / 3))
                    color = (int(r * 255), int(g * 255), int(b * 255), alpha)
                    pygame.draw.circle(effect_surface, color,
                                       (int(onda.x + self.shake_x), int(onda.y + self.shake_y)),
                                       radio_actual, int(onda.grosor))

        # === DIBUJAR RAYOS ELÉCTRICOS ===
        for rayo in self.rayos:
            for i in range(len(rayo.puntos) - 1):
                x1, y1 = rayo.puntos[i]
                x2, y2 = rayo.puntos[i + 1]

                # Rayo principal
                pygame.draw.line(effect_surface, (150, 200, 255, rayo.alpha),
                                 (int(x1 + self.shake_x), int(y1 + self.shake_y)),
                                 (int(x2 + self.shake_x), int(y2 + self.shake_y)),
                                 int(rayo.grosor))

                # Glow
                if rayo.alpha > 100:
                    pygame.draw.line(effect_surface, (200, 230, 255, rayo.alpha // 2),
                                     (int(x1 + self.shake_x), int(y1 + self.shake_y)),
                                     (int(x2 + self.shake_x), int(y2 + self.shake_y)),
                                     int(rayo.grosor * 2))

        # === DIBUJAR PARTÍCULAS CON TRAILS ===
        for particula in self.particulas:
            # Dibujar trail
            for i, (tx, ty, ts) in enumerate(particula.trail):
                alpha = int(255 * (i / len(particula.trail)) * (particula.vida / particula.vida_max))
                r, g, b = colorsys.hsv_to_rgb(particula.hue, particula.sat, particula.val)
                color = (int(r * 255), int(g * 255), int(b * 255), alpha)

                tamaño_trail = max(1, int(ts * (i / len(particula.trail))))
                pygame.draw.circle(effect_surface, color,
                                   (int(tx + self.shake_x), int(ty + self.shake_y)),
                                   tamaño_trail)

            # Dibujar partícula principal
            alpha = int(255 * (particula.vida / particula.vida_max))
            r, g, b = colorsys.hsv_to_rgb(particula.hue, particula.sat, particula.val)

            # Núcleo brillante
            pygame.draw.circle(effect_surface, (int(r * 255), int(g * 255), int(b * 255), alpha),
                               (int(particula.x + self.shake_x), int(particula.y + self.shake_y)),
                               int(particula.tamaño))

            # Glow exterior
            if particula.tamaño > 3:
                pygame.draw.circle(effect_surface, (int(r * 255), int(g * 255), int(b * 255), alpha // 2),
                                   (int(particula.x + self.shake_x), int(particula.y + self.shake_y)),
                                   int(particula.tamaño * 2))

        # === DIBUJAR FRAGMENTOS DEL LOGO ===
        for fragmento in self.fragmentos_logo:
            # Crear surface rotada para el fragmento
            frag_size = int(30 * fragmento.escala)
            if frag_size > 0:
                frag_surf = pygame.Surface((frag_size, frag_size), pygame.SRCALPHA)

                # Color según el fragmento
                r, g, b = colorsys.hsv_to_rgb((fragmento.fragmento_id * 0.1) % 1.0, 0.8, 1.0)
                color = (int(r * 255), int(g * 255), int(b * 255), int(fragmento.alpha))

                # Dibujar forma del fragmento (rectángulo girado)
                pygame.draw.rect(frag_surf, color, (0, 0, frag_size, frag_size))

                # Rotar
                frag_rotada = pygame.transform.rotate(frag_surf, math.degrees(fragmento.rotacion))
                rect = frag_rotada.get_rect(center=(int(fragmento.x + self.shake_x),
                                                    int(fragmento.y + self.shake_y)))

                effect_surface.blit(frag_rotada, rect)

        # Aplicar surface de efectos a pantalla
        pantalla.blit(effect_surface, (0, 0))

        # === TEXTO PRINCIPAL ===
        if self.fase_actual >= 3:
            # Título principal con múltiples capas de efecto
            texto_grande = self.juego.fonts.big.render("GILBERTOV EVIL", False, (0, 255, 100))

            # Aplicar zoom
            w = int(texto_grande.get_width() * self.zoom)
            h = int(texto_grande.get_height() * self.zoom)
            if w > 0 and h > 0:
                texto_escalado = pygame.transform.scale(texto_grande, (w, h))
                texto_surface = pygame.Surface(texto_escalado.get_size(), pygame.SRCALPHA)
                texto_surface.blit(texto_escalado, (0, 0))
                texto_surface.set_alpha(int(self.alpha_texto))

                # Posición central con offset
                centro_x = self.juego.ancho // 2
                centro_y = self.juego.alto // 2 + self.texto_offset_y

                # Chromatic aberration
                if self.aberracion_intensidad > 0:
                    # Canal rojo
                    texto_r = pygame.transform.scale(texto_grande, (w, h))
                    surf_r = pygame.Surface((w, h), pygame.SRCALPHA)
                    surf_r.blit(texto_r, (0, 0))
                    surf_r.set_alpha(int(self.alpha_texto * 0.7))
                    rect_r = surf_r.get_rect(center=(centro_x - self.aberracion_intensidad + self.shake_x,
                                                     centro_y + self.shake_y))
                    pantalla.blit(surf_r, rect_r)

                    # Canal azul
                    texto_b = pygame.transform.scale(texto_grande, (w, h))
                    surf_b = pygame.Surface((w, h), pygame.SRCALPHA)
                    surf_b.blit(texto_b, (0, 0))
                    surf_b.set_alpha(int(self.alpha_texto * 0.7))
                    rect_b = surf_b.get_rect(center=(centro_x + self.aberracion_intensidad + self.shake_x,
                                                     centro_y + self.shake_y))
                    pantalla.blit(surf_b, rect_b)

                # Sombras múltiples
                for i in range(5, 0, -1):
                    sombra = pygame.transform.scale(texto_grande, (w, h))
                    sombra_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                    sombra_surf.blit(sombra, (0, 0))
                    sombra_surf.set_alpha(int(self.alpha_texto * 0.2))
                    sombra_rect = sombra_surf.get_rect(center=(centro_x + i * 2 + self.shake_x,
                                                               centro_y + i * 2 + self.shake_y))
                    pantalla.blit(sombra_surf, sombra_rect)

                # Texto principal
                texto_rect = texto_surface.get_rect(center=(centro_x + self.shake_x,
                                                            centro_y + self.shake_y))
                pantalla.blit(texto_surface, texto_rect)

                # Glow pulsante
                if self.fase_actual == 4:
                    glow_alpha = int(100 + math.sin(self.tiempo_total * 5) * 80)
                    glow_surf = pygame.Surface((w + 40, h + 40), pygame.SRCALPHA)
                    for r in range(20, 0, -2):
                        alpha = int(glow_alpha * (r / 20))
                        pygame.draw.rect(glow_surf, (0, 255, 100, alpha),
                                         (20 - r, 20 - r, w + r * 2, h + r * 2), 2)
                    glow_rect = glow_surf.get_rect(center=(centro_x + self.shake_x,
                                                           centro_y + self.shake_y))
                    pantalla.blit(glow_surf, glow_rect)

        # === SUBTÍTULO ===
        if self.fase_actual == 4 and self.alpha_texto > 200:
            sub_text = self.juego.fonts.medium.render("Experimento: Estudiante Perfecto", False, (100, 255, 150))
            sub_alpha = int(self.alpha_texto * 0.8)
            sub_surface = pygame.Surface(sub_text.get_size(), pygame.SRCALPHA)
            sub_surface.blit(sub_text, (0, 0))
            sub_surface.set_alpha(sub_alpha)
            sub_rect = sub_surface.get_rect(center=(self.juego.ancho // 2 + self.shake_x,
                                                    self.juego.alto // 2 + 60 + self.shake_y))
            pantalla.blit(sub_surface, sub_rect)

            # "Presiona ENTER" parpadeante
            if math.sin(self.tiempo_total * 3) > 0:
                enter_text = self.juego.fonts.medium.render(">>> PRESIONA ENTER <<<", False, (255, 255, 0))
                enter_surface = pygame.Surface(enter_text.get_size(), pygame.SRCALPHA)
                enter_surface.blit(enter_text, (0, 0))
                enter_surface.set_alpha(int(200 + math.sin(self.tiempo_total * 10) * 55))
                enter_rect = enter_surface.get_rect(center=(self.juego.ancho // 2,
                                                            self.juego.alto // 2 + 120))
                pantalla.blit(enter_surface, enter_rect)

        # === FLASH BLANCO ===
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((self.juego.ancho, self.juego.alto), pygame.SRCALPHA)
            flash_surf.fill((*self.flash_color, int(self.flash_alpha)))
            pantalla.blit(flash_surf, (0, 0))

        # === EFECTO GLITCH ===
        if self.glitch_activo and random.random() < 0.3:
            # Cortar y desplazar líneas horizontales aleatoriamente
            for _ in range(5):
                y = random.randint(0, self.juego.alto - 50)
                altura = min(random.randint(5, 30), self.juego.alto - y)  # No exceder límites
                offset = random.randint(-20, 20)

                # Verificar que la sección está dentro de los límites
                if y >= 0 and y + altura <= self.juego.alto and altura > 0:
                    try:
                        # Copiar sección
                        seccion = pantalla.subsurface((0, y, self.juego.ancho, altura)).copy()
                        # Pegar desplazada
                        pantalla.blit(seccion, (offset, y))
                    except ValueError:
                        # Si hay error, simplemente continuar
                        pass

        # === SCANLINES CRT ===
        if self.fase_actual >= 2:
            scanlines = pygame.Surface((self.juego.ancho, self.juego.alto), pygame.SRCALPHA)
            for y in range(0, self.juego.alto, 3):
                alpha = 20 + int(10 * math.sin(self.tiempo_total * 2 + y * 0.1))
                pygame.draw.line(scanlines, (0, 0, 0, alpha), (0, y), (self.juego.ancho, y), 1)
            pantalla.blit(scanlines, (0, 0))

        # === VIÑETA FINAL ===
        vignette = pygame.Surface((self.juego.ancho, self.juego.alto), pygame.SRCALPHA)
        for i in range(150):
            alpha = int(i * 0.8)
            pygame.draw.rect(vignette, (0, 0, 0, alpha),
                             (i, i, self.juego.ancho - i * 2, self.juego.alto - i * 2), 1)
        pantalla.blit(vignette, (0, 0))