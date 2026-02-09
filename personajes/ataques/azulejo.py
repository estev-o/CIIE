from personajes.ataques.attack import Attack
from personajes.constants import BLUE
import pygame


class Azulejo(Attack):
    def __init__(self, game, x, y, direction):
        super().__init__(
            damage = 10,
            game = game,
            x = x,
            y = y,
            width = 16,
            height = 16,
            scale = 2,
            speed = 500,
            anim_fps = 10,
            hitbox_offset_x= 0,
            hitbox_offset_y= 0
        )
        self.image = pygame.Surface((self.frame_w, self.frame_h))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos_x, self.pos_y)

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
        
        self.game.screen.blit(self.image, (self.pos_x, self.pos_y))

    def update(self, dt, acciones):
        screen_x, screen_y = self.game.screen.get_size()
        self.pos_x += self.direction_x * self.speed * dt
        self.pos_y += self.direction_y * self.speed * dt

        if not -screen_x < self.pos_x < screen_x:
            self.game.state_stack[-1].attacks.remove(self)
        if not -screen_y < self.pos_y < screen_y:
            self.game.state_stack[-1].attacks.remove(self)

    def render(self, screen):
        screen.blit(self._curr_image, (int(self.pos_x), int(self.pos_y)))


    def load_sprites(self):
        pass