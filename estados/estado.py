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
