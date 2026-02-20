from personajes.constants import BLUE
import pygame
from personajes.ataques.attack import Attack


class Azulejo(Attack):
    def __init__(self, game):
        image = pygame.image.load("assets/ataques/azulejo.png").convert_alpha()

        super().__init__(
            damage = 10,
            game = game,
            image = image,
            speed = 500
        )

        self.direction_x = 0
        self.direction_y = 0
        self.angle = 0
        self.original_image = self.image

    def init(self, x, y, direction):
        self.activate()
        self.direction_x = direction.x
        self.direction_y = direction.y
        self.angle = 0
    
        self.rect.center = (x, y)

    def update(self, dt, tiles=None):
        screen_x, screen_y = self.game.screen.get_size()
        self.rect.x += self.direction_x * self.speed * dt
        self.rect.y += self.direction_y * self.speed * dt
        
        self.angle = (self.angle + 360 * 3 * dt) % 360

        self.check_collisions()
        
        if tiles:
            for tile in tiles:
                if self.rect.colliderect(tile.hitbox):
                    self.deactivate()
                    return
        if not -screen_x < self.rect.x < screen_x:
            self.deactivate()
        if not -screen_y < self.rect.y < screen_y:
            self.deactivate()

    def render(self, screen):
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rect)

    def load_sprites(self):
        pass