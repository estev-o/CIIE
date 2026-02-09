from abc import abstractmethod
from personajes.character import Character

class Attack(Character):
    def __init__(self, damage, game, x, y, width, height, scale, speed, anim_fps):
        super().__init__(game, x, y, width, height, scale, speed, anim_fps)
        self.damage = damage
    
    def die(self):
        pass
    