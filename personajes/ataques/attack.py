from abc import abstractmethod
from personajes.character import Character

class Attack(Character):
    def __init__(self, damage, game, x, y, width, height, scale, speed, anim_fps, hitbox_offset_x, hitbox_offset_y):
        super().__init__(game=game, x=x, y=y, width=width, height=height, scale=scale, speed=speed, anim_fps=anim_fps, hitbox_offset_x=hitbox_offset_x, hitbox_offset_y=hitbox_offset_y)
        self.damage = damage
    
    def die(self):
        pass
    