from personajes.constants import BLUE
import pygame
from personajes.ataques.attack import Attack


class Azulejo(Attack):
    def __init__(self, game):
        image = pygame.Surface((16, 16))
        image.fill(BLUE)

        super().__init__(
            damage = 10,
            game = game,
            image = image,
            speed = 500
        )

        self.direction_x = 0
        self.direction_y = 0

    def init(self, x, y, direction):
        self.activate()
        self.direction_x = 0
        self.direction_y = 0

        if direction == "right":
            self.direction_x = 1
        elif direction == "left":
            self.direction_x = -1
        elif direction == "down":
            self.direction_y = 1
        elif direction == "up":
            self.direction_y = -1
        else:
            raise ValueError("Azulejo: invalid direction ", direction)
    
        self.rect.x = x
        self.rect.y = y

    def update(self, dt):
        screen_x, screen_y = self.game.screen.get_size()
        self.rect.x += self.direction_x * self.speed * dt
        self.rect.y += self.direction_y * self.speed * dt

        if not -screen_x < self.rect.x < screen_x:
            self.deactivate()
        if not -screen_y < self.rect.y < screen_y:
            self.deactivate()

    def load_sprites(self):
        pass