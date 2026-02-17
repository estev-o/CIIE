import pygame

class Attack(pygame.sprite.Sprite):
    def __init__(self, game, image, damage, speed, rect=None):
        super().__init__()
        self.damage = damage
        self.game = game
        self.speed = speed
        self.image = image
        self.active = False

        if rect:
            self.rect = rect
        else:
            self.rect = self.image.get_rect()

    def init(self, *args, **kwargs):
        raise NotImplementedError
    
    def check_collisions(self):
        hits = pygame.sprite.spritecollide(self, self.game.actual_state.enemies, False)
        # Avoid circular import by checking class name
        hits = [hit for hit in hits if hit.__class__.__name__ != "Chest"]

        if len(hits) > 0:
            for enemy in hits:
                enemy.apply_damage(self.damage)
            
            self.deactivate()

    def update(self, dt, tiles=None):
        raise NotImplementedError
    
    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def in_use(self):
        return self.active
    
    def render(self, screen):
        screen.blit(self.image, self.rect)
