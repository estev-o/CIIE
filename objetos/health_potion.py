import pygame


class HealthPotion(pygame.sprite.Sprite):
    def __init__(self, x, y, heal_amount=25, sprite_path="assets/objects/potion.png", pickup_delay=0.25):
        super().__init__()
        self.heal_amount = heal_amount
        self.pickup_delay = pickup_delay
        self.time_alive = 0.0
        self.image = pygame.image.load(sprite_path).convert_alpha()
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self, player, dt=0.0):
        self.time_alive += dt
        if self.time_alive < self.pickup_delay:
            return
        if self.rect.colliderect(player.body_hitbox):
            player.heal(self.heal_amount)
            self.kill()
