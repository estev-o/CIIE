import pygame

class Estado():
    def __init__(self, juego):
        self.juego = juego
        self.estado_prev= None
        self.enemies = pygame.sprite.Group()
        self.objects = pygame.sprite.Group()
        self.interactions = []

    def append_enemy(self, enemy):
        self.enemies.add(enemy)

    def actualizar(self, dt, acciones):
        pass

    def dibujar(self, pantalla):
        pass

    def entrar_estado(self):
        if len(self.juego.state_stack) > 0:
            self.estado_prev = self.juego.state_stack[-1]
        self.juego.state_stack.append(self)

    def salir_estado(self):
        self.juego.state_stack.pop()

    def append_interaction(self, interaction):
        self.interactions.append(interaction)

    def update_interactions(self, player, actions):
        for interaction in self.interactions:
            interaction.update(player, actions)

    def draw_interactions(self, screen):
        for interaction in self.interactions:
            interaction.draw(screen)

    def is_interaction_active(self):
        for interaction in self.interactions:
            if interaction.is_active():
                return True
            
        return False

    def iniciar_texto_nivel(self, nombre, duracion=3000):
        self._nivel_nombre = nombre.upper()
        self._nivel_duracion = duracion
        self._nivel_inicio = pygame.time.get_ticks()
        self._nivel_activo = True
        self._nivel_font = self.juego.fonts.level_title
    
    def dibujar_texto_nivel(self, pantalla):
        if not getattr(self, "_nivel_activo", False):
            return

        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = tiempo_actual - self._nivel_inicio

        if tiempo_transcurrido >= self._nivel_duracion:
            self._nivel_activo = False
            return

        # Fade out último segundo
        alpha = 255
        tiempo_restante = self._nivel_duracion - tiempo_transcurrido
        if tiempo_restante < 1000:
            alpha = int(255 * (tiempo_restante / 1000))

        texto = self._nivel_font.render(self._nivel_nombre, True, (255, 255, 255))
        texto.set_alpha(alpha)

        # 👇 Centro real de la pantalla
        rect = texto.get_rect(center=(
            pantalla.get_width() // 2,
            pantalla.get_height() // 2
        ))

        pantalla.blit(texto, rect)