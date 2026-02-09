from personajes.ataques.cooldowns import cooldowns
from pygame.time import get_ticks

class AttackLauncher():
    def __init__(self, attack):
        self.attack = attack
        self.cooldown = cooldowns[attack]
        self._last_use = 0

    @property
    def is_ready(self):
        now = get_ticks()
        return now - self._last_use >= self.cooldown
    
    def get_attack(self, *args):
        if self.is_ready:
            self._last_use = get_ticks()
            return self.attack(*args)