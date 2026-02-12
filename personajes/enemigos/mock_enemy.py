from abc import ABC

from personajes.enemigos.enemy import Enemy

class Mock_enemy(Enemy, ABC):
    def __init__(self, game):
        super().__init__(game=game,
                        max_live = 40,
                            # la posición la cambiamos porque el spawn cambia según el estado del nivel
                        x = 0,
                        y = 0,
                        width = 64,
                        height = 64,
                        speed = 50,
                        scale = 1.75,
                        vision_range= 100,
                        anim_fps = 15,
                        hitbox_offset_x = 37.5,
                        hitbox_offset_y = 37.5,
                        asset_file = "assets/Blub/PNG/Slime1/Walk/Slime1_Walk_full.png",
                         )