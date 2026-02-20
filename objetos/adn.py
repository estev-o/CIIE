import pygame


class ADN(pygame.sprite.Sprite):
    def __init__(self, x, y, amount=1, sprite_path="assets/UI/ADN/ADN.png", pickup_delay=0.25):
        super().__init__()
        self.amount = int(amount)
        self.pickup_delay = pickup_delay
        self.time_alive = 0.0
        self.image = pygame.image.load(sprite_path).convert_alpha()
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self, player, dt=0.0):
        self.time_alive += dt
        if self.time_alive < self.pickup_delay:
            return
        if self.rect.colliderect(player.body_hitbox):
            player.game.add_adn(self.amount)
            self.kill()
