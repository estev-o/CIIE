from personajes.ataques.cooldowns import cooldowns
from pygame.time import get_ticks

class AttackPool():
    MAX = 1000

    def __init__(self, attack, *args, **kwargs):
        self.attacks = [attack(*args, **kwargs) for _ in range(self.MAX)]
        self.cooldown = cooldowns[attack]
        self.last_use = 0

    def is_ready(self):
        now = get_ticks()
        return now - self.last_use >= self.cooldown
    
    def create(self, *args, **kwargs):
        for attack in self.attacks:
            if not attack.in_use():
                self.last_use = get_ticks()
                attack.init(*args, **kwargs)
                return attack
    
    def update(self, dt):
        for attack in self.attacks:
            if attack.in_use():
                attack.update(dt)

    def render(self, screen):
        for attack in self.attacks:
            if attack.in_use():
                attack.render(screen)