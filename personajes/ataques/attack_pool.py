from personajes.ataques.cooldowns import cooldowns
from pygame.time import get_ticks

class AttackPool():
    MAX = 1000

    def __init__(self, attack, *args, **kwargs):
        self.attacks = [attack(*args, **kwargs) for _ in range(self.MAX)]
        self.base_cooldown = cooldowns[attack]
        self.cooldown_multiplier = 1.0
        self.last_use = 0

    @property
    def cooldown(self):
        return max(1, int(self.base_cooldown * self.cooldown_multiplier))

    def set_cooldown_multiplier(self, multiplier):
        self.cooldown_multiplier = max(0.01, float(multiplier))
        return self.cooldown

    def is_ready(self):
        now = get_ticks()
        return now - self.last_use >= self.cooldown
    
    def create(self, *args, **kwargs):
        for attack in self.attacks:
            if not attack.in_use():
                self.last_use = get_ticks()
                attack.init(*args, **kwargs)
                return attack
    
    def update(self, dt, tiles=None):
        for attack in self.attacks:
            if attack.in_use():
                attack.update(dt, tiles)

    def render(self, screen):
        for attack in self.attacks:
            if attack.in_use():
                attack.render(screen)
